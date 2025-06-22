import json
import logging
import asyncio
import re
from typing import Tuple, Optional, Dict, Any
import aiohttp
from huggingface_hub import HfApi, ModelCard, hf_hub_download
from huggingface_hub import hf_api
from transformers import AutoConfig, AutoTokenizer
from app.config.base import HF_TOKEN, API
from app.utils.logging import LogFormatter


logger = logging.getLogger(__name__)

class ModelValidator:
    def __init__(self):
        self.token = HF_TOKEN
        self.api = HfApi(token=self.token)
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
    async def check_model_card(self, model_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Check if model has a valid model card"""
        try:
            logger.info(LogFormatter.info(f"Checking model card for {model_id}"))
            
            # Get model card content using ModelCard.load
            try:
                model_card = await asyncio.to_thread(
                    ModelCard.load,
                    model_id
                )
                logger.info(LogFormatter.success("Model card found"))
            except Exception as e:
                error_msg = "Please add a model card to your model to explain how you trained/fine-tuned it."
                logger.error(LogFormatter.error(error_msg, e))
                return False, error_msg, None
            
            # Check license in model card data
            if model_card.data.license is None and not ("license_name" in model_card.data and "license_link" in model_card.data):
                error_msg = "License not found. Please add a license to your model card using the `license` metadata or a `license_name`/`license_link` pair."
                logger.warning(LogFormatter.warning(error_msg))
                return False, error_msg, None

            # Enforce card content length
            if len(model_card.text) < 200:
                error_msg = "Please add a description to your model card, it is too short."
                logger.warning(LogFormatter.warning(error_msg))
                return False, error_msg, None
            
            logger.info(LogFormatter.success("Model card validation passed"))
            return True, "", model_card
            
        except Exception as e:
            error_msg = "Failed to validate model card"
            logger.error(LogFormatter.error(error_msg, e))
            return False, str(e), None
            
    async def get_safetensors_metadata(self, model_id: str, is_adapter: bool = False, revision: str = "main")  -> Optional[Dict]:
        """Get metadata from a safetensors file"""
        try:
            if is_adapter:
                metadata = await asyncio.to_thread(
                    hf_api.parse_safetensors_file_metadata,
                    model_id,
                    "adapter_model.safetensors",
                    token=self.token,
                    revision=revision,
                )
            else:
                metadata = await asyncio.to_thread(
                    hf_api.get_safetensors_metadata,
                    repo_id=model_id,
                    token=self.token,
                    revision=revision,
                )
            return metadata

        except Exception as e:
            logger.error(f"Failed to get safetensors metadata: {str(e)}")
            return None

    async def get_model_size(
        self,
        model_info: Any,
        precision: str,
        base_model: str,
        revision: str
    ) -> Tuple[Optional[float], Optional[str]]:
        """Get model size in billions of parameters"""
        try:
            logger.info(LogFormatter.info(f"Checking model size for {model_info.modelId}"))

            # Check if model is adapter
            is_adapter = any(s.rfilename == "adapter_config.json" for s in model_info.siblings if hasattr(s, 'rfilename'))

            # Try to get size from safetensors first
            model_size = None

            if is_adapter and base_model:
                # For adapters, we need both adapter and base model sizes
                adapter_meta = await self.get_safetensors_metadata(model_info.id, is_adapter=True, revision=revision)
                base_meta = await self.get_safetensors_metadata(base_model, revision="main")

                if adapter_meta and base_meta:
                    adapter_size = sum(adapter_meta.parameter_count.values())
                    base_size = sum(base_meta.parameter_count.values())
                    model_size = adapter_size + base_size
            else:
                # For regular models, just get the model size
                meta = await self.get_safetensors_metadata(model_info.id, revision=revision)
                if meta:
                    model_size = sum(meta.parameter_count.values()) # total params

            if model_size is None:
                # If model size could not be determined, return an error
                return None, "Model size could not be determined"

            # Adjust size for GPTQ models
            size_factor = 8 if (precision == "GPTQ" or "gptq" in model_info.id.lower()) else 1
            model_size = model_size / 1e9  # Convert to billions, assuming float16
            model_size = round(size_factor * model_size, 3)

            logger.info(LogFormatter.success(f"Model size: {model_size}B parameters"))
            return model_size, None

        except Exception as e:
            logger.error(LogFormatter.error(f"Error while determining model size: {e}"))
            return None, str(e)

            
    async def check_chat_template(
        self,
        model_id: str,
        revision: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if model has a valid chat template"""
        try:
            logger.info(LogFormatter.info(f"Checking chat template for {model_id}"))
            
            try:
                config_file = await asyncio.to_thread(
                    hf_hub_download,
                    repo_id=model_id,
                    filename="tokenizer_config.json",
                    revision=revision,
                    repo_type="model"
                )
                
                with open(config_file, 'r') as f:
                    tokenizer_config = json.load(f)
                
                if 'chat_template' not in tokenizer_config:
                    error_msg = f"The model {model_id} doesn't have a chat_template in its tokenizer_config.json. Please add a chat_template before submitting or submit without it."
                    logger.error(LogFormatter.error(error_msg))
                    return False, error_msg
                
                logger.info(LogFormatter.success("Valid chat template found"))
                return True, None
                
            except Exception as e:
                error_msg = f"Error checking chat_template: {str(e)}"
                logger.error(LogFormatter.error(error_msg))
                return False, error_msg
                    
        except Exception as e:
            error_msg = "Failed to check chat template"
            logger.error(LogFormatter.error(error_msg, e))
            return False, str(e)
            
    async def is_model_on_hub(
        self,
        model_name: str,
        revision: str,
        test_tokenizer: bool = False,
        trust_remote_code: bool = False
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Check if model exists and is properly configured on the Hub"""
        try:
            config = await asyncio.to_thread(
                AutoConfig.from_pretrained,
                model_name,
                revision=revision,
                trust_remote_code=trust_remote_code,
                token=self.token,
                force_download=True
            )
            
            if test_tokenizer:
                try:
                    await asyncio.to_thread(
                        AutoTokenizer.from_pretrained,
                        model_name,
                        revision=revision,
                        trust_remote_code=trust_remote_code,
                        token=self.token
                    )
                except ValueError as e:
                    return False, f"The tokenizer is not available in an official Transformers release: {e}", None
                except Exception:
                    return False, "The tokenizer cannot be loaded. Ensure the tokenizer class is part of a stable Transformers release and correctly configured.", None
            
            return True, None, config
            
        except ValueError:
            return False, "The model requires `trust_remote_code=True` to launch, and for safety reasons, we don't accept such models automatically.", None
        except Exception as e:
            if "You are trying to access a gated repo." in str(e):
                return True, "The model is gated and requires special access permissions.", None
            return False, f"The model was not found or is misconfigured on the Hub. Error: {e.args[0]}", None
// Define the list of allowed models to display
export const ALLOWED_MODELS = [
  "GPT-4o",
  "o3-Mini",
  "Deepseek-V3",
  "meta-llama/Llama-4-Scout-17B-16E-Instruct",
  "meta-llama/Llama-3.1-70B-Instruct",
  "google/gemma-3-4b-it",
  "google/gemma-3-27b-it",
  "Qwen/Qwen2.5-32B-Instruct",
  "Qwen/Qwen2.5-Omni-7B",
  "TheFinAI/finma-7b-full",
  "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview",
  "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese",
  "TheFinAI/FinMA-ES-Bilingual",
  "TheFinAI/plutus-8B-instruct",
  "Qwen-VL-MAX",
  "LLaVA-1.6 Vicuna-13B",
  "Deepseek-VL-7B-Chat",
  "Whisper-V3",
  "Qwen2-Audio-7B",
  "Qwen2-Audio-7B-Instruct",
  "SALMONN-7B",
  "SALMONN-13B"
];

// Function to check if a model is in the allowed list
export const isModelAllowed = (modelName) => {
  return ALLOWED_MODELS.some(allowedModel => 
    modelName.toLowerCase().includes(allowedModel.toLowerCase())
  );
}; 
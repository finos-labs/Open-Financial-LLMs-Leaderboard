export const MODEL_TYPE_ORDER = [
  'pretrained',
  'continuously pretrained',
  'fine-tuned',
  'chat',
  'merge',
  'multimodal'
];

export const MODEL_TYPES = {
  'pretrained': {
    icon: '🟢',
    label: 'Pretrained',
    description: 'Base models trained on raw text data using self-supervised learning objectives',
    order: 0
  },
  'continuously pretrained': {
    icon: '🟩',
    label: 'Continuously Pretrained',
    description: 'Base models with extended pretraining on additional data while maintaining original architecture',
    order: 1
  },
  'fine-tuned': {
    icon: '🔶',
    label: 'Fine-tuned',
    description: 'Models specialized through task-specific training on curated datasets',
    order: 2
  },
  'chat': {
    icon: '💬',
    label: 'Chat',
    description: 'Models optimized for conversation using various techniques: RLHF, DPO, IFT, SFT',
    order: 3
  },
  'merge': {
    icon: '🤝',
    label: 'Merge',
    description: 'Models created by combining weights from multiple models',
    order: 4
  },
  'multimodal': {
    icon: '🌸',
    label: 'Multimodal',
    description: 'Models capable of processing multiple types of input',
    order: 5
  }
};

export const getModelTypeIcon = (type) => {
  const cleanType = type.toLowerCase().trim();
  const matchedType = Object.entries(MODEL_TYPES).find(([key]) => 
    cleanType.includes(key)
  );
  return matchedType ? matchedType[1].icon : '❓';
};

export const getModelTypeLabel = (type) => {
  const cleanType = type.toLowerCase().trim();
  const matchedType = Object.entries(MODEL_TYPES).find(([key]) => 
    cleanType.includes(key)
  );
  return matchedType ? matchedType[1].label : type;
};

export const getModelTypeDescription = (type) => {
  const cleanType = type.toLowerCase().trim();
  const matchedType = Object.entries(MODEL_TYPES).find(([key]) => 
    cleanType.includes(key)
  );
  return matchedType ? matchedType[1].description : 'Unknown model type';
};

export const getModelTypeOrder = (type) => {
  const cleanType = type.toLowerCase().trim();
  const matchedType = Object.entries(MODEL_TYPES).find(([key]) => 
    cleanType.includes(key)
  );
  return matchedType ? matchedType[1].order : Infinity;
}; 
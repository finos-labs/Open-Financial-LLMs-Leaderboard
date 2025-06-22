import { useMemo } from "react";
import {
  looksLikeRegex,
  parseSearchQuery,
  getValueByPath,
} from "../utils/searchUtils";
import { ALLOWED_MODELS, isModelAllowed } from "../constants/allowedModels";

// 硬编码数据集
const HARDCODED_SCORES = {
  vision: {
    "GPT-4o": 55.54, "o3-Mini": 0.00, "Deepseek-V3": 0.00, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 16.27,
    "meta-llama/Llama-3.1-70B-Instruct": 0.00, "google/gemma-3-4b-it": 14.97, "google/gemma-3-27b-it": 25.57,
    "Qwen/Qwen2.5-32B-Instruct": 0.00, "Qwen/Qwen2.5-Omni-7B": 24.97, "TheFinAI/finma-7b-full": 0.00,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 0.00, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 0.00,
    "TheFinAI/FinMA-ES-Bilingual": 0.00, "TheFinAI/plutus-8B-instruct": 0.00, "Qwen-VL-MAX": 18.47,
    "LLaVA-1.6 Vicuna-13B": 19.77, "Deepseek-VL-7B-Chat": 19.10, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  audio: {
    "GPT-4o": 55.56, "o3-Mini": 0.00, "Deepseek-V3": 0.00, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 0.00,
    "meta-llama/Llama-3.1-70B-Instruct": 0.00, "google/gemma-3-4b-it": 0.00, "google/gemma-3-27b-it": 0.00,
    "Qwen/Qwen2.5-32B-Instruct": 0.00, "Qwen/Qwen2.5-Omni-7B": 48.22, "TheFinAI/finma-7b-full": 0.00,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 0.00, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 0.00,
    "TheFinAI/FinMA-ES-Bilingual": 0.00, "TheFinAI/plutus-8B-instruct": 0.00, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 51.58, "Qwen2-Audio-7B": 48.02,
    "Qwen2-Audio-7B-Instruct": 50.06, "SALMONN-7B": 24.24, "SALMONN-13B": 24.59
  },
  english: {
    "GPT-4o": 42.18, "o3-Mini": 20.20, "Deepseek-V3": 18.04, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 24.16,
    "meta-llama/Llama-3.1-70B-Instruct": 38.71, "google/gemma-3-4b-it": 16.13, "google/gemma-3-27b-it": 17.19,
    "Qwen/Qwen2.5-32B-Instruct": 32.01, "Qwen/Qwen2.5-Omni-7B": 24.99, "TheFinAI/finma-7b-full": 28.89,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 29.39, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 26.38,
    "TheFinAI/FinMA-ES-Bilingual": 31.72, "TheFinAI/plutus-8B-instruct": 27.82, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  chinese: {
    "GPT-4o": 60.34, "o3-Mini": 0.00, "Deepseek-V3": 60.94, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 64.51,
    "meta-llama/Llama-3.1-70B-Instruct": 56.74, "google/gemma-3-4b-it": 26.23, "google/gemma-3-27b-it": 26.24,
    "Qwen/Qwen2.5-32B-Instruct": 56.62, "Qwen/Qwen2.5-Omni-7B": 53.09, "TheFinAI/finma-7b-full": 24.42,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 23.04, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 13.18,
    "TheFinAI/FinMA-ES-Bilingual": 21.50, "TheFinAI/plutus-8B-instruct": 31.04, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  japanese: {
    "GPT-4o": 0.00, "o3-Mini": 0.00, "Deepseek-V3": 0.00, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 48.43,
    "meta-llama/Llama-3.1-70B-Instruct": 32.17, "google/gemma-3-4b-it": 8.98, "google/gemma-3-27b-it": 23.96,
    "Qwen/Qwen2.5-32B-Instruct": 4.54, "Qwen/Qwen2.5-Omni-7B": 44.35, "TheFinAI/finma-7b-full": 46.94,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 47.59, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 23.96,
    "TheFinAI/FinMA-ES-Bilingual": 57.36, "TheFinAI/plutus-8B-instruct": 34.62, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  spanish: {
    "GPT-4o": 29.80, "o3-Mini": 4.53, "Deepseek-V3": 25.49, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 47.90,
    "meta-llama/Llama-3.1-70B-Instruct": 37.84, "google/gemma-3-4b-it": 27.66, "google/gemma-3-27b-it": 27.77,
    "Qwen/Qwen2.5-32B-Instruct": 37.47, "Qwen/Qwen2.5-Omni-7B": 39.16, "TheFinAI/finma-7b-full": 27.04,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 42.86, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 28.01,
    "TheFinAI/FinMA-ES-Bilingual": 38.69, "TheFinAI/plutus-8B-instruct": 40.16, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  greek: {
    "GPT-4o": 43.04, "o3-Mini": 9.48, "Deepseek-V3": 39.07, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 48.95,
    "meta-llama/Llama-3.1-70B-Instruct": 43.60, "google/gemma-3-4b-it": 15.45, "google/gemma-3-27b-it": 15.44,
    "Qwen/Qwen2.5-32B-Instruct": 44.32, "Qwen/Qwen2.5-Omni-7B": 23.45, "TheFinAI/finma-7b-full": 17.93,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 29.49, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 20.91,
    "TheFinAI/FinMA-ES-Bilingual": 15.47, "TheFinAI/plutus-8B-instruct": 60.19, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  bilingual: {
    "GPT-4o": 92.29, "o3-Mini": 90.13, "Deepseek-V3": 86.26, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 89.17,
    "meta-llama/Llama-3.1-70B-Instruct": 92.13, "google/gemma-3-4b-it": 35.92, "google/gemma-3-27b-it": 35.92,
    "Qwen/Qwen2.5-32B-Instruct": 92.29, "Qwen/Qwen2.5-Omni-7B": 91.80, "TheFinAI/finma-7b-full": 69.24,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 91.60, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 71.81,
    "TheFinAI/FinMA-ES-Bilingual": 66.57, "TheFinAI/plutus-8B-instruct": 91.59, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  },
  multilingual: {
    "GPT-4o": 6.53, "o3-Mini": 7.80, "Deepseek-V3": 36.99, "meta-llama/Llama-4-Scout-17B-16E-Instruct": 13.52,
    "meta-llama/Llama-3.1-70B-Instruct": 21.97, "google/gemma-3-4b-it": 0.00, "google/gemma-3-27b-it": 0.00,
    "Qwen/Qwen2.5-32B-Instruct": 18.48, "Qwen/Qwen2.5-Omni-7B": 16.29, "TheFinAI/finma-7b-full": 3.10,
    "Duxiaoman-DI/Llama3.1-XuanYuan-FinX1-Preview": 1.76, "cyberagent/DeepSeek-R1-Distill-Qwen-32B-Japanese": 10.25,
    "TheFinAI/FinMA-ES-Bilingual": 0.35, "TheFinAI/plutus-8B-instruct": 7.24, "Qwen-VL-MAX": 0.00,
    "LLaVA-1.6 Vicuna-13B": 0.00, "Deepseek-VL-7B-Chat": 0.00, "Whisper-V3": 0.00, "Qwen2-Audio-7B": 0.00,
    "Qwen2-Audio-7B-Instruct": 0.00, "SALMONN-7B": 0.00, "SALMONN-13B": 0.00
  }
};

// Calculate min/max averages
export const useAverageRange = (data) => {
  return useMemo(() => {
    const averages = data.map((item) => item.model.average_score);
    return {
      minAverage: Math.min(...averages),
      maxAverage: Math.max(...averages),
    };
  }, [data]);
};

// Generate colors for scores
export const useColorGenerator = (minAverage, maxAverage) => {
  return useMemo(() => {
    const colorCache = new Map();
    return (value) => {
      const cached = colorCache.get(value);
      if (cached) return cached;

      const normalizedValue = (value - minAverage) / (maxAverage - minAverage);
      const red = Math.round(255 * (1 - normalizedValue) * 1);
      const green = Math.round(255 * normalizedValue) * 1;
      // const color = `rgba(${red}, ${green}, 0, 1)`;
      const color = `rgba(${red}, 0, ${green}, 1)`;
      colorCache.set(value, color);
      return color;
    };
  }, [minAverage, maxAverage]);
};

// Process data with boolean standardization
export const useProcessedData = (data, averageMode, visibleColumns) => {
  return useMemo(() => {
    // 直接使用硬编码数据创建模型列表
    const modelList = [];
    
    // 从HARDCODED_SCORES中获取所有模型名称
    const modelNames = new Set();
    Object.values(HARDCODED_SCORES).forEach(categoryData => {
      Object.entries(categoryData).forEach(([modelName, score]) => {
        // 添加所有模型，不管分数是否为0
        modelNames.add(modelName);
      });
    });
    
    // 为每个模型创建条目
    Array.from(modelNames).forEach((modelName, index) => {
      // 创建硬编码评估数据
      const hardcodedEvaluations = {
        vision_average: getHardcodedScore(modelName, 'vision'),
        audio_average: getHardcodedScore(modelName, 'audio'),
        english_average: getHardcodedScore(modelName, 'english'),
        chinese_average: getHardcodedScore(modelName, 'chinese'),
        japanese_average: getHardcodedScore(modelName, 'japanese'),
        spanish_average: getHardcodedScore(modelName, 'spanish'),
        greek_average: getHardcodedScore(modelName, 'greek'),
        bilingual_average: getHardcodedScore(modelName, 'bilingual'),
        multilingual_average: getHardcodedScore(modelName, 'multilingual')
      };
      
      // 计算总平均分（包含分数为0的类别）
      const scores = Object.values(hardcodedEvaluations).filter(score => score !== null);
      const averageScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
      
      // 创建模型数据
      modelList.push({
        id: `model-${index}`,
        model: {
          name: modelName,
          average_score: averageScore,
          type: "chat", // 统一设为chat类型
        },
        evaluations: hardcodedEvaluations,
        features: {
          is_moe: false,
          is_flagged: false,
          is_highlighted_by_maintainer: false,
          is_merged: false,
          is_not_available_on_hub: false,
        },
        metadata: {
          submission_date: new Date().toISOString(),
        },
        isMissing: false,
      });
    });

    // 根据平均分排序
    modelList.sort((a, b) => {
      if (a.model.average_score === null && b.model.average_score === null)
        return 0;
      if (a.model.average_score === null) return 1;
      if (b.model.average_score === null) return -1;
      return b.model.average_score - a.model.average_score;
    });

    // 添加排名
    return modelList.map((item, index) => ({
      ...item,
      static_rank: index + 1,
    }));
  }, [data, averageMode, visibleColumns]);
};

// 辅助函数：从硬编码数据中获取分数
function getHardcodedScore(modelName, category) {
  if (!HARDCODED_SCORES[category]) return null;
  
  // 尝试精确匹配
  if (HARDCODED_SCORES[category][modelName] !== undefined) {
    return HARDCODED_SCORES[category][modelName];
  }
  
  // 尝试部分匹配
  for (const key in HARDCODED_SCORES[category]) {
    if (modelName.includes(key) || key.includes(modelName)) {
      return HARDCODED_SCORES[category][key];
    }
  }
  
  return null;
}

// Common filtering logic
export const useFilteredData = (
  processedData,
  selectedPrecisions,
  selectedTypes,
  paramsRange,
  searchValue,
  selectedBooleanFilters,
  rankingMode,
  pinnedModels = [],
  isOfficialProviderActive = false
) => {
  return useMemo(() => {
    // 由于使用的是硬编码数据，这里直接返回所有数据而不进行过滤
    return processedData.map((item, index) => ({
          ...item,
      dynamic_rank: index + 1,
      rank: rankingMode === "static" ? item.static_rank : index + 1,
          isPinned: pinnedModels.includes(item.id),
    }));
  }, [
    processedData,
    rankingMode,
    pinnedModels,
  ]);
};

// Column visibility management
export const useColumnVisibility = (visibleColumns = []) => {
  // Create secure visibility object
  const columnVisibility = useMemo(() => {
    // Check visible columns
    const safeVisibleColumns = Array.isArray(visibleColumns)
      ? visibleColumns
      : [];

    const visibility = {};
    try {
      safeVisibleColumns.forEach((columnKey) => {
        if (typeof columnKey === "string") {
          visibility[columnKey] = true;
        }
      });
    } catch (error) {
      console.warn("Error in useColumnVisibility:", error);
    }
    return visibility;
  }, [visibleColumns]);

  return columnVisibility;
};

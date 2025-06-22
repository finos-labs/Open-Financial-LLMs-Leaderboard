export const QUICK_FILTER_PRESETS = [
  {
    id: 'edge_device',
    label: 'For Edge Devices',
    shortDescription: 'Tiny models: Up to 3B parameters',
    description: 'Lightweight models optimized for edge devices with limited resources. Ideal for mobile deployment or edge computing environments.',
    filters: {
      paramsRange: [0, 3],
      selectedBooleanFilters: ['is_for_edge_devices']
    }
  },
  {
    id: 'small_models',
    label: 'For Consumers',
    shortDescription: 'Smol-LMs: 3-7B parameters',
    description: 'Lightweight models optimized for consumer hardware with up to one GPU. Ideal for private consumer hardware.',
    filters: {
      paramsRange: [3, 7],
      selectedBooleanFilters: ['is_for_edge_devices']
    }
  },
  {
    id: 'medium_models',
    label: 'Mid-range',
    shortDescription: 'Medium-sized models: 7B-65B parameters',
    description: 'Overall balance between performance and required resources.',
    filters: {
      paramsRange: [7, 65],
      selectedBooleanFilters: []
    }
  },
  {
    id: 'large_models',
    label: 'For the GPU-rich',
    shortDescription: 'Large models: 65B+ parameters',
    description: 'Large-scale models offering (in theory) the best performance but requiring significant resources. Require adapted infrastructure.',
    filters: {
      paramsRange: [65, 141],
      selectedBooleanFilters: []
    }
  },
  {
    id: 'official_providers',
    label: 'Only Official Providers',
    shortDescription: 'Officially provided models',
    description: 'Models that are officially provided and maintained by official creators or organizations.',
    filters: {
      selectedBooleanFilters: ['is_highlighted_by_maintainer']
    }
  }
]; 
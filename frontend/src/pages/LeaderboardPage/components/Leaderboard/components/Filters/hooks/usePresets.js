import { useCallback } from "react";
import { QUICK_FILTER_PRESETS } from "../../../constants/quickFilters";
import { TABLE_DEFAULTS } from "../../../constants/defaults";

const DEFAULT_FILTERS = {
  searchValue: "",
  selectedPrecisions: TABLE_DEFAULTS.SEARCH.PRECISIONS,
  selectedTypes: TABLE_DEFAULTS.SEARCH.TYPES,
  paramsRange: TABLE_DEFAULTS.SEARCH.PARAMS_RANGE,
  selectedBooleanFilters: [],
};

export const usePresets = (searchFilters) => {
  const handlePresetChange = useCallback(
    (preset) => {
      if (!searchFilters?.batchUpdateState) return;

      if (preset === null) {
        // Reset with default values
        searchFilters.batchUpdateState(DEFAULT_FILTERS, true);
        return;
      }

      // Apply preset with default values as base
      const updates = {
        ...DEFAULT_FILTERS,
        ...preset.filters,
      };

      // Apply all changes at once
      searchFilters.batchUpdateState(updates, true);
    },
    [searchFilters]
  );

  const resetPreset = useCallback(() => {
    handlePresetChange(null);
  }, [handlePresetChange]);

  const getActivePreset = useCallback(() => {
    // If searchFilters is not initialized yet, return null
    if (!searchFilters) return null;

    // Dynamic detection of preset matching current filters
    const currentParamsRange = Array.isArray(searchFilters.paramsRange)
      ? searchFilters.paramsRange
      : DEFAULT_FILTERS.paramsRange;
    const currentBooleanFilters = Array.isArray(
      searchFilters.selectedBooleanFilters
    )
      ? searchFilters.selectedBooleanFilters
      : DEFAULT_FILTERS.selectedBooleanFilters;
    const currentPrecisions = Array.isArray(searchFilters.selectedPrecisions)
      ? searchFilters.selectedPrecisions
      : DEFAULT_FILTERS.selectedPrecisions;
    const currentTypes = Array.isArray(searchFilters.selectedTypes)
      ? searchFilters.selectedTypes
      : DEFAULT_FILTERS.selectedTypes;

    return (
      QUICK_FILTER_PRESETS.find((preset) => {
        const presetParamsRange = Array.isArray(preset.filters.paramsRange)
          ? preset.filters.paramsRange
          : DEFAULT_FILTERS.paramsRange;
        const presetBooleanFilters = Array.isArray(
          preset.filters.selectedBooleanFilters
        )
          ? preset.filters.selectedBooleanFilters
          : DEFAULT_FILTERS.selectedBooleanFilters;

        const paramsMatch =
          JSON.stringify(presetParamsRange) ===
          JSON.stringify(currentParamsRange);
        const booleanFiltersMatch =
          JSON.stringify(presetBooleanFilters.sort()) ===
          JSON.stringify(currentBooleanFilters.sort());

        // Check if other filters match default values
        const precisionMatch =
          JSON.stringify(currentPrecisions.sort()) ===
          JSON.stringify(DEFAULT_FILTERS.selectedPrecisions.sort());
        const typesMatch =
          JSON.stringify(currentTypes.sort()) ===
          JSON.stringify(DEFAULT_FILTERS.selectedTypes.sort());

        return (
          paramsMatch && booleanFiltersMatch && precisionMatch && typesMatch
        );
      })?.id || null
    );
  }, [searchFilters]);

  return {
    activePreset: getActivePreset(),
    handlePresetChange,
    resetPreset,
  };
};

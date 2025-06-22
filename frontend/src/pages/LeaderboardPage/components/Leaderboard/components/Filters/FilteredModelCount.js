import React from "react";
import { Box, Typography, Skeleton } from "@mui/material";
import { useMemo } from "react";
import { useLeaderboard } from "../../context/LeaderboardContext";

const useModelCount = ({ totalCount, filteredCount, data, table, loading }) => {
  const { state } = useLeaderboard();
  const isOfficialProviderActive = state.filters.isOfficialProviderActive;
  const { officialOnly: officialOnlyCounts } = state.filterCounts;

  return useMemo(() => {
    if (loading) {
      return {
        displayCount: 0,
        currentFilteredCount: 0,
        totalPinnedCount: 0,
        filteredPinnedCount: 0,
        isOfficialProviderActive,
      };
    }
    const displayCount = isOfficialProviderActive
      ? officialOnlyCounts.maintainersHighlight
      : totalCount;

    // Calculate total number of pinned models
    const totalPinnedCount =
      data?.filter((model) => model.isPinned)?.length || 0;

    // Get current filter criteria
    const filterConfig = {
      selectedPrecisions: state.filters.precisions,
      selectedTypes: state.filters.types,
      paramsRange: state.filters.paramsRange,
      searchValue: state.filters.search,
      selectedBooleanFilters: state.filters.booleanFilters,
      isOfficialProviderActive: state.filters.isOfficialProviderActive,
    };

    // Check each pinned model if it would pass filters without its pinned status
    const filteredPinnedCount =
      data?.filter((model) => {
        if (!model.isPinned) return false;

        // Check each filter criteria

        // Filter by official providers
        if (filterConfig.isOfficialProviderActive) {
          if (
            !model.features?.is_highlighted_by_maintainer &&
            !model.metadata?.is_highlighted_by_maintainer
          ) {
            return false;
          }
        }

        // Filter by precision
        if (filterConfig.selectedPrecisions.length > 0) {
          if (
            !filterConfig.selectedPrecisions.includes(model.model.precision)
          ) {
            return false;
          }
        }

        // Filter by type
        if (filterConfig.selectedTypes.length > 0) {
          const modelType = model.model.type?.toLowerCase().trim();
          if (
            !filterConfig.selectedTypes.some((type) =>
              modelType?.includes(type)
            )
          ) {
            return false;
          }
        }

        // Filter by parameters
        const params = model.metadata.params_billions;
        if (
          params < filterConfig.paramsRange[0] ||
          params >= filterConfig.paramsRange[1]
        ) {
          return false;
        }

        // Filter by search
        if (filterConfig.searchValue) {
          const searchLower = filterConfig.searchValue.toLowerCase();
          const modelName = model.model.name.toLowerCase();
          if (!modelName.includes(searchLower)) {
            return false;
          }
        }

        // Filter by boolean flags
        if (filterConfig.selectedBooleanFilters.length > 0) {
          if (
            !filterConfig.selectedBooleanFilters.every((filter) => {
              const filterValue =
                typeof filter === "object" ? filter.value : filter;

              // Maintainer's Highlight keeps positive logic
              if (filterValue === "is_highlighted_by_maintainer") {
                return model.features[filterValue];
              }

              // For all other filters, invert the logic
              if (filterValue === "is_not_available_on_hub") {
                return model.features[filterValue];
              }

              return !model.features[filterValue];
            })
          ) {
            return false;
          }
        }

        // If we get here, the model passes all filters
        return true;
      })?.length || 0;

    return {
      displayCount,
      currentFilteredCount: filteredCount,
      totalPinnedCount,
      filteredPinnedCount,
      isOfficialProviderActive,
    };
  }, [
    loading,
    totalCount,
    filteredCount,
    data,
    state.filters,
    isOfficialProviderActive,
    officialOnlyCounts.maintainersHighlight,
  ]);
};

const CountTypography = ({
  value,
  color = "text.primary",
  loading = false,
  pinnedCount = 0,
  filteredPinnedCount = 0,
  showPinned = false,
}) => {
  if (loading) {
    return (
      <Skeleton
        variant="text"
        width={24}
        height={20}
        sx={{
          display: "inline-block",
          transform: "none",
          marginBottom: "-4px",
        }}
      />
    );
  }

  return (
    <Box sx={{ display: "flex", alignItems: "center" }}>
      <Typography
        variant="body2"
        sx={{
          fontWeight: 700,
          whiteSpace: "nowrap",
          color,
        }}
      >
        {value}
      </Typography>
      {showPinned && pinnedCount > 0 && (
        <Typography
          variant="body2"
          component="span"
          sx={{
            fontWeight: 700,
            whiteSpace: "nowrap",
            color: "text.secondary",
            ml: 0.5,
          }}
        >
          {`+${pinnedCount}`}
        </Typography>
      )}
    </Box>
  );
};

const FilteredModelCount = React.memo(
  ({
    totalCount = 0,
    filteredCount = 0,
    hasFilterChanges = false,
    loading = false,
    data = [],
    table = null,
  }) => {
    const {
      displayCount,
      currentFilteredCount,
      totalPinnedCount,
      filteredPinnedCount,
      isOfficialProviderActive,
    } = useModelCount({
      totalCount,
      filteredCount,
      data,
      table,
      loading,
    });

    const shouldHighlight =
      !loading && hasFilterChanges && currentFilteredCount !== displayCount;

    // Always show pinned models when they exist
    const pinnedToShow = totalPinnedCount;

    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
        <CountTypography
          value={currentFilteredCount - pinnedToShow}
          color={shouldHighlight ? "primary.main" : "text.primary"}
          loading={loading}
          pinnedCount={pinnedToShow}
          filteredPinnedCount={filteredPinnedCount}
          showPinned={pinnedToShow > 0}
        />
        <CountTypography value="/" loading={loading} />
        <CountTypography
          value={displayCount}
          color={isOfficialProviderActive ? "secondary.main" : "text.primary"}
          loading={loading}
        />
      </Box>
    );
  }
);

FilteredModelCount.displayName = "FilteredModelCount";

export default FilteredModelCount;

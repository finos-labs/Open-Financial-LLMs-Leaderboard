import React, { useMemo, useEffect, useCallback } from "react";
import { Box, Typography } from "@mui/material";
import { useSearchParams } from "react-router-dom";

import { TABLE_DEFAULTS } from "./constants/defaults";
import { useLeaderboard } from "./context/LeaderboardContext";
import { useLeaderboardProcessing } from "./hooks/useLeaderboardData";
import { useLeaderboardData } from "./hooks/useLeaderboardData";

import LeaderboardFilters from "./components/Filters/Filters";
import LeaderboardTable from "./components/Table/Table";
import SearchBar, { SearchBarSkeleton } from "./components/Filters/SearchBar";
import PerformanceMonitor from "./components/PerformanceMonitor";
import QuickFilters, {
  QuickFiltersSkeleton,
} from "./components/Filters/QuickFilters";

const FilterAccordion = ({ expanded, quickFilters, advancedFilters }) => {
  const advancedFiltersRef = React.useRef(null);
  const quickFiltersRef = React.useRef(null);
  const [height, setHeight] = React.useState("auto");
  const resizeTimeoutRef = React.useRef(null);

  const updateHeight = React.useCallback(() => {
    if (expanded && advancedFiltersRef.current) {
      setHeight(`${advancedFiltersRef.current.scrollHeight}px`);
    } else if (!expanded && quickFiltersRef.current) {
      setHeight(`${quickFiltersRef.current.scrollHeight}px`);
    }
  }, [expanded]);

  React.useEffect(() => {
    // Initial height calculation
    const timer = setTimeout(updateHeight, 100);

    // Resize handler with debounce
    const handleResize = () => {
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
      resizeTimeoutRef.current = setTimeout(updateHeight, 150);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      clearTimeout(timer);
      window.removeEventListener("resize", handleResize);
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, [updateHeight]);

  // Update height when expanded state changes
  React.useEffect(() => {
    updateHeight();
  }, [expanded, updateHeight]);

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        height,
        transition: "height 0.3s ease",
        mb: 0.5,
        overflow: "hidden",
      }}
    >
      <Box
        ref={quickFiltersRef}
        sx={{
          position: expanded ? "absolute" : "relative",
          top: 0,
          left: 0,
          right: 0,
          opacity: expanded ? 0 : 1,
          visibility: expanded ? "hidden" : "visible",
          transition: "opacity 0.3s ease",
          mb: 0,
        }}
      >
        {quickFilters}
      </Box>
      <Box
        ref={advancedFiltersRef}
        sx={{
          position: !expanded ? "absolute" : "relative",
          top: 0,
          left: 0,
          right: 0,
          opacity: expanded ? 1 : 0,
          visibility: !expanded ? "hidden" : "visible",
          transition: "opacity 0.3s ease",
          mt: 0,
        }}
      >
        {advancedFilters}
      </Box>
    </Box>
  );
};

const Leaderboard = () => {
  const { state, actions } = useLeaderboard();
  const [searchParams, setSearchParams] = useSearchParams();
  const {
    data,
    isLoading: dataLoading,
    error: dataError,
  } = useLeaderboardData();
  const {
    table,
    filteredData,
    error: processingError,
  } = useLeaderboardProcessing();

  // Memoize filtered data
  const memoizedFilteredData = useMemo(() => filteredData, [filteredData]);
  const memoizedTable = useMemo(() => table, [table]);

  // Memoize table options
  const hasTableOptionsChanges = useMemo(() => {
    return (
      state.display.rowSize !== TABLE_DEFAULTS.ROW_SIZE ||
      JSON.stringify(state.display.scoreDisplay) !==
        JSON.stringify(TABLE_DEFAULTS.SCORE_DISPLAY) ||
      state.display.averageMode !== TABLE_DEFAULTS.AVERAGE_MODE ||
      state.display.rankingMode !== TABLE_DEFAULTS.RANKING_MODE
    );
  }, [state.display]);

  const hasColumnFilterChanges = useMemo(() => {
    return (
      JSON.stringify([...state.display.visibleColumns].sort()) !==
      JSON.stringify([...TABLE_DEFAULTS.COLUMNS.DEFAULT_VISIBLE].sort())
    );
  }, [state.display.visibleColumns]);

  // Memoize callbacks
  const onToggleFilters = useCallback(() => {
    actions.toggleFiltersExpanded();
  }, [actions]);

  const onColumnVisibilityChange = useCallback(
    (newVisibility) => {
      actions.setDisplayOption(
        "visibleColumns",
        Object.keys(newVisibility).filter((key) => newVisibility[key])
      );
    },
    [actions]
  );

  const onRowSizeChange = useCallback(
    (size) => {
      actions.setDisplayOption("rowSize", size);
    },
    [actions]
  );

  const onScoreDisplayChange = useCallback(
    (display) => {
      actions.setDisplayOption("scoreDisplay", display);
    },
    [actions]
  );

  const onAverageModeChange = useCallback(
    (mode) => {
      actions.setDisplayOption("averageMode", mode);
    },
    [actions]
  );

  const onRankingModeChange = useCallback(
    (mode) => {
      actions.setDisplayOption("rankingMode", mode);
    },
    [actions]
  );

  const onPrecisionsChange = useCallback(
    (precisions) => {
      actions.setFilter("precisions", precisions);
    },
    [actions]
  );

  const onTypesChange = useCallback(
    (types) => {
      actions.setFilter("types", types);
    },
    [actions]
  );

  const onParamsRangeChange = useCallback(
    (range) => {
      actions.setFilter("paramsRange", range);
    },
    [actions]
  );

  const onBooleanFiltersChange = useCallback(
    (filters) => {
      actions.setFilter("booleanFilters", filters);
    },
    [actions]
  );

  const onReset = useCallback(() => {
    actions.resetFilters();
  }, [actions]);

  // Memoize loading states
  const loadingStates = useMemo(() => {
    const isInitialLoading = dataLoading || !data;
    const isProcessingData = !memoizedTable || !memoizedFilteredData;
    const isApplyingFilters = state.models.length > 0 && !memoizedFilteredData;
    const hasValidFilterCounts =
      state.countsReady &&
      state.filterCounts &&
      state.filterCounts.normal &&
      state.filterCounts.officialOnly;

    return {
      isInitialLoading,
      isProcessingData,
      isApplyingFilters,
      showSearchSkeleton: isInitialLoading || !hasValidFilterCounts,
      showFiltersSkeleton: isInitialLoading || !hasValidFilterCounts,
      showTableSkeleton:
        isInitialLoading ||
        isProcessingData ||
        isApplyingFilters ||
        !hasValidFilterCounts,
    };
  }, [
    dataLoading,
    data,
    memoizedTable,
    memoizedFilteredData,
    state.models.length,
    state.filterCounts,
    state.countsReady,
  ]);

  // Memoize child components
  const memoizedSearchBar = useMemo(
    () => (
      <SearchBar
        onToggleFilters={onToggleFilters}
        filtersOpen={state.filtersExpanded}
        loading={loadingStates.showTableSkeleton}
        data={memoizedFilteredData}
        table={table}
      />
    ),
    [
      onToggleFilters,
      state.filtersExpanded,
      loadingStates.showTableSkeleton,
      memoizedFilteredData,
      table,
    ]
  );

  const memoizedQuickFilters = useMemo(
    () => (
      <QuickFilters
        totalCount={state.models.length}
        filteredCount={memoizedFilteredData?.length || 0}
        data={memoizedFilteredData}
        table={memoizedTable}
      />
    ),
    [state.models.length, memoizedFilteredData, memoizedTable]
  );

  const memoizedLeaderboardFilters = useMemo(
    () => (
      <LeaderboardFilters
        data={memoizedFilteredData}
        loading={loadingStates.showFiltersSkeleton}
        selectedPrecisions={state.filters.precisions}
        onPrecisionsChange={onPrecisionsChange}
        selectedTypes={state.filters.types}
        onTypesChange={onTypesChange}
        paramsRange={state.filters.paramsRange}
        onParamsRangeChange={onParamsRangeChange}
        selectedBooleanFilters={state.filters.booleanFilters}
        onBooleanFiltersChange={onBooleanFiltersChange}
        onReset={onReset}
      />
    ),
    [
      memoizedFilteredData,
      loadingStates.showFiltersSkeleton,
      state.filters.precisions,
      state.filters.types,
      state.filters.paramsRange,
      state.filters.booleanFilters,
      onPrecisionsChange,
      onTypesChange,
      onParamsRangeChange,
      onBooleanFiltersChange,
      onReset,
    ]
  );

  // No need to memoize LeaderboardTable as it handles its own sorting state
  const tableComponent = (
    <LeaderboardTable
      table={table}
      loading={loadingStates.showTableSkeleton}
      onColumnVisibilityChange={onColumnVisibilityChange}
      hasTableOptionsChanges={hasTableOptionsChanges}
      hasColumnFilterChanges={hasColumnFilterChanges}
      rowSize={state.display.rowSize}
      onRowSizeChange={onRowSizeChange}
      scoreDisplay={state.display.scoreDisplay}
      onScoreDisplayChange={onScoreDisplayChange}
      averageMode={state.display.averageMode}
      onAverageModeChange={onAverageModeChange}
      rankingMode={state.display.rankingMode}
      onRankingModeChange={onRankingModeChange}
      searchParams={searchParams}
      setSearchParams={setSearchParams}
      pinnedModels={state.pinnedModels}
    />
  );

  // Update context with loaded data
  useEffect(() => {
    if (data) {
      actions.setModels(data);
    }
  }, [data, actions]);

  // Log to understand loading state
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("Loading state:", {
        dataLoading,
        hasData: !!data,
        hasTable: !!table,
        hasFilteredData: !!filteredData,
        filteredDataLength: filteredData?.length,
        stateModelsLength: state.models.length,
        hasFilters: Object.keys(state.filters).some((key) => {
          if (Array.isArray(state.filters[key])) {
            return state.filters[key].length > 0;
          }
          return !!state.filters[key];
        }),
      });
    }
  }, [
    dataLoading,
    data,
    table,
    filteredData?.length,
    state.models.length,
    filteredData,
    state.filters,
  ]);

  // If an error occurred, display it
  if (dataError || processingError) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography color="error">
          {(dataError || processingError)?.message ||
            "An error occurred while loading the data"}
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <PerformanceMonitor />
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 0,
          alignItems: "center",
        }}
      >
        <Box
          sx={{
            width: {
              xs: "100%",
              sm: "100%",
              md: "80%",
            },
            maxWidth: "1200px",
          }}
        >
          {loadingStates.showSearchSkeleton ? (
            <SearchBarSkeleton />
          ) : (
            memoizedSearchBar
          )}
          <Box sx={{ mt: 1 }}>
            {loadingStates.showFiltersSkeleton ? (
              <QuickFiltersSkeleton />
            ) : (
              <FilterAccordion
                expanded={state.filtersExpanded}
                quickFilters={memoizedQuickFilters}
                advancedFilters={memoizedLeaderboardFilters}
              />
            )}
          </Box>
        </Box>

        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            width: "100%",
            overflow: "hidden",
          }}
        >
          <Box
            sx={{
              width: "100%",
              px: 1,
            }}
          >
            {tableComponent}
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Leaderboard;

import { useMemo, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useLeaderboard } from "../context/LeaderboardContext";
import { useDataProcessing } from "../components/Table/hooks/useDataProcessing";

const CACHE_KEY = "leaderboardData";
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const useLeaderboardData = () => {
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const isInitialLoadRef = useRef(true);

  const { data, isLoading, error } = useQuery({
    queryKey: ["leaderboard"],
    queryFn: async () => {
      try {
        const cachedData = localStorage.getItem(CACHE_KEY);
        if (cachedData) {
          const { data: cached, timestamp } = JSON.parse(cachedData);
          const age = Date.now() - timestamp;
          if (age < CACHE_DURATION) {
            return cached;
          }
        }

        const response = await fetch("/api/leaderboard/formatted");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const newData = await response.json();
        localStorage.setItem(
          CACHE_KEY,
          JSON.stringify({
            data: newData,
            timestamp: Date.now(),
          })
        );

        return newData;
      } catch (error) {
        console.error("Detailed error:", error);
        throw error;
      }
    },
    staleTime: CACHE_DURATION,
    cacheTime: CACHE_DURATION * 2,
    refetchOnWindowFocus: false,
    enabled: isInitialLoadRef.current || !!searchParams.toString(),
  });

  useMemo(() => {
    if (data && isInitialLoadRef.current) {
      isInitialLoadRef.current = false;
    }
  }, [data]);

  return {
    data,
    isLoading,
    error,
    refetch: () => queryClient.invalidateQueries(["leaderboard"]),
  };
};

export const useLeaderboardProcessing = () => {
  const { state, actions } = useLeaderboard();
  const [sorting, setSorting] = useState([
    { id: "model.average_score", desc: true },
  ]);

  const memoizedData = useMemo(() => state.models, [state.models]);
  const memoizedFilters = useMemo(
    () => ({
      search: state.filters.search,
      precisions: state.filters.precisions,
      types: state.filters.types,
      paramsRange: state.filters.paramsRange,
      booleanFilters: state.filters.booleanFilters,
      isOfficialProviderActive: state.filters.isOfficialProviderActive,
    }),
    [
      state.filters.search,
      state.filters.precisions,
      state.filters.types,
      state.filters.paramsRange,
      state.filters.booleanFilters,
      state.filters.isOfficialProviderActive,
    ]
  );

  const {
    table,
    minAverage,
    maxAverage,
    getColorForValue,
    processedData,
    filteredData,
    columns,
    columnVisibility,
  } = useDataProcessing(
    memoizedData,
    memoizedFilters.search,
    memoizedFilters.precisions,
    memoizedFilters.types,
    memoizedFilters.paramsRange,
    memoizedFilters.booleanFilters,
    sorting,
    state.display.rankingMode,
    state.display.averageMode,
    state.display.visibleColumns,
    state.display.scoreDisplay,
    state.pinnedModels,
    actions.togglePinnedModel,
    setSorting,
    memoizedFilters.isOfficialProviderActive
  );

  return {
    table,
    minAverage,
    maxAverage,
    getColorForValue,
    processedData,
    filteredData,
    columns,
    columnVisibility,
    loading: state.loading,
    error: state.error,
  };
};

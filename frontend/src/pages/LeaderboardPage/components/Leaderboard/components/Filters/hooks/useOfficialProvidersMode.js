import { useCallback, useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";

const useRouterSearchParams = () => {
  try {
    return useSearchParams();
  } catch {
    return [null, () => {}];
  }
};

export const useOfficialProvidersMode = () => {
  const [isOfficialProviderActive, setIsOfficialProviderActive] =
    useState(false);
  const [searchParams, setSearchParams] = useRouterSearchParams();
  const normalFiltersRef = useRef(null);
  const isInitialLoadRef = useRef(true);
  const lastToggleSourceRef = useRef(null);

  // Effect to handle initial state and updates
  useEffect(() => {
    if (!searchParams) return;

    const filters = searchParams.get("filters");
    const isHighlighted =
      filters?.includes("is_highlighted_by_maintainer") || false;

    // On initial load
    if (isInitialLoadRef.current) {
      isInitialLoadRef.current = false;

      // If official mode is active at start, store filters without the highlightFilter
      if (isHighlighted && filters) {
        const initialNormalFilters = filters
          .split(",")
          .filter((f) => f !== "is_highlighted_by_maintainer" && f !== "")
          .filter(Boolean);
        if (initialNormalFilters.length > 0) {
          normalFiltersRef.current = initialNormalFilters.join(",");
        }
      }

      // Update state without triggering URL change
      setIsOfficialProviderActive(isHighlighted);
      return;
    }

    // For subsequent changes
    if (!isHighlighted && filters) {
      normalFiltersRef.current = filters;
    }

    setIsOfficialProviderActive(isHighlighted);
  }, [searchParams]);

  const toggleOfficialProviderMode = useCallback(
    (source = null) => {
      if (!searchParams || !setSearchParams) return;

      // If source is the same as last time and last change was less than 100ms ago, ignore
      const now = Date.now();
      if (
        source &&
        source === lastToggleSourceRef.current?.source &&
        now - (lastToggleSourceRef.current?.timestamp || 0) < 100
      ) {
        return;
      }

      const currentFiltersStr = searchParams.get("filters");
      const currentFilters =
        currentFiltersStr?.split(",").filter(Boolean) || [];
      const highlightFilter = "is_highlighted_by_maintainer";
      const newSearchParams = new URLSearchParams(searchParams);

      if (currentFilters.includes(highlightFilter)) {
        // Deactivating official provider mode
        if (normalFiltersRef.current) {
          const normalFilters = normalFiltersRef.current
            .split(",")
            .filter((f) => f !== highlightFilter && f !== "")
            .filter(Boolean);

          if (normalFilters.length > 0) {
            newSearchParams.set("filters", normalFilters.join(","));
          } else {
            newSearchParams.delete("filters");
          }
        } else {
          const newFilters = currentFilters.filter(
            (f) => f !== highlightFilter && f !== ""
          );
          if (newFilters.length === 0) {
            newSearchParams.delete("filters");
          } else {
            newSearchParams.set("filters", newFilters.join(","));
          }
        }
      } else {
        // Activating official provider mode
        if (currentFiltersStr) {
          normalFiltersRef.current = currentFiltersStr;
        }

        const filtersToSet = [
          ...new Set([...currentFilters, highlightFilter]),
        ].filter(Boolean);
        newSearchParams.set("filters", filtersToSet.join(","));
      }

      // Update state immediately
      setIsOfficialProviderActive(!currentFilters.includes(highlightFilter));

      // Save source and timestamp of last change
      lastToggleSourceRef.current = {
        source,
        timestamp: now,
      };

      // Update search params and let HashRouter handle the URL
      setSearchParams(newSearchParams);
    },
    [searchParams, setSearchParams]
  );

  return {
    isOfficialProviderActive,
    toggleOfficialProviderMode,
  };
};

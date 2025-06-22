import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useMemo,
  useCallback,
} from "react";
import { useSearchParams, useLocation } from "react-router-dom";
import { MODEL_TYPE_ORDER } from "../constants/modelTypes";
import { FILTER_PRECISIONS, TABLE_DEFAULTS } from "../constants/defaults";

// Create context
const LeaderboardContext = createContext();

// Define default filter values
const DEFAULT_FILTERS = {
  search: "",
  precisions: FILTER_PRECISIONS,
  types: MODEL_TYPE_ORDER,
  paramsRange: [-1, 140],
  booleanFilters: [],
  isOfficialProviderActive: false,
};

// Define default display values
const DEFAULT_DISPLAY = {
  rowSize: TABLE_DEFAULTS.ROW_SIZE,
  scoreDisplay: TABLE_DEFAULTS.SCORE_DISPLAY,
  averageMode: TABLE_DEFAULTS.AVERAGE_MODE,
  rankingMode: TABLE_DEFAULTS.RANKING_MODE,
  visibleColumns: [
    'isPinned',
    'rank',
    'model_type',
    'id',
    'model.average_score',
    'evaluations.vision_average',
    'evaluations.audio_average', 
    'evaluations.english_average',
    'evaluations.chinese_average',
    'evaluations.japanese_average',
    'evaluations.spanish_average',
    'evaluations.greek_average',
    'evaluations.bilingual_average',
    'evaluations.multilingual_average'
  ],
};

// Create initial counter structure
const createInitialCounts = () => {
  const modelTypes = {};
  MODEL_TYPE_ORDER.forEach((type) => {
    modelTypes[type] = 0;
  });

  const precisions = {};
  FILTER_PRECISIONS.forEach((precision) => {
    precisions[precision] = 0;
  });

  return {
    modelTypes,
    precisions,
    maintainersHighlight: 0,
    mixtureOfExperts: 0,
    flagged: 0,
    merged: 0,
    notOnHub: 0,
    parameterRanges: {
      edge: 0,
      small: 0,
      medium: 0,
      large: 0,
    },
  };
};

// Define initial state
const initialState = {
  models: [],
  loading: true,
  countsReady: false,
  error: null,
  filters: DEFAULT_FILTERS,
  display: DEFAULT_DISPLAY,
  filtersExpanded: false,
  pinnedModels: [],
  filterCounts: {
    normal: createInitialCounts(),
    officialOnly: createInitialCounts(),
  },
};

// Function to normalize parameter value
const normalizeParams = (params) => {
  const numParams = Number(params);
  if (isNaN(numParams)) return null;
  return Math.round(numParams * 100) / 100;
};

// Function to check if a parameter count is within a range
const isInParamRange = (params, range) => {
  if (range[0] === -1 && range[1] === 140) return true;
  const normalizedParams = normalizeParams(params);
  if (normalizedParams === null) return false;
  return normalizedParams >= range[0] && normalizedParams < range[1];
};

// Function to check if a model matches filter criteria
const modelMatchesFilters = (model, filters) => {
  // Filter by precision
  if (
    filters.precisions.length > 0 &&
    !filters.precisions.includes(model.model.precision)
  ) {
    return false;
  }

  // Filter by type
  if (filters.types.length > 0) {
    const modelType = model.model.type?.toLowerCase().trim();
    if (!filters.types.some((type) => modelType?.includes(type))) {
      return false;
    }
  }

  // Filter by parameters
  const params = Number(
    model.metadata?.params_billions || model.features?.params_billions
  );
  if (!isInParamRange(params, filters.paramsRange)) return false;

  // Filter by search
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    const modelName = model.model.name.toLowerCase();
    if (!modelName.includes(searchLower)) return false;
  }

  // Boolean filters
  if (filters.booleanFilters.length > 0) {
    return filters.booleanFilters.every((filter) => {
      const filterValue = typeof filter === "object" ? filter.value : filter;

      // Maintainer's Highlight keeps positive logic
      if (filterValue === "is_highlighted_by_maintainer") {
        return model.features[filterValue];
      }

      // For all other filters, invert the logic
      if (filterValue === "is_not_available_on_hub") {
        return model.features[filterValue];
      }

      return !model.features[filterValue];
    });
  }

  return true;
};

// Function to calculate filtered model counts
const calculateFilteredCounts = (
  allRows,
  totalPinnedCount,
  filters,
  filteredCount
) => {
  // If no table, use raw filteredCount
  if (!allRows) {
    return {
      currentFilteredCount:
        typeof filteredCount === "number" ? filteredCount : 0,
      totalPinnedCount: totalPinnedCount || 0,
    };
  }

  // 1. Total number of rows (models matching filters)
  const totalFilteredCount = allRows.length;

  // 2. Number of pinned models that also match filters
  // These models are already included in totalFilteredCount, so we need to subtract them
  // to avoid counting them twice
  const pinnedMatchingFilters = allRows.filter((row) => {
    const model = row.original;
    return model.isPinned && modelMatchesFilters(model, filters);
  }).length;

  return {
    // Subtract pinned models that match filters
    // as they are already displayed separately with "+X"
    currentFilteredCount: totalFilteredCount - pinnedMatchingFilters,
    totalPinnedCount: totalPinnedCount || 0,
  };
};

// Function to calculate counters
const calculateModelCounts = (models) => {
  const normalCounts = createInitialCounts();
  const officialOnlyCounts = createInitialCounts();

  models.forEach((model) => {
    const isOfficial =
      model.features?.is_highlighted_by_maintainer ||
      model.metadata?.is_highlighted_by_maintainer;
    const countsToUpdate = [normalCounts];

    if (isOfficial) {
      countsToUpdate.push(officialOnlyCounts);
    }

    countsToUpdate.forEach((counts) => {
      // Model type
      if (model.model?.type) {
        const cleanType = model.model.type.toLowerCase().trim();
        const matchedType = MODEL_TYPE_ORDER.find((key) =>
          cleanType.includes(key)
        );
        if (matchedType) {
          counts.modelTypes[matchedType]++;
        }
      }

      // Precision
      if (model.model?.precision) {
        counts.precisions[model.model.precision]++;
      }

      // Boolean filters
      if (
        model.features?.is_highlighted_by_maintainer ||
        model.metadata?.is_highlighted_by_maintainer
      )
        counts.maintainersHighlight++;
      if (model.features?.is_moe || model.metadata?.is_moe)
        counts.mixtureOfExperts++;
      if (model.features?.is_flagged || model.metadata?.is_flagged)
        counts.flagged++;
      if (model.features?.is_merged || model.metadata?.is_merged)
        counts.merged++;
      if (
        !(
          model.features?.is_not_available_on_hub ||
          model.metadata?.is_not_available_on_hub
        )
      )
        counts.notOnHub++;

      // Parameter ranges
      const params = Number(
        model.metadata?.params_billions || model.features?.params_billions
      );
      if (!isNaN(params)) {
        if (isInParamRange(params, [0, 3])) counts.parameterRanges.edge++;
        if (isInParamRange(params, [3, 7])) counts.parameterRanges.small++;
        if (isInParamRange(params, [7, 65])) counts.parameterRanges.medium++;
        if (isInParamRange(params, [65, 141])) counts.parameterRanges.large++;
      }
    });
  });

  return {
    normal: normalCounts,
    officialOnly: officialOnlyCounts,
  };
};

// Define reducer
const reducer = (state, action) => {
  switch (action.type) {
    case "SET_MODELS":
      const newCounts = calculateModelCounts(action.payload);
      return {
        ...state,
        models: action.payload,
        filterCounts: newCounts,
        countsReady: true,
        loading: false,
      };

    case "SET_LOADING":
      return {
        ...state,
        loading: action.payload,
        ...(action.payload ? { countsReady: false } : {}),
      };

    case "SET_ERROR":
      return {
        ...state,
        error: action.payload,
        loading: false,
      };

    case "SET_FILTER":
      return {
        ...state,
        filters: {
          ...state.filters,
          [action.key]: action.value,
        },
      };

    case "SET_DISPLAY_OPTION":
      return {
        ...state,
        display: {
          ...state.display,
          [action.key]: action.value,
        },
      };

    case "TOGGLE_PINNED_MODEL":
      const modelKey = action.payload;
      const pinnedModels = [...state.pinnedModels];
      const modelIndex = pinnedModels.indexOf(modelKey);

      if (modelIndex === -1) {
        pinnedModels.push(modelKey);
      } else {
        pinnedModels.splice(modelIndex, 1);
      }

      return {
        ...state,
        pinnedModels,
      };

    case "SET_PINNED_MODELS":
      return {
        ...state,
        pinnedModels: action.payload,
      };

    case "TOGGLE_FILTERS_EXPANDED":
      return {
        ...state,
        filtersExpanded: !state.filtersExpanded,
      };

    case "TOGGLE_OFFICIAL_PROVIDER":
      return {
        ...state,
        filters: {
          ...state.filters,
          isOfficialProviderActive: !state.filters.isOfficialProviderActive,
        },
      };

    case "RESET_FILTERS":
      return {
        ...state,
        filters: DEFAULT_FILTERS,
      };

    case "RESET_ALL":
      return {
        ...state,
        filters: DEFAULT_FILTERS,
        display: DEFAULT_DISPLAY,
        pinnedModels: [],
      };

    default:
      return state;
  }
};

// Provider component
const LeaderboardProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();

  // Effect to load initial values from URL
  useEffect(() => {
    // Skip URL sync if we're resetting
    if (location.state?.skipUrlSync) return;

    const loadFromUrl = () => {
      // Load filters
      const searchFromUrl = searchParams.get("search");
      if (searchFromUrl) {
        dispatch({ type: "SET_FILTER", key: "search", value: searchFromUrl });
      }

      const paramsFromUrl = searchParams.get("params")?.split(",").map(Number);
      if (paramsFromUrl?.length === 2) {
        dispatch({
          type: "SET_FILTER",
          key: "paramsRange",
          value: paramsFromUrl,
        });
      }

      const filtersFromUrl =
        searchParams.get("filters")?.split(",").filter(Boolean) || [];
      if (filtersFromUrl.length > 0) {
        dispatch({
          type: "SET_FILTER",
          key: "booleanFilters",
          value: filtersFromUrl,
        });
      }

      const precisionsFromUrl = searchParams
        .get("precision")
        ?.split(",")
        .filter(Boolean);
      if (precisionsFromUrl) {
        dispatch({
          type: "SET_FILTER",
          key: "precisions",
          value: precisionsFromUrl,
        });
      }

      const typesFromUrl = searchParams
        .get("types")
        ?.split(",")
        .filter(Boolean);
      if (typesFromUrl) {
        dispatch({ type: "SET_FILTER", key: "types", value: typesFromUrl });
      }

      const officialFromUrl = searchParams.get("official") === "true";
      if (officialFromUrl) {
        dispatch({
          type: "SET_FILTER",
          key: "isOfficialProviderActive",
          value: true,
        });
      }

      // Load pinned models
      const pinnedFromUrl =
        searchParams.get("pinned")?.split(",").filter(Boolean) || [];
      if (pinnedFromUrl.length > 0) {
        dispatch({ type: "SET_PINNED_MODELS", payload: pinnedFromUrl });
      }

      // Load visible columns
      const columnsFromUrl = searchParams
        .get("columns")
        ?.split(",")
        .filter(Boolean);
      if (columnsFromUrl) {
        dispatch({
          type: "SET_DISPLAY_OPTION",
          key: "visibleColumns",
          value: columnsFromUrl,
        });
      }

      // Load table options
      const rowSizeFromUrl = searchParams.get("rowSize");
      if (rowSizeFromUrl) {
        dispatch({
          type: "SET_DISPLAY_OPTION",
          key: "rowSize",
          value: rowSizeFromUrl,
        });
      }

      const scoreDisplayFromUrl = searchParams.get("scoreDisplay");
      if (scoreDisplayFromUrl) {
        dispatch({
          type: "SET_DISPLAY_OPTION",
          key: "scoreDisplay",
          value: scoreDisplayFromUrl,
        });
      }

      const averageModeFromUrl = searchParams.get("averageMode");
      if (averageModeFromUrl) {
        dispatch({
          type: "SET_DISPLAY_OPTION",
          key: "averageMode",
          value: averageModeFromUrl,
        });
      }

      const rankingModeFromUrl = searchParams.get("rankingMode");
      if (rankingModeFromUrl) {
        dispatch({
          type: "SET_DISPLAY_OPTION",
          key: "rankingMode",
          value: rankingModeFromUrl,
        });
      }
    };

    loadFromUrl();
  }, [searchParams, location.state]);

  // Effect to synchronize filters with URL
  useEffect(() => {
    // Skip URL sync if we're resetting
    if (location.state?.skipUrlSync) return;

    const newSearchParams = new URLSearchParams(searchParams);
    const currentParams = searchParams.get("params")?.split(",").map(Number);
    const currentFilters =
      searchParams.get("filters")?.split(",").filter(Boolean) || [];
    const currentSearch = searchParams.get("search");
    const currentPinned =
      searchParams.get("pinned")?.split(",").filter(Boolean) || [];
    const currentColumns =
      searchParams.get("columns")?.split(",").filter(Boolean) || [];
    const currentRowSize = searchParams.get("rowSize");
    const currentScoreDisplay = searchParams.get("scoreDisplay");
    const currentAverageMode = searchParams.get("averageMode");
    const currentRankingMode = searchParams.get("rankingMode");
    const currentOfficialProvider = searchParams.get("official") === "true";
    const currentPrecisions =
      searchParams.get("precision")?.split(",").filter(Boolean) || [];
    const currentTypes =
      searchParams.get("types")?.split(",").filter(Boolean) || [];

    // Only update URL if values have changed
    const paramsChanged =
      !currentParams ||
      currentParams[0] !== state.filters.paramsRange[0] ||
      currentParams[1] !== state.filters.paramsRange[1];

    const filtersChanged =
      state.filters.booleanFilters.length !== currentFilters.length ||
      state.filters.booleanFilters.some((f) => !currentFilters.includes(f));

    const searchChanged = state.filters.search !== currentSearch;

    const pinnedChanged =
      state.pinnedModels.length !== currentPinned.length ||
      state.pinnedModels.some((m) => !currentPinned.includes(m));

    const columnsChanged =
      state.display.visibleColumns.length !== currentColumns.length ||
      state.display.visibleColumns.some((c) => !currentColumns.includes(c));

    const rowSizeChanged = state.display.rowSize !== currentRowSize;
    const scoreDisplayChanged =
      state.display.scoreDisplay !== currentScoreDisplay;
    const averageModeChanged = state.display.averageMode !== currentAverageMode;
    const rankingModeChanged = state.display.rankingMode !== currentRankingMode;
    const officialProviderChanged =
      state.filters.isOfficialProviderActive !== currentOfficialProvider;
    const precisionsChanged =
      state.filters.precisions.length !== currentPrecisions.length ||
      state.filters.precisions.some((p) => !currentPrecisions.includes(p));
    const typesChanged =
      state.filters.types.length !== currentTypes.length ||
      state.filters.types.some((t) => !currentTypes.includes(t));

    if (paramsChanged) {
      if (
        state.filters.paramsRange[0] !== -1 ||
        state.filters.paramsRange[1] !== 140
      ) {
        newSearchParams.set("params", state.filters.paramsRange.join(","));
      } else {
        newSearchParams.delete("params");
      }
    }

    if (filtersChanged) {
      if (state.filters.booleanFilters.length > 0) {
        newSearchParams.set("filters", state.filters.booleanFilters.join(","));
      } else {
        newSearchParams.delete("filters");
      }
    }

    if (searchChanged) {
      if (state.filters.search) {
        newSearchParams.set("search", state.filters.search);
      } else {
        newSearchParams.delete("search");
      }
    }

    if (pinnedChanged) {
      if (state.pinnedModels.length > 0) {
        newSearchParams.set("pinned", state.pinnedModels.join(","));
      } else {
        newSearchParams.delete("pinned");
      }
    }

    if (columnsChanged) {
      if (
        JSON.stringify([...state.display.visibleColumns].sort()) !==
        JSON.stringify([...TABLE_DEFAULTS.COLUMNS.DEFAULT_VISIBLE].sort())
      ) {
        newSearchParams.set("columns", state.display.visibleColumns.join(","));
      } else {
        newSearchParams.delete("columns");
      }
    }

    if (rowSizeChanged) {
      if (state.display.rowSize !== TABLE_DEFAULTS.ROW_SIZE) {
        newSearchParams.set("rowSize", state.display.rowSize);
      } else {
        newSearchParams.delete("rowSize");
      }
    }

    if (scoreDisplayChanged) {
      if (state.display.scoreDisplay !== TABLE_DEFAULTS.SCORE_DISPLAY) {
        newSearchParams.set("scoreDisplay", state.display.scoreDisplay);
      } else {
        newSearchParams.delete("scoreDisplay");
      }
    }

    if (averageModeChanged) {
      if (state.display.averageMode !== TABLE_DEFAULTS.AVERAGE_MODE) {
        newSearchParams.set("averageMode", state.display.averageMode);
      } else {
        newSearchParams.delete("averageMode");
      }
    }

    if (rankingModeChanged) {
      if (state.display.rankingMode !== TABLE_DEFAULTS.RANKING_MODE) {
        newSearchParams.set("rankingMode", state.display.rankingMode);
      } else {
        newSearchParams.delete("rankingMode");
      }
    }

    if (officialProviderChanged) {
      if (state.filters.isOfficialProviderActive) {
        newSearchParams.set("official", "true");
      } else {
        newSearchParams.delete("official");
      }
    }

    if (precisionsChanged) {
      if (
        JSON.stringify([...state.filters.precisions].sort()) !==
        JSON.stringify([...FILTER_PRECISIONS].sort())
      ) {
        newSearchParams.set("precision", state.filters.precisions.join(","));
      } else {
        newSearchParams.delete("precision");
      }
    }

    if (typesChanged) {
      if (
        JSON.stringify([...state.filters.types].sort()) !==
        JSON.stringify([...MODEL_TYPE_ORDER].sort())
      ) {
        newSearchParams.set("types", state.filters.types.join(","));
      } else {
        newSearchParams.delete("types");
      }
    }

    if (
      paramsChanged ||
      filtersChanged ||
      searchChanged ||
      pinnedChanged ||
      columnsChanged ||
      rowSizeChanged ||
      scoreDisplayChanged ||
      averageModeChanged ||
      rankingModeChanged ||
      officialProviderChanged ||
      precisionsChanged ||
      typesChanged
    ) {
      // Update search params and let HashRouter handle the URL
      setSearchParams(newSearchParams);
    }
  }, [state, searchParams, location.state]);

  const actions = useMemo(
    () => ({
      setModels: (models) => dispatch({ type: "SET_MODELS", payload: models }),
      setLoading: (loading) =>
        dispatch({ type: "SET_LOADING", payload: loading }),
      setError: (error) => dispatch({ type: "SET_ERROR", payload: error }),
      setFilter: (key, value) => dispatch({ type: "SET_FILTER", key, value }),
      setDisplayOption: (key, value) =>
        dispatch({ type: "SET_DISPLAY_OPTION", key, value }),
      togglePinnedModel: (modelKey) =>
        dispatch({ type: "TOGGLE_PINNED_MODEL", payload: modelKey }),
      toggleOfficialProvider: () =>
        dispatch({ type: "TOGGLE_OFFICIAL_PROVIDER" }),
      toggleFiltersExpanded: () =>
        dispatch({ type: "TOGGLE_FILTERS_EXPANDED" }),
      resetFilters: () => {
        dispatch({ type: "RESET_FILTERS" });
        const newParams = new URLSearchParams(searchParams);
        [
          "filters",
          "params",
          "precision",
          "types",
          "official",
          "search",
        ].forEach((param) => {
          newParams.delete(param);
        });
        setSearchParams(newParams);
      },
      resetAll: () => {
        // Reset all state
        dispatch({ type: "RESET_ALL" });
        // Clear all URL params with skipUrlSync flag
        setSearchParams({}, { state: { skipUrlSync: true } });
      },
    }),
    [searchParams, setSearchParams]
  );

  // Function to calculate counts (exposed via context)
  const getFilteredCounts = useCallback(
    (allRows, totalPinnedCount, filteredCount) => {
      return calculateFilteredCounts(
        allRows,
        totalPinnedCount,
        state.filters,
        filteredCount
      );
    },
    [state.filters]
  );

  // Also expose filtering function for reuse elsewhere
  const checkModelMatchesFilters = useCallback(
    (model) => {
      return modelMatchesFilters(model, state.filters);
    },
    [state.filters]
  );

  const value = useMemo(
    () => ({
      state: {
        ...state,
        loading: state.loading || !state.countsReady,
      },
      actions,
      utils: {
        getFilteredCounts,
        checkModelMatchesFilters,
      },
    }),
    [state, actions, getFilteredCounts, checkModelMatchesFilters]
  );

  return (
    <LeaderboardContext.Provider value={value}>
      {children}
    </LeaderboardContext.Provider>
  );
};

// Hook to use context
const useLeaderboard = () => {
  const context = useContext(LeaderboardContext);
  if (!context) {
    throw new Error("useLeaderboard must be used within a LeaderboardProvider");
  }
  return context;
};

export { useLeaderboard };
export default LeaderboardProvider;

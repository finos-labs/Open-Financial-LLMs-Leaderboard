import React, { useState, useEffect } from "react";
import { Box, InputBase, Typography, Paper, Skeleton } from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import FilterListIcon from "@mui/icons-material/FilterList";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { useTheme } from "@mui/material/styles";
import { generateSearchDescription } from "../../utils/searchUtils";
import {
  HIGHLIGHT_COLORS,
  TABLE_DEFAULTS,
  FILTER_PRECISIONS,
} from "../../constants/defaults";
import { MODEL_TYPE_ORDER } from "../../constants/modelTypes";
import { alpha } from "@mui/material/styles";
import FilteredModelCount from "./FilteredModelCount";
import { useLeaderboard } from "../../context/LeaderboardContext";
import InfoIconWithTooltip from "../../../../../../components/shared/InfoIconWithTooltip";
import { UI_TOOLTIPS } from "../../constants/tooltips";

export const SearchBarSkeleton = () => (
  <Box>
    <Box
      sx={{
        width: "100%",
        height: "56px",
        bgcolor: (theme) => alpha(theme.palette.background.paper, 0.8),
        borderRadius: 1,
        border: (theme) =>
          `1px solid ${alpha(
            theme.palette.divider,
            theme.palette.mode === "dark" ? 0.05 : 0.1
          )}`,
        display: "flex",
        alignItems: "center",
        px: 2,
        gap: 2,
      }}
    >
      <Skeleton variant="circular" width={20} height={20} />
      <Skeleton variant="text" sx={{ flex: 7 }} height={32} />
      <Skeleton variant="text" sx={{ flex: 1 }} height={32} />
      <Box sx={{ display: "flex", gap: 1 }}>
        <Skeleton variant="rounded" width={150} height={28} />
      </Box>
      <Skeleton variant="circular" width={20} height={20} />
    </Box>
    <Box sx={{ ml: 3.5 }}>
      <Typography
        variant="caption"
        sx={{
          color: "text.secondary",
          fontSize: "0.75rem",
          textAlign: "left",
          opacity: 1,
          transition: "opacity 0.2s ease",
          height: "18px",
        }}
      >
        Supports strict search and regex • Use semicolons for multiple terms
      </Typography>
    </Box>
  </Box>
);

const SearchDescription = ({ searchValue }) => {
  const searchGroups = generateSearchDescription(searchValue);

  if (!searchGroups || searchGroups.length === 0) return null;

  return (
    <Box
      sx={{ display: "flex", gap: 1, flexWrap: "wrap", alignItems: "center" }}
    >
      <Typography
        sx={{
          color: "text.secondary",
          fontSize: "0.85rem",
        }}
      >
        Showing models matching:
      </Typography>
      {searchGroups.map(({ text, index }, i) => (
        <React.Fragment key={index}>
          {i > 0 && (
            <Typography
              sx={{
                color: "text.secondary",
                fontSize: "0.85rem",
              }}
            >
              and
            </Typography>
          )}
          <Box
            sx={{
              backgroundColor:
                HIGHLIGHT_COLORS[index % HIGHLIGHT_COLORS.length],
              color: (theme) =>
                theme.palette.getContrastText(
                  HIGHLIGHT_COLORS[index % HIGHLIGHT_COLORS.length]
                ),
              padding: "2px 4px",
              borderRadius: "4px",
              fontSize: "0.85rem",
              fontWeight: 500,
            }}
          >
            {text}
          </Box>
        </React.Fragment>
      ))}
    </Box>
  );
};

const SearchBar = ({
  onToggleFilters,
  filtersOpen,
  loading = false,
  data = [],
  table = null,
}) => {
  const theme = useTheme();
  const { state, actions } = useLeaderboard();
  const [localValue, setLocalValue] = useState(state.filters.search);

  useEffect(() => {
    setLocalValue(state.filters.search);
  }, [state.filters.search]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== state.filters.search) {
        actions.setFilter("search", localValue);
      }
    }, TABLE_DEFAULTS.DEBOUNCE.SEARCH);

    return () => clearTimeout(timer);
  }, [localValue, state.filters.search, actions]);

  const handleLocalChange = (e) => {
    setLocalValue(e.target.value);
  };

  const hasActiveFilters =
    Object.values(state.filters.booleanFilters).some((value) => value) ||
    state.filters.precisions.length !== FILTER_PRECISIONS.length ||
    state.filters.types.length !== MODEL_TYPE_ORDER.length ||
    state.filters.paramsRange[0] !== -1 ||
    state.filters.paramsRange[1] !== 140 ||
    state.filters.isOfficialProviderActive;

  const shouldShowReset = localValue || hasActiveFilters;

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        gap: 0.5,
      }}
    >
      <Paper
        elevation={0}
        sx={{
          display: "flex",
          alignItems: "center",
          flex: 1,
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 1,
          px: 2,
          py: 1.5,
          backgroundColor: "background.paper",
          "&:focus-within": {
            borderColor: "primary.main",
          },
        }}
      >
        <SearchIcon
          sx={{ color: "text.secondary", mr: 1, fontSize: "1.5rem" }}
        />
        <InputBase
          value={localValue}
          onChange={handleLocalChange}
          placeholder='Search by model name • try "meta @architecture:llama @license:mit"'
          sx={{
            flex: 1,
            fontSize: "1rem",
            color: "text.primary",
            mr: 4,
            "& .MuiInputBase-input": {
              padding: "2px 0",
              fontWeight: 600,
              "&::placeholder": {
                color: "text.secondary",
                opacity: 0.8,
              },
            },
          }}
        />
        {!loading && (
          <FilteredModelCount
            totalCount={state.models.length}
            filteredCount={data.length}
            hasFilterChanges={hasActiveFilters}
            loading={loading}
            isOfficialProviderActive={state.filters.isOfficialProviderActive}
            officialProvidersCount={state.filters.officialProvidersCount}
            size="large"
            data={data}
            table={table}
          />
        )}
        <Box sx={{ display: "flex", gap: 1, ml: 2 }}>
          {shouldShowReset && (
            <Box
              onClick={() => {
                setLocalValue("");
                actions.resetFilters();
              }}
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 0.5,
                cursor: "pointer",
                color: "text.secondary",
                backgroundColor: "transparent",
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 1,
                padding: "4px 8px",
                "&:hover": {
                  backgroundColor: "action.hover",
                  color: "text.primary",
                },
                userSelect: "none",
                transition: "all 0.2s ease",
              }}
            >
              <RestartAltIcon sx={{ fontSize: "1.2rem" }} />
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 600,
                  display: { xs: "none", md: "block" },
                }}
              >
                Reset
              </Typography>
            </Box>
          )}
          <Box
            onClick={onToggleFilters}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 0.5,
              cursor: "pointer",
              color:
                !loading && hasActiveFilters
                  ? "primary.main"
                  : filtersOpen
                  ? "primary.main"
                  : "text.secondary",
              backgroundColor: filtersOpen
                ? alpha(theme.palette.primary.main, 0.04)
                : "transparent",
              border: "1px solid",
              borderColor: filtersOpen ? "primary.100" : "divider",
              borderRadius: 1,
              padding: "4px 8px",
              "&:hover": {
                backgroundColor: alpha(theme.palette.primary.main, 0.08),
              },
              userSelect: "none",
            }}
          >
            <FilterListIcon sx={{ fontSize: "1.2rem" }} />
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                display: { xs: "none", md: "block" },
              }}
            >
              Advanced Filters
            </Typography>
          </Box>
          <InfoIconWithTooltip
            tooltip={UI_TOOLTIPS.SEARCH_BAR}
            iconProps={{
              sx: { fontSize: "1.2rem", display: { xs: "none", md: "block" } },
            }}
          />
        </Box>
      </Paper>
      <Box sx={{ ml: 3.5, mr: 3.5 }}>
        {localValue ? (
          <SearchDescription searchValue={localValue} />
        ) : (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography
              variant="caption"
              sx={{
                color: "text.secondary",
                fontSize: "0.75rem",
                textAlign: { xs: "center", md: "left" },
                opacity: 1,
                transition: "opacity 0.2s ease",
                minHeight: "18px",
                width: "100%",
                whiteSpace: "normal",
                lineHeight: 1.5,
              }}
            >
              Supports strict search and regex • Use semicolons for multiple
              terms
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default SearchBar;

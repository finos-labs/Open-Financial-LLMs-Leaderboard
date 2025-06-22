import React from "react";
import { Box, Typography } from "@mui/material";
import TuneIcon from "@mui/icons-material/Tune";
import CloseIcon from "@mui/icons-material/Close";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import FilterTag from "../../../../../../components/shared/FilterTag";
import {
  TABLE_DEFAULTS,
  ROW_SIZES,
  SCORE_DISPLAY_OPTIONS,
  RANKING_MODE_OPTIONS,
} from "../../constants/defaults";
import { UI_TOOLTIPS } from "../../constants/tooltips";
import DropdownButton from "../shared/DropdownButton";
import InfoIconWithTooltip from "../../../../../../components/shared/InfoIconWithTooltip";

const TableOptions = ({
  rowSize,
  onRowSizeChange,
  scoreDisplay = "normalized",
  onScoreDisplayChange,
  averageMode = "all",
  onAverageModeChange,
  rankingMode = "static",
  onRankingModeChange,
  hasChanges,
  searchParams,
  setSearchParams,
  loading = false,
}) => {
  const handleReset = () => {
    onRowSizeChange(TABLE_DEFAULTS.ROW_SIZE);
    onScoreDisplayChange(TABLE_DEFAULTS.SCORE_DISPLAY);
    onAverageModeChange(TABLE_DEFAULTS.AVERAGE_MODE);
    onRankingModeChange(TABLE_DEFAULTS.RANKING_MODE);

    const newParams = new URLSearchParams(searchParams);
    ["rowSize", "scoreDisplay", "averageMode", "rankingMode"].forEach(
      (param) => {
        newParams.delete(param);
      }
    );
    setSearchParams(newParams);
  };

  return (
    <DropdownButton
      label="table options"
      icon={TuneIcon}
      closeIcon={CloseIcon}
      hasChanges={hasChanges}
      loading={loading}
      defaultWidth={260}
      tooltip={UI_TOOLTIPS.DISPLAY_OPTIONS}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          mb: 3,
          pb: 2,
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Table Options
          </Typography>
          <InfoIconWithTooltip
            tooltip={UI_TOOLTIPS.DISPLAY_OPTIONS}
            iconProps={{ sx: { fontSize: "1rem", ml: 0.5 } }}
          />
        </Box>
        <Box
          onClick={hasChanges ? handleReset : undefined}
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 0.5,
            cursor: hasChanges ? "pointer" : "default",
            color: hasChanges ? "text.secondary" : "text.disabled",
            backgroundColor: "transparent",
            border: "1px solid",
            borderColor: hasChanges ? "divider" : "action.disabledBackground",
            borderRadius: 1,
            padding: "4px 8px",
            "&:hover": hasChanges
              ? {
                  backgroundColor: "action.hover",
                  color: "text.primary",
                }
              : {},
            userSelect: "none",
            transition: "all 0.2s ease",
          }}
        >
          <RestartAltIcon sx={{ fontSize: "1.2rem" }} />
          <Typography
            variant="body2"
            sx={{
              fontWeight: 600,
              display: { xs: "none", sm: "block" },
            }}
          >
            Reset
          </Typography>
        </Box>
      </Box>

      <Box>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <Box>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography variant="subtitle2">
                {UI_TOOLTIPS.ROW_SIZE.title}
              </Typography>
              <InfoIconWithTooltip
                tooltip={UI_TOOLTIPS.ROW_SIZE.description}
                iconProps={{ sx: { fontSize: "1rem", ml: 0.5 } }}
              />
            </Box>
            <Box sx={{ display: "flex", gap: 1 }}>
              {Object.keys(ROW_SIZES).map((size) => (
                <FilterTag
                  key={size}
                  label={size.charAt(0).toUpperCase() + size.slice(1)}
                  checked={rowSize === size}
                  onChange={() => onRowSizeChange(size)}
                  variant="tag"
                />
              ))}
            </Box>
          </Box>

          <Box>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography variant="subtitle2">
                {UI_TOOLTIPS.SCORE_DISPLAY.title}
              </Typography>
              <InfoIconWithTooltip
                tooltip={UI_TOOLTIPS.SCORE_DISPLAY.description}
                iconProps={{ sx: { fontSize: "1rem", ml: 0.5 } }}
              />
            </Box>
            <Box sx={{ display: "flex", gap: 1 }}>
              {SCORE_DISPLAY_OPTIONS.map(({ value, label }) => (
                <FilterTag
                  key={value}
                  label={label}
                  checked={scoreDisplay === value}
                  onChange={() => onScoreDisplayChange(value)}
                  variant="tag"
                />
              ))}
            </Box>
          </Box>

          <Box>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography variant="subtitle2">
                {UI_TOOLTIPS.RANKING_MODE.title}
              </Typography>
              <InfoIconWithTooltip
                tooltip={UI_TOOLTIPS.RANKING_MODE.description}
                iconProps={{ sx: { fontSize: "1rem", ml: 0.5 } }}
              />
            </Box>
            <Box sx={{ display: "flex", gap: 1 }}>
              {RANKING_MODE_OPTIONS.map(({ value, label }) => (
                <FilterTag
                  key={value}
                  label={label}
                  checked={rankingMode === value}
                  onChange={() => onRankingModeChange(value)}
                  variant="tag"
                />
              ))}
            </Box>
          </Box>

          <Box>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography variant="subtitle2">
                {UI_TOOLTIPS.AVERAGE_SCORE.title}
              </Typography>
              <InfoIconWithTooltip
                tooltip={UI_TOOLTIPS.AVERAGE_SCORE.description}
                iconProps={{ sx: { fontSize: "1rem", ml: 0.5 } }}
              />
            </Box>
            <Box sx={{ display: "flex", gap: 1 }}>
              <FilterTag
                label="All Scores"
                checked={averageMode === "all"}
                onChange={() => onAverageModeChange("all")}
                variant="tag"
              />
              <FilterTag
                label="Visible Only"
                checked={averageMode === "visible"}
                onChange={() => onAverageModeChange("visible")}
                variant="tag"
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </DropdownButton>
  );
};

export default TableOptions;

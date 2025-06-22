import React from "react";
import { Box, Typography } from "@mui/material";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import CloseIcon from "@mui/icons-material/Close";
import FilterTag from "../../../../../../components/shared/FilterTag";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { TABLE_DEFAULTS } from "../../constants/defaults";
import DropdownButton from "../shared/DropdownButton";
import InfoIconWithTooltip from "../../../../../../components/shared/InfoIconWithTooltip";
import { UI_TOOLTIPS } from "../../constants/tooltips";

const FilterGroup = ({ title, children, count, total }) => (
  <Box
    sx={{
      mb: 3,
    }}
  >
    <Typography
      variant="subtitle2"
      sx={{
        mb: 1.5,
        fontSize: "0.8rem",
        fontWeight: 700,
        color: "text.primary",
        display: "flex",
        alignItems: "center",
        gap: 0.5,
      }}
    >
      {title}
      {count !== undefined && total !== undefined && (
        <Typography
          component="span"
          variant="caption"
          sx={{
            color: "text.secondary",
            ml: 0.5,
            fontSize: "0.75rem",
          }}
        >
          ({count}/{total})
        </Typography>
      )}
    </Typography>
    <Box
      sx={{
        display: "flex",
        flexWrap: "wrap",
        gap: 1,
        alignItems: "center",
      }}
    >
      {children}
    </Box>
  </Box>
);

const ColumnSelector = ({
  table,
  onReset,
  hasChanges,
  onColumnVisibilityChange,
  loading = false,
}) => {
  const { getState, setColumnVisibility } = table;
  const { columnVisibility } = getState();

  // Filter columns to only show filterable ones
  const filterableColumns = [
    ...TABLE_DEFAULTS.COLUMNS.EVALUATION,
    ...TABLE_DEFAULTS.COLUMNS.OPTIONAL,
  ];

  const handleReset = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!hasChanges) return;

    // Call onReset first
    onReset?.();

    // Create object with all columns set to false by default
    const defaultVisibility = {};

    // Set to true all columns that should be visible by default
    TABLE_DEFAULTS.COLUMNS.DEFAULT_VISIBLE.forEach((col) => {
      defaultVisibility[col] = true;
    });

    onColumnVisibilityChange?.(defaultVisibility);
    setColumnVisibility(defaultVisibility);
  };

  const toggleColumn = (columnId) => {
    if (TABLE_DEFAULTS.COLUMNS.FIXED.includes(columnId)) return;

    const newVisibility = {
      ...columnVisibility,
      [columnId]: !columnVisibility[columnId],
    };

    setColumnVisibility(newVisibility);
    onColumnVisibilityChange?.(newVisibility);
  };

  return (
    <DropdownButton
      label="column visibility"
      icon={ViewColumnIcon}
      closeIcon={CloseIcon}
      hasChanges={hasChanges}
      loading={loading}
      tooltip={UI_TOOLTIPS.COLUMN_SELECTOR}
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
            Column Visibility
          </Typography>
          <InfoIconWithTooltip
            tooltip={UI_TOOLTIPS.COLUMN_SELECTOR}
            iconProps={{ sx: { fontSize: "1rem" } }}
          />
        </Box>
        <Box
          component="button"
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

      {Object.entries(TABLE_DEFAULTS.COLUMNS.COLUMN_GROUPS).map(
        ([groupTitle, columns]) => {
          // Calculer le nombre de colonnes cochées pour les évaluations
          const isEvalGroup = groupTitle === "Evaluation Scores";
          const filteredColumns = columns.filter((col) =>
            filterableColumns.includes(col)
          );
          const checkedCount = isEvalGroup
            ? filteredColumns.filter((col) => columnVisibility[col]).length
            : undefined;
          const totalCount = isEvalGroup ? filteredColumns.length : undefined;

          return (
            <FilterGroup
              key={groupTitle}
              title={groupTitle}
              count={checkedCount}
              total={totalCount}
            >
              {filteredColumns.map((columnName) => {
                const isFixed =
                  TABLE_DEFAULTS.COLUMNS.FIXED.includes(columnName);
                return (
                  <FilterTag
                    key={columnName}
                    label={
                      TABLE_DEFAULTS.COLUMNS.COLUMN_LABELS[columnName] ||
                      columnName
                    }
                    checked={columnVisibility[columnName]}
                    onChange={() => toggleColumn(columnName)}
                    disabled={isFixed}
                    variant="tag"
                  />
                );
              })}
            </FilterGroup>
          );
        }
      )}
    </DropdownButton>
  );
};

export default ColumnSelector;

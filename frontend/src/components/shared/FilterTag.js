import React from "react";
import { Chip } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { alpha } from "@mui/material/styles";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import CheckBoxOutlinedIcon from "@mui/icons-material/CheckBoxOutlined";

const FilterTag = ({
  label,
  checked,
  onChange,
  count,
  isHideFilter = false,
  totalCount = 0,
  variant = "tag",
  showCheckbox = false,
  stacked = false,
  sx = {},
}) => {
  const theme = useTheme();

  const formatCount = (count) => {
    if (count === undefined) return "";
    return `${count}`;
  };

  const mainLabel = label;
  const countLabel = count !== undefined ? formatCount(count) : "";

  return (
    <Chip
      icon={
        showCheckbox ? (
          checked ? (
            <CheckBoxOutlinedIcon
              sx={{
                fontSize: "1.1rem",
                ml: 0.8,
                color: checked
                  ? variant === "secondary"
                    ? "secondary.main"
                    : "primary.main"
                  : "text.secondary",
              }}
            />
          ) : (
            <CheckBoxOutlineBlankIcon
              sx={{
                fontSize: "1.1rem",
                ml: 0.8,
                color: "text.secondary",
              }}
            />
          )
        ) : null
      }
      label={
        <span>
          {mainLabel}
          {countLabel && (
            <>
              <span
                style={{
                  display: "inline-block",
                  width: "3px",
                  height: "3px",
                  borderRadius: "50%",
                  backgroundColor: "currentColor",
                  opacity: 0.2,
                  margin: "0 4px",
                  verticalAlign: "middle",
                }}
              />
              <span style={{ opacity: 0.5 }}>{countLabel}</span>
            </>
          )}
        </span>
      }
      onClick={onChange}
      variant="outlined"
      color={
        checked
          ? variant === "secondary"
            ? "secondary"
            : "primary"
          : "default"
      }
      size="small"
      data-checked={checked}
      sx={{
        height: "32px",
        fontWeight: 600,
        opacity: checked ? 1 : 0.8,
        borderRadius: "5px",
        borderWidth: "1px",
        borderStyle: "solid",
        cursor: "pointer",
        pl: showCheckbox ? 0.5 : 0,
        mr: 0.5,
        mb: 0.5,
        transition: "opacity 0.2s ease, border-color 0.2s ease",
        "& .MuiChip-label": {
          px: 0.75,
          pl: showCheckbox ? 0.6 : 0.75,
        },
        "& .MuiChip-icon": {
          mr: 0.5,
          pl: 0.2,
        },
        "&:hover": {
          opacity: 1,
          backgroundColor: checked
            ? alpha(
                theme.palette[variant === "secondary" ? "secondary" : "primary"]
                  .main,
                theme.palette.mode === "light" ? 0.08 : 0.16
              )
            : "action.hover",
          borderWidth: "1px",
        },
        backgroundColor: checked
          ? alpha(
              theme.palette[variant === "secondary" ? "secondary" : "primary"]
                .main,
              theme.palette.mode === "light" ? 0.08 : 0.16
            )
          : "background.paper",
        borderColor: checked
          ? variant === "secondary"
            ? "secondary.main"
            : "primary.main"
          : "divider",
        ...sx,
      }}
    />
  );
};

export default FilterTag;

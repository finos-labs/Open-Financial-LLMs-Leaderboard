import { alpha } from "@mui/material";

export const commonStyles = {
  // Tooltips
  tooltip: {
    sx: {
      bgcolor: "background.tooltip",
      "& .MuiTooltip-arrow": {
        color: "background.tooltip",
      },
      padding: "12px 16px",
      maxWidth: 300,
      fontSize: "0.875rem",
      lineHeight: 1.4,
    },
  },

  // Progress bars
  progressBar: {
    position: "absolute",
    left: -16,
    top: -8,
    height: "calc(100% + 16px)",
    opacity: (theme) => (theme.palette.mode === "light" ? 0.1 : 0.2),
    transition: "width 0.3s ease",
    zIndex: 0,
  },

  // Cell containers
  cellContainer: {
    display: "flex",
    alignItems: "center",
    height: "100%",
    width: "100%",
    position: "relative",
  },

  // Hover effects
  hoverEffect: (theme, isActive = false) => ({
    backgroundColor: isActive
      ? alpha(
          theme.palette.primary.main,
          theme.palette.mode === "light" ? 0.08 : 0.16
        )
      : theme.palette.action.hover,
    "& .MuiTypography-root": {
      color: isActive ? "primary.main" : "text.primary",
    },
    "& .MuiSvgIcon-root": {
      color: isActive ? "primary.main" : "text.primary",
    },
  }),

  // Filter groups
  filterGroup: {
    title: {
      mb: 1,
      fontSize: "0.8rem",
      fontWeight: 700,
      color: "text.primary",
      display: "flex",
      alignItems: "center",
      gap: 0.5,
    },
    container: {
      display: "flex",
      flexWrap: "wrap",
      gap: 0.5,
      alignItems: "center",
    },
  },

  // Option buttons (like in DisplayOptions)
  optionButton: {
    display: "flex",
    alignItems: "center",
    gap: 0.8,
    cursor: "pointer",
    padding: "4px 10px",
    borderRadius: 1,
    height: "32px",
    "& .MuiSvgIcon-root": {
      fontSize: "0.9rem",
    },
    "& .MuiTypography-root": {
      fontSize: "0.85rem",
    },
  },

  // Score indicators
  scoreIndicator: {
    dot: {
      width: 10,
      height: 10,
      borderRadius: "50%",
      marginLeft: -1,
    },
    bar: {
      position: "absolute",
      left: -16,
      top: -8,
      height: "calc(100% + 16px)",
      opacity: (theme) => (theme.palette.mode === "light" ? 0.1 : 0.2),
      transition: "width 0.3s ease",
    },
  },

  // Popover content
  popoverContent: {
    p: 3,
    width: 280,
    maxHeight: 400,
    overflowY: "auto",
  },
};

// Composant styles
export const componentStyles = {
  // Table header cell
  headerCell: {
    borderRight: (theme) =>
      `1px solid ${alpha(
        theme.palette.divider,
        theme.palette.mode === "dark" ? 0.05 : 0.1
      )}`,
    "&:last-child": {
      borderRight: "none",
    },
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    padding: "8px 16px",
    backgroundColor: (theme) => theme.palette.background.paper,
    position: "sticky !important",
    top: 0,
    zIndex: 10,
  },

  // Table cell
  tableCell: {
    borderRight: (theme) =>
      `1px solid ${alpha(
        theme.palette.divider,
        theme.palette.mode === "dark" ? 0.05 : 0.1
      )}`,
    "&:last-child": {
      borderRight: "none",
    },
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
  },
};

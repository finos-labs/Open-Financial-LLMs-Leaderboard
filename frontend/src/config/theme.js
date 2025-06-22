import { createTheme, alpha } from "@mui/material/styles";

const getDesignTokens = (mode) => ({
  typography: {
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"Segoe UI"',
      "Roboto",
      '"Helvetica Neue"',
      "Arial",
      "sans-serif",
    ].join(","),
    h1: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    h2: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    h3: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    h4: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    h5: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    h6: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    subtitle1: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
    subtitle2: {
      fontFamily: '"Source Sans Pro", sans-serif',
    },
  },
  palette: {
    mode,
    primary: {
      main: "#4F86C6",
      light: mode === "light" ? "#7BA7D7" : "#6B97D7",
      dark: mode === "light" ? "#2B5C94" : "#3B6CA4",
      50: mode === "light" ? alpha("#4F86C6", 0.05) : alpha("#4F86C6", 0.15),
      100: mode === "light" ? alpha("#4F86C6", 0.1) : alpha("#4F86C6", 0.2),
      200: mode === "light" ? alpha("#4F86C6", 0.2) : alpha("#4F86C6", 0.3),
      contrastText: "#fff",
    },
    background: {
      default: mode === "light" ? "#f8f9fa" : "#0a0a0a",
      paper: mode === "light" ? "#fff" : "#1a1a1a",
      subtle: mode === "light" ? "grey.100" : "grey.900",
      hover: mode === "light" ? "action.hover" : alpha("#fff", 0.08),
      tooltip: mode === "light" ? alpha("#212121", 0.9) : alpha("#fff", 0.9),
    },
    text: {
      primary: mode === "light" ? "rgba(0, 0, 0, 0.87)" : "#fff",
      secondary:
        mode === "light" ? "rgba(0, 0, 0, 0.6)" : "rgba(255, 255, 255, 0.7)",
      disabled:
        mode === "light" ? "rgba(0, 0, 0, 0.38)" : "rgba(255, 255, 255, 0.5)",
      hint:
        mode === "light" ? "rgba(0, 0, 0, 0.38)" : "rgba(255, 255, 255, 0.5)",
    },
    divider:
      mode === "light" ? "rgba(0, 0, 0, 0.12)" : "rgba(255, 255, 255, 0.12)",
    action: {
      active:
        mode === "light" ? "rgba(0, 0, 0, 0.54)" : "rgba(255, 255, 255, 0.7)",
      hover:
        mode === "light" ? "rgba(0, 0, 0, 0.04)" : "rgba(255, 255, 255, 0.08)",
      selected:
        mode === "light" ? "rgba(0, 0, 0, 0.08)" : "rgba(255, 255, 255, 0.16)",
      disabled:
        mode === "light" ? "rgba(0, 0, 0, 0.26)" : "rgba(255, 255, 255, 0.3)",
      disabledBackground:
        mode === "light" ? "rgba(0, 0, 0, 0.12)" : "rgba(255, 255, 255, 0.12)",
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        "html, body": {
          backgroundColor: "background.default",
          color: mode === "dark" ? "#fff" : "#000",
        },
        body: {
          "& *::-webkit-scrollbar": {
            width: 8,
            height: 8,
            backgroundColor: "transparent",
          },
          "& *::-webkit-scrollbar-thumb": {
            borderRadius: 8,
            backgroundColor:
              mode === "light" ? alpha("#000", 0.2) : alpha("#fff", 0.1),
            "&:hover": {
              backgroundColor:
                mode === "light" ? alpha("#000", 0.3) : alpha("#fff", 0.15),
            },
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: "none",
          boxShadow: "none",
          border: "1px solid",
          borderColor:
            mode === "light"
              ? "rgba(0, 0, 0, 0.12)!important"
              : "rgba(255, 255, 255, 0.25)!important",
        },
        rounded: {
          borderRadius: 12,
        },
      },
    },

    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: (theme) =>
            alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            ),
        },
        head: {
          backgroundColor: mode === "light" ? "grey.50" : "grey.900",
          color: "text.primary",
          fontWeight: 600,
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          backgroundColor: "transparent",
        },
      },
    },
    MuiTableContainer: {
      styleOverrides: {
        root: {
          backgroundColor: "background.paper",
          borderRadius: 8,
          border: "none",
          boxShadow: "none",
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          "& .MuiSlider-valueLabel": {
            backgroundColor: "background.paper",
            color: "text.primary",
            border: "1px solid",
            borderColor: "divider",
            boxShadow:
              mode === "light"
                ? "0px 2px 4px rgba(0, 0, 0, 0.1)"
                : "0px 2px 4px rgba(0, 0, 0, 0.3)",
          },
        },
        thumb: {
          "&:hover": {
            boxShadow: (theme) =>
              `0px 0px 0px 8px ${alpha(
                theme.palette.primary.main,
                mode === "light" ? 0.08 : 0.16
              )}`,
          },
          "&.Mui-active": {
            boxShadow: (theme) =>
              `0px 0px 0px 12px ${alpha(
                theme.palette.primary.main,
                mode === "light" ? 0.08 : 0.16
              )}`,
          },
        },
        track: {
          border: "none",
        },
        rail: {
          opacity: mode === "light" ? 0.38 : 0.3,
        },
        mark: {
          backgroundColor: mode === "light" ? "grey.400" : "grey.600",
        },
        markLabel: {
          color: "text.secondary",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 8,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
        outlinedInfo: {
          borderWidth: 2,
          fontWeight: 600,
          bgcolor: "info.100",
          borderColor: "info.400",
          color: "info.700",
          "& .MuiChip-label": {
            px: 1.2,
          },
          "&:hover": {
            bgcolor: "info.200",
          },
        },
        outlinedWarning: {
          borderWidth: 2,
          fontWeight: 600,
          bgcolor: "warning.100",
          borderColor: "warning.400",
          color: "warning.700",
          "& .MuiChip-label": {
            px: 1.2,
          },
          "&:hover": {
            bgcolor: "warning.200",
          },
        },
        outlinedSuccess: {
          borderWidth: 2,
          fontWeight: 600,
          bgcolor: "success.100",
          borderColor: "success.400",
          color: "success.700",
          "& .MuiChip-label": {
            px: 1.2,
          },
          "&:hover": {
            bgcolor: "success.200",
          },
        },
        outlinedError: {
          borderWidth: 2,
          fontWeight: 600,
          bgcolor: "error.100",
          borderColor: "error.400",
          color: "error.700",
          "& .MuiChip-label": {
            px: 1.2,
          },
          "&:hover": {
            bgcolor: "error.200",
          },
        },
        outlinedPrimary: {
          borderWidth: 2,
          fontWeight: 600,
          bgcolor: "primary.100",
          borderColor: "primary.400",
          color: "primary.700",
          "& .MuiChip-label": {
            px: 1.2,
          },
          "&:hover": {
            bgcolor: "primary.200",
          },
        },
        outlinedSecondary: {
          borderWidth: 2,
          fontWeight: 600,
          bgcolor: "secondary.100",
          borderColor: "secondary.400",
          color: "secondary.700",
          "& .MuiChip-label": {
            px: 1.2,
          },
          "&:hover": {
            bgcolor: "secondary.200",
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "8px",
          "&.MuiIconButton-sizeSmall": {
            padding: "4px",
            borderRadius: 6,
          },
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor:
            mode === "light" ? alpha("#212121", 0.9) : alpha("#424242", 0.9),
          color: "#fff",
          fontSize: "0.875rem",
          padding: "8px 12px",
          maxWidth: 400,
          borderRadius: 8,
          lineHeight: 1.4,
          border: "1px solid",
          borderColor:
            mode === "light" ? alpha("#fff", 0.1) : alpha("#fff", 0.05),
          boxShadow:
            mode === "light"
              ? "0 2px 8px rgba(0, 0, 0, 0.15)"
              : "0 2px 8px rgba(0, 0, 0, 0.5)",
          "& b": {
            fontWeight: 600,
            color: "inherit",
          },
          "& a": {
            color: mode === "light" ? "#90caf9" : "#64b5f6",
            textDecoration: "none",
            "&:hover": {
              textDecoration: "underline",
            },
          },
        },
        arrow: {
          color:
            mode === "light" ? alpha("#212121", 0.9) : alpha("#424242", 0.9),
          "&:before": {
            border: "1px solid",
            borderColor:
              mode === "light" ? alpha("#fff", 0.1) : alpha("#fff", 0.05),
          },
        },
      },
      defaultProps: {
        arrow: true,
        enterDelay: 400,
        leaveDelay: 200,
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          border: "none",
          borderBottom: "none",
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1240,
      xl: 1536,
    },
  },
});

const getTheme = (mode) => {
  const tokens = getDesignTokens(mode);
  return createTheme(tokens);
};

export default getTheme;

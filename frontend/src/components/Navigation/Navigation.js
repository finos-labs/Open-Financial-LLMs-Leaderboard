import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Box,
  Link as MuiLink,
  IconButton,
  Tooltip,
  ButtonBase,
  Typography,
} from "@mui/material";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import { alpha } from "@mui/material/styles";
import MenuIcon from "@mui/icons-material/Menu";
import { Menu, MenuItem, useMediaQuery, useTheme } from "@mui/material";

const Navigation = ({ onToggleTheme, mode }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [anchorEl, setAnchorEl] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [hasChanged, setHasChanged] = useState(false);

  const handleThemeToggle = () => {
    setHasChanged(true);
    onToggleTheme();
  };

  const iconStyle = {
    fontSize: "1.125rem",
    ...(hasChanged && {
      animation: "rotateIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      "@keyframes rotateIn": {
        "0%": {
          opacity: 0,
          transform:
            mode === "light"
              ? "rotate(-90deg) scale(0.8)"
              : "rotate(90deg) scale(0.8)",
        },
        "100%": {
          opacity: 1,
          transform: "rotate(0) scale(1)",
        },
      },
    }),
  };

  // Function to sync URL with parent HF page
  const syncUrlWithParent = (queryString, hash) => {
    // Check if we're in an HF Space iframe
    const isHFSpace = window.location !== window.parent.location;
    if (isHFSpace) {
      try {
        // Build complete URL with hash
        const fullPath = `${queryString}${hash ? "#" + hash : ""}`;
        window.parent.postMessage(
          {
            type: "urlUpdate",
            path: fullPath,
          },
          "https://huggingface.co"
        );
      } catch (e) {
        console.warn("Unable to sync URL with parent:", e);
      }
    }
  };

  const linkStyle = (isActive = false) => ({
    textDecoration: "none",
    color: isActive ? "text.primary" : "text.secondary",
    fontSize: "0.8125rem",
    opacity: isActive ? 1 : 0.8,
    display: "flex",
    alignItems: "center",
    gap: 0.5,
    paddingBottom: "2px",
    cursor: "pointer",
    position: "relative",
    "&:hover": {
      opacity: 1,
      color: "text.primary",
    },
    "&::after": isActive
      ? {
          content: '""',
          position: "absolute",
          bottom: "-4px",
          left: "0",
          width: "100%",
          height: "2px",
          backgroundColor: (theme) =>
            alpha(
              theme.palette.text.primary,
              theme.palette.mode === "dark" ? 0.3 : 0.2
            ),
          borderRadius: "2px",
        }
      : {},
  });

  const Separator = () => (
    <Box
      sx={(theme) => ({
        width: "4px",
        height: "4px",
        borderRadius: "100%",
        backgroundColor: alpha(
          theme.palette.text.primary,
          theme.palette.mode === "dark" ? 0.2 : 0.15
        ),
      })}
    />
  );

  const handleNavigation = (path) => (e) => {
    e.preventDefault();
    const searchString = searchParams.toString();
    const queryString = searchString ? `?${searchString}` : "";
    const newPath = `${path}${queryString}`;

    // Local navigation via React Router
    navigate(newPath);

    // If in HF Space, sync with parent
    if (window.location !== window.parent.location) {
      syncUrlWithParent(queryString, newPath);
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar
      position="static"
      sx={{
        backgroundColor: "transparent",
        boxShadow: "none",
        width: "100%",
      }}
    >
      <Toolbar sx={{ justifyContent: "center" }}>
        {isMobile ? (
          <Box
            sx={{
              display: "flex",
              width: "100%",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <IconButton
              onClick={handleMenuOpen}
              sx={{ color: "text.secondary" }}
            >
              <MenuIcon />
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              PaperProps={{
                elevation: 3,
                sx: {
                  mt: 1.5,
                  minWidth: 220,
                  borderRadius: "12px",
                  border: (theme) =>
                    `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                  backgroundColor: (theme) =>
                    theme.palette.mode === "dark"
                      ? alpha(theme.palette.background.paper, 0.8)
                      : theme.palette.background.paper,
                  backdropFilter: "blur(20px)",
                  "& .MuiList-root": {
                    py: 1,
                  },
                  "& .MuiMenuItem-root": {
                    px: 2,
                    py: 1,
                    fontSize: "0.8125rem",
                    color: "text.secondary",
                    transition: "all 0.2s ease-in-out",
                    position: "relative",
                    "&:hover": {
                      backgroundColor: (theme) =>
                        alpha(
                          theme.palette.text.primary,
                          theme.palette.mode === "dark" ? 0.1 : 0.06
                        ),
                      color: "text.primary",
                    },
                    "&.Mui-selected": {
                      backgroundColor: "transparent",
                      color: "text.primary",
                      "&::after": {
                        content: '""',
                        position: "absolute",
                        left: "8px",
                        width: "4px",
                        height: "100%",
                        top: "0",
                        backgroundColor: (theme) =>
                          alpha(
                            theme.palette.text.primary,
                            theme.palette.mode === "dark" ? 0.3 : 0.2
                          ),
                        borderRadius: "2px",
                      },
                      "&:hover": {
                        backgroundColor: (theme) =>
                          alpha(
                            theme.palette.text.primary,
                            theme.palette.mode === "dark" ? 0.1 : 0.06
                          ),
                      },
                    },
                  },
                },
              }}
              transformOrigin={{ horizontal: "left", vertical: "top" }}
              anchorOrigin={{ horizontal: "left", vertical: "bottom" }}
            >
              {/* Navigation Section */}
              <Box sx={{ px: 2, pb: 1.5, pt: 0.5 }}>
                <Typography variant="caption" sx={{ color: "text.disabled" }}>
                  Navigation
                </Typography>
              </Box>
              <MenuItem
                onClick={(e) => {
                  handleNavigation("/")(e);
                  handleMenuClose();
                }}
                selected={location.pathname === "/"}
              >
                Leaderboard
              </MenuItem>
              <MenuItem
                onClick={(e) => {
                  handleNavigation("/add")(e);
                  handleMenuClose();
                }}
                selected={location.pathname === "/add"}
              >
                Submit model
              </MenuItem>
              <MenuItem
                onClick={(e) => {
                  handleNavigation("/quote")(e);
                  handleMenuClose();
                }}
                selected={location.pathname === "/quote"}
              >
                Citations
              </MenuItem>

              {/* Separator */}
              <Box
                sx={{
                  my: 1,
                  borderTop: (theme) =>
                    `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                }}
              />

              {/* External Links Section */}
              <Box sx={{ px: 2, pb: 1.5 }}>
                <Typography variant="caption" sx={{ color: "text.disabled" }}>
                  External links
                </Typography>
              </Box>
            </Menu>

            <Tooltip
              title={
                mode === "light"
                  ? "Switch to dark mode"
                  : "Switch to light mode"
              }
            >
              <ButtonBase
                onClick={handleThemeToggle}
                sx={(theme) => ({
                  color: "text.secondary",
                  borderRadius: "100%",
                  padding: 0,
                  width: "36px",
                  height: "36px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    color: "text.primary",
                    backgroundColor: alpha(
                      theme.palette.text.primary,
                      theme.palette.mode === "dark" ? 0.1 : 0.06
                    ),
                  },
                  "&.MuiButtonBase-root": {
                    overflow: "hidden",
                  },
                  "& .MuiTouchRipple-root": {
                    color: alpha(theme.palette.text.primary, 0.3),
                  },
                })}
              >
                {mode === "light" ? (
                  <DarkModeOutlinedIcon sx={iconStyle} />
                ) : (
                  <LightModeOutlinedIcon sx={iconStyle} />
                )}
              </ButtonBase>
            </Tooltip>
          </Box>
        ) : (
          // Desktop version
          <Box
            sx={{
              display: "flex",
              gap: 2.5,
              alignItems: "center",
              padding: "0.5rem 0",
            }}
          >
            {/* Internal navigation */}
            <Box sx={{ display: "flex", gap: 2.5, alignItems: "center" }}>
              <Box
                onClick={handleNavigation("/")}
                sx={linkStyle(location.pathname === "/")}
              >
                Leaderboard
              </Box>
              <Box
                onClick={handleNavigation("/add")}
                sx={linkStyle(location.pathname === "/add")}
              >
                Submit model
              </Box>
              <Box
                onClick={handleNavigation("/quote")}
                sx={linkStyle(location.pathname === "/quote")}
              >
                Citations
              </Box>
            </Box>

            <Separator />


            {/* Dark mode toggle */}
            <Tooltip
              title={
                mode === "light"
                  ? "Switch to dark mode"
                  : "Switch to light mode"
              }
            >
              <ButtonBase
                onClick={handleThemeToggle}
                sx={(theme) => ({
                  color: "text.secondary",
                  borderRadius: "100%",
                  padding: 0,
                  width: "36px",
                  height: "36px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    color: "text.primary",
                    backgroundColor: alpha(
                      theme.palette.text.primary,
                      theme.palette.mode === "dark" ? 0.1 : 0.06
                    ),
                  },
                  "&.MuiButtonBase-root": {
                    overflow: "hidden",
                  },
                  "& .MuiTouchRipple-root": {
                    color: alpha(theme.palette.text.primary, 0.3),
                  },
                })}
              >
                {mode === "light" ? (
                  <DarkModeOutlinedIcon sx={iconStyle} />
                ) : (
                  <LightModeOutlinedIcon sx={iconStyle} />
                )}
              </ButtonBase>
            </Tooltip>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;

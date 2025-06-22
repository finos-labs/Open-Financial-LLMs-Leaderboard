import React, { useEffect, useState, useRef } from "react";
import { Box, Typography, Tooltip, useTheme } from "@mui/material";
import NetworkCheckIcon from "@mui/icons-material/NetworkCheck";
import MemoryIcon from "@mui/icons-material/Memory";
import SpeedIcon from "@mui/icons-material/Speed";
import GpuIcon from "@mui/icons-material/Memory";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

const getGPUStats = () => {
  try {
    const canvas = document.createElement("canvas");
    const gl =
      canvas.getContext("webgl") || canvas.getContext("experimental-webgl");

    if (!gl) {
      canvas.remove();
      return null;
    }

    // Try to get GPU info extensions
    const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");

    // Estimate GPU memory usage (very approximate)
    let usedMemoryEstimate = 0;

    try {
      // Create test texture
      const testTexture = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, testTexture);

      // Test size: 1024x1024 RGBA
      const testSize = 1024;
      const pixels = new Uint8Array(testSize * testSize * 4);
      gl.texImage2D(
        gl.TEXTURE_2D,
        0,
        gl.RGBA,
        testSize,
        testSize,
        0,
        gl.RGBA,
        gl.UNSIGNED_BYTE,
        pixels
      );

      // Estimate memory usage (very approximate)
      usedMemoryEstimate = (testSize * testSize * 4) / (1024 * 1024); // In MB

      gl.deleteTexture(testTexture);
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    } catch (e) {
      console.warn("GPU memory estimation failed:", e);
    } finally {
      // Cleanup WebGL resources
      const loseContext = gl.getExtension("WEBGL_lose_context");
      if (loseContext) loseContext.loseContext();
      gl.canvas.remove();
    }

    return {
      vendor: debugInfo
        ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL)
        : "Unknown",
      renderer: debugInfo
        ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
        : "Unknown",
      usedMemory: Math.round(usedMemoryEstimate),
    };
  } catch (e) {
    return null;
  }
};

const MetricBox = ({ icon, label, value, tooltip }) => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 1,
        padding: "2px 0",
        position: "relative",
      }}
    >
      {icon}
      <Typography
        component="div"
        variant="body2"
        sx={{
          fontSize: "0.8rem",
          fontWeight: 500,
          display: "flex",
          alignItems: "center",
          gap: 0.5,
          flex: 1,
          color: theme.palette.text.primary,
        }}
      >
        <Box
          component="span"
          sx={{
            opacity: 0.7,
            fontSize: "0.75rem",
            textTransform: "uppercase",
            color: theme.palette.text.secondary,
          }}
        >
          {label}
        </Box>
        <Box sx={{ flex: 1 }} />
        {React.isValidElement(value) ? value : <span>{value}</span>}
      </Typography>
      {tooltip && (
        <Box
          component="span"
          sx={{
            opacity: 0.5,
            display: "flex",
            alignItems: "center",
            cursor: "help",
            ml: 0.5,
            "&:hover": { opacity: 0.8 },
            color: theme.palette.text.secondary,
          }}
        >
          <Tooltip
            title={tooltip}
            arrow
            placement="top"
            componentsProps={{
              tooltip: {
                sx: {
                  bgcolor:
                    theme.palette.mode === "dark"
                      ? "rgba(0, 0, 0, 0.95)"
                      : "rgba(255, 255, 255, 0.95)",
                  color: theme.palette.text.primary,
                  padding: "8px 12px",
                  maxWidth: 250,
                  fontSize: "0.75rem",
                  position: "relative",
                  top: "-10px",
                  border: "1px solid",
                  borderColor:
                    theme.palette.mode === "dark"
                      ? "rgba(255, 255, 255, 0.1)"
                      : "rgba(0, 0, 0, 0.1)",
                  "& .MuiTooltip-arrow": {
                    color:
                      theme.palette.mode === "dark"
                        ? "rgba(0, 0, 0, 0.95)"
                        : "rgba(255, 255, 255, 0.95)",
                  },
                },
              },
              popper: {
                sx: {
                  zIndex: 10000,
                },
              },
            }}
          >
            <InfoOutlinedIcon sx={{ fontSize: "0.9rem" }} />
          </Tooltip>
        </Box>
      )}
    </Box>
  );
};

const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
};

const PerformanceMonitor = () => {
  const theme = useTheme();

  const [stats, setStats] = useState({
    fps: 0,
    memory: {
      usedJSHeapSize: 0,
      totalJSHeapSize: 0,
    },
    renders: 0,
    network: {
      transferSize: 0,
      decodedBodySize: 0,
      compressionRatio: 0,
    },
    gpu: getGPUStats(),
    fcp: null,
  });
  const [isVisible, setIsVisible] = useState(
    process.env.NODE_ENV === "development"
  );
  const renderCountRef = useRef(0);
  const originalCreateElementRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ignore if user is in an input field
      if (
        event.target.tagName === "INPUT" ||
        event.target.tagName === "TEXTAREA"
      ) {
        return;
      }

      if (event.key === "p" || event.key === "P") {
        setIsVisible((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    let animationFrameId;

    const getNetworkStats = () => {
      const resources = performance.getEntriesByType("resource");
      const navigation = performance.getEntriesByType("navigation")[0];

      let totalTransferSize = navigation ? navigation.transferSize : 0;
      let totalDecodedSize = navigation ? navigation.decodedBodySize : 0;

      resources.forEach((resource) => {
        totalTransferSize += resource.transferSize || 0;
        totalDecodedSize += resource.decodedBodySize || 0;
      });

      const compressionRatio = totalDecodedSize
        ? Math.round((1 - totalTransferSize / totalDecodedSize) * 100)
        : 0;

      return {
        transferSize: Math.round(totalTransferSize / 1024),
        decodedBodySize: Math.round(totalDecodedSize / 1024),
        compressionRatio,
      };
    };

    // Save original function
    originalCreateElementRef.current = React.createElement;

    // Replace createElement
    React.createElement = function (...args) {
      renderCountRef.current++;
      return originalCreateElementRef.current.apply(this, args);
    };

    const updateStats = () => {
      frameCount++;
      const now = performance.now();
      const delta = now - lastTime;

      if (delta >= 1000) {
        const fps = Math.round((frameCount * 1000) / delta);

        const memory = window.performance?.memory
          ? {
              usedJSHeapSize: Math.round(
                window.performance.memory.usedJSHeapSize / 1048576
              ),
              totalJSHeapSize: Math.round(
                window.performance.memory.totalJSHeapSize / 1048576
              ),
            }
          : null;

        const network = getNetworkStats();
        const gpu = getGPUStats();

        setStats((prev) => ({
          ...prev,
          fps,
          memory: memory || prev.memory,
          renders: renderCountRef.current,
          network,
          gpu,
        }));

        frameCount = 0;
        lastTime = now;
      }

      animationFrameId = requestAnimationFrame(updateStats);
    };

    updateStats();

    return () => {
      cancelAnimationFrame(animationFrameId);
      // Restore original function
      if (originalCreateElementRef.current) {
        React.createElement = originalCreateElementRef.current;
      }
      // Clean up counters
      renderCountRef.current = 0;
      delete window.__REACT_RENDERS__;
    };
  }, []);

  useEffect(() => {
    // Add FCP observer
    if (window.PerformanceObserver) {
      try {
        const fcpObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          if (entries.length > 0) {
            const fcp = entries[0].startTime;
            setStats((prev) => ({
              ...prev,
              fcp,
            }));
          }
        });

        fcpObserver.observe({ entryTypes: ["paint"] });
        return () => fcpObserver.disconnect();
      } catch (e) {
        console.warn("FCP observation failed:", e);
      }
    }
  }, []);

  const getFpsColor = (fps) => {
    if (fps >= 55) return "#4CAF50";
    if (fps >= 30) return "#FFC107";
    return "#F44336";
  };

  return isVisible ? (
    <Box
      sx={{
        position: "fixed",
        top: 16,
        left: 16,
        zIndex: 9999,
        backgroundColor: theme.palette.background.paper,
        borderRadius: "6px",
        color: "white",
        fontFamily: "monospace",
        userSelect: "none",
        padding: "6px 10px",
        minWidth: "180px",
        border: "1px solid",
        borderColor: theme.palette.divider,
        display: "flex",
        flexDirection: "column",
        gap: 0.25,
      }}
    >
      <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
        <Typography
          variant="body2"
          sx={{
            fontSize: "0.85rem",
            fontWeight: 600,
            color: theme.palette.text.primary,
            borderBottom: `1px solid ${theme.palette.divider}`,
            pb: 0.5,
          }}
        >
          Performances{" "}
          <span style={{ float: "right", opacity: 0.3 }}>dev only</span>
        </Typography>
      </Box>
      {/* Performance Metrics */}
      <Box sx={{ display: "flex", flexDirection: "column", gap: 0.25 }}>
        <MetricBox
          icon={
            <SpeedIcon
              sx={{ fontSize: "1.1rem", color: getFpsColor(stats.fps) }}
            />
          }
          label="FPS"
          value={
            <Typography
              sx={{
                fontSize: "0.9rem",
                fontWeight: 600,
                color: getFpsColor(stats.fps),
              }}
            >
              {stats.fps}
            </Typography>
          }
          tooltip="Frames Per Second - Indicates how smooth the UI is running"
        />

        {stats.fcp !== null && (
          <MetricBox
            icon={
              <SpeedIcon
                sx={{ fontSize: "1.1rem", color: theme.palette.text.secondary }}
              />
            }
            label="FCP"
            value={
              <Typography
                sx={{
                  fontSize: "0.9rem",
                  fontWeight: 600,
                  color: theme.palette.text.primary,
                }}
              >
                {Math.round(stats.fcp)}ms
              </Typography>
            }
            tooltip="First Contentful Paint - Time until first content is rendered"
          />
        )}
        <MetricBox
          icon={
            <Box
              sx={{
                width: "0.9rem",
                height: "0.9rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.7rem",
              }}
            >
              ⚛️
            </Box>
          }
          label="React"
          value={
            <Box
              component="span"
              sx={{ display: "flex", gap: 0.5, alignItems: "center" }}
            >
              <span>{formatNumber(stats.renders)}</span>
              <span style={{ opacity: 0.5 }}> cycles</span>
            </Box>
          }
          tooltip="Total number of React render cycles"
        />
      </Box>

      {/* Memory Metrics */}
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 0.25,
          mt: 0.5,
          pt: 0.5,
          borderTop: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        {window.performance?.memory && (
          <MetricBox
            icon={<MemoryIcon sx={{ fontSize: "0.9rem", color: "#64B5F6" }} />}
            label="Mem"
            value={
              <Box
                component="span"
                sx={{ display: "flex", gap: 0.5, alignItems: "center" }}
              >
                <span>{stats.memory.usedJSHeapSize}</span>
                <span style={{ opacity: 0.5 }}> / </span>
                <span>{stats.memory.totalJSHeapSize}</span>
                <span style={{ opacity: 0.5 }}> MB</span>
              </Box>
            }
            tooltip="JavaScript heap memory usage (Used / Total)"
          />
        )}
        {stats.gpu && (
          <MetricBox
            icon={<GpuIcon sx={{ fontSize: "0.9rem", color: "#FFB74D" }} />}
            label="GPU"
            value={
              <Box
                component="span"
                sx={{ display: "flex", gap: 0.5, alignItems: "center" }}
              >
                <span>{stats.gpu.usedMemory}</span>
                <span style={{ opacity: 0.5 }}> MB</span>
              </Box>
            }
            tooltip="Estimated GPU memory usage"
          />
        )}
      </Box>

      {/* Network Metrics */}
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 0.25,
          mt: 0.5,
          pt: 0.5,
          borderTop: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <MetricBox
          icon={
            <NetworkCheckIcon sx={{ fontSize: "0.9rem", color: "#81C784" }} />
          }
          label="Net"
          value={
            <Box
              component="span"
              sx={{ display: "flex", gap: 0.5, alignItems: "center" }}
            >
              <span>{stats.network.transferSize}</span>
              <span style={{ opacity: 0.5 }}> KB</span>
            </Box>
          }
          tooltip="Network data transferred"
        />
        <MetricBox
          icon={<Box sx={{ width: "0.9rem", opacity: 0.5 }} />}
          label="Size"
          value={
            <Box
              component="span"
              sx={{ display: "flex", gap: 0.5, alignItems: "center" }}
            >
              <span>{formatNumber(stats.network.decodedBodySize)}</span>
              <span style={{ opacity: 0.5 }}> KB</span>
              <Box
                component="span"
                sx={{
                  color:
                    stats.network.compressionRatio > 0 ? "#81C784" : "inherit",
                  fontSize: "0.7rem",
                  opacity: 0.8,
                  ml: 1,
                }}
              >
                (-{stats.network.compressionRatio}%)
              </Box>
            </Box>
          }
          tooltip="Total decoded size and compression ratio"
        />
        <Box
          sx={{
            borderTop: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Typography
            variant="body2"
            sx={{
              fontSize: "0.7rem",
              pt: 1,
              pb: 0.5,
              opacity: 0.5,
              color: theme.palette.text.primary,
            }}
          >
            Press "P" to show/hide
          </Typography>
        </Box>
      </Box>
    </Box>
  ) : null;
};

export default React.memo(PerformanceMonitor);

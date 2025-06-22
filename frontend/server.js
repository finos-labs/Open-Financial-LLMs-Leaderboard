const express = require("express");
const cors = require("cors");
const compression = require("compression");
const path = require("path");
const serveStatic = require("serve-static");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app = express();
const port = process.env.PORT || 7860;
const apiPort = process.env.INTERNAL_API_PORT || 7861;

// Enable CORS for all routes
app.use(cors());

// Enable GZIP compression
app.use(compression());

// Proxy all API requests to the Python backend
app.use(
  "/api",
  createProxyMiddleware({
    target: `http://127.0.0.1:${apiPort}`,
    changeOrigin: true,
    onError: (err, req, res) => {
      console.error("Proxy Error:", err);
      res.status(500).json({ error: "Proxy Error", details: err.message });
    },
  })
);

// Serve static files from the build directory
app.use(
  express.static(path.join(__dirname, "build"), {
    // Don't cache HTML files
    setHeaders: (res, path) => {
      if (path.endsWith(".html")) {
        res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");
        res.setHeader("Pragma", "no-cache");
        res.setHeader("Expires", "0");
      } else {
        // Cache other static resources for 1 year
        res.setHeader("Cache-Control", "public, max-age=31536000");
      }
    },
  })
);

// Middleware to preserve URL parameters
app.use((req, res, next) => {
  // Don't interfere with API requests
  if (req.url.startsWith("/api")) {
    return next();
  }

  // Preserve original URL parameters
  req.originalUrl = req.url;
  next();
});

// Handle all other routes by serving index.html
app.get("*", (req, res) => {
  // Don't interfere with API requests
  if (req.url.startsWith("/api")) {
    return next();
  }

  // Headers for client-side routing
  res.set({
    "Cache-Control": "no-cache, no-store, must-revalidate",
    Pragma: "no-cache",
    Expires: "0",
  });

  // Send index.html for all other routes
  res.sendFile(path.join(__dirname, "build", "index.html"));
});

app.listen(port, "0.0.0.0", () => {
  console.log(
    `Frontend server is running on port ${port} in ${
      process.env.NODE_ENV || "development"
    } mode`
  );
  console.log(`API proxy target: http://127.0.0.1:${apiPort}`);
});

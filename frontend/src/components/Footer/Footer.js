import React from "react";
import { Box, Typography, Link, Stack } from "@mui/material";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <Box
      component="footer"
      sx={{
        width: "100%",
        py: 4,
        textAlign: "center",
        backgroundColor: "background.paper",
        borderTop: "1px solid",
        borderColor: "divider",
      }}
    >
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          © {currentYear} The Fin AI - Open Financial LLM Leaderboard
        </Typography>
        <Stack direction="row" spacing={2} justifyContent="center">
          <Link
            href="https://thefin.ai"
            target="_blank"
            rel="noopener noreferrer"
            color="inherit"
            underline="hover"
          >
            Home
          </Link>
          <Link
            href="https://github.com/thefin-ai"
            target="_blank"
            rel="noopener noreferrer"
            color="inherit"
            underline="hover"
          >
            GitHub
          </Link>
          <Link
            href="https://thefin.ai/docs"
            target="_blank"
            rel="noopener noreferrer"
            color="inherit"
            underline="hover"
          >
            Documentation
          </Link>
        </Stack>
      </Stack>
    </Box>
  );
};

export default Footer;

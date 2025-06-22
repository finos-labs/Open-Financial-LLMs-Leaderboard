import React from "react";
import { Box, Typography } from "@mui/material";

const PageHeader = ({ title, subtitle }) => {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        mb: 6,
        mt: 6,
        gap: 2,
      }}
    >
      <Typography fontWeight="bold" variant="h3" component="h1">
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="h6" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </Box>
  );
};

export default PageHeader;

import React from "react";
import { Box, Tooltip, Portal, Backdrop } from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

const InfoIconWithTooltip = ({ tooltip, iconProps = {}, sx = {} }) => {
  const [open, setOpen] = React.useState(false);

  return (
    <>
      <Tooltip
        title={tooltip}
        arrow
        placement="top"
        open={open}
        onOpen={() => setOpen(true)}
        onClose={() => setOpen(false)}
        componentsProps={{
          tooltip: {
            sx: {
              bgcolor: "rgba(33, 33, 33, 0.95)",
              padding: "12px 16px",
              maxWidth: "none !important",
              width: "auto",
              minWidth: "200px",
              fontSize: "0.875rem",
              lineHeight: 1.5,
              position: "relative",
              zIndex: 1501,
              "& .MuiTooltip-arrow": {
                color: "rgba(33, 33, 33, 0.95)",
              },
            },
          },
          popper: {
            sx: {
              zIndex: 1501,
              maxWidth: "min(600px, 90vw) !important",
              '&[data-popper-placement*="bottom"] .MuiTooltip-tooltip': {
                marginTop: "10px",
              },
              '&[data-popper-placement*="top"] .MuiTooltip-tooltip': {
                marginBottom: "10px",
              },
            },
          },
        }}
      >
        <Box
          component="span"
          sx={{
            opacity: 0.5,
            display: "flex",
            alignItems: "center",
            cursor: "help",
            "&:hover": { opacity: 0.8 },
            position: "relative",
            zIndex: open ? 1502 : "auto",
            ...sx,
          }}
        >
          <InfoOutlinedIcon
            sx={{
              fontSize: "1rem",
              ...iconProps.sx,
            }}
            {...iconProps}
          />
        </Box>
      </Tooltip>
      {open && (
        <Portal>
          <Backdrop
            open={true}
            sx={{
              zIndex: 1500,
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              transition: "opacity 0.2s ease",
              pointerEvents: "none",
            }}
          />
        </Portal>
      )}
    </>
  );
};

export default InfoIconWithTooltip;

import React, { useState } from "react";
import { Box, Popover, Portal, Typography, Skeleton } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { commonStyles } from "../../styles/common";

const DropdownButton = ({
  label,
  icon: Icon,
  closeIcon: CloseIcon,
  hasChanges = false,
  children,
  defaultWidth = 340,
  paperProps = {},
  buttonSx = {},
  loading = false,
}) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (event) => {
    if (event) {
      event.stopPropagation();
    }
    setAnchorEl(null);
  };

  if (loading) {
    return (
      <Skeleton
        variant="rounded"
        sx={{
          width: label === "table options" ? 120 : 140,
          height: 32,
          transform: "none",
          borderRadius: 1,
        }}
      />
    );
  }

  return (
    <Box>
      <Box
        onClick={handleClick}
        sx={{
          ...commonStyles.optionButton,
          "&:hover": commonStyles.hoverEffect(theme, hasChanges),
          ...buttonSx,
        }}
      >
        {Boolean(anchorEl) && CloseIcon ? (
          <CloseIcon
            sx={{
              fontSize: "1rem",
              color: hasChanges ? "primary.main" : "grey.600",
            }}
          />
        ) : (
          <Icon
            sx={{
              fontSize: "1rem",
              color: hasChanges ? "primary.main" : "grey.600",
            }}
          />
        )}
        <Typography
          variant="caption"
          sx={{
            color: hasChanges ? "primary.main" : "grey.600",
            fontSize: "0.875rem",
            userSelect: "none",
            lineHeight: 1,
          }}
        >
          {label}
        </Typography>
      </Box>
      <Portal>
        <Popover
          open={Boolean(anchorEl)}
          anchorEl={anchorEl}
          onClose={handleClose}
          disableRestoreFocus
          disableAutoFocus
          PaperProps={{
            sx: {
              p: 3,
              maxHeight: "470px",
              overflowY: "auto",
              width: defaultWidth,
              backgroundColor: "background.paper",
              border: "1px solid",
              borderColor: (theme) =>
                theme.palette.mode === "light"
                  ? "rgba(0, 0, 0, 0.12)"
                  : "rgba(255, 255, 255, 0.12)",
              borderRadius: 1,
              position: "relative",
              boxShadow: (theme) =>
                `0px 4px 20px ${
                  theme.palette.mode === "light"
                    ? "rgba(0, 0, 0, 0.1)"
                    : "rgba(255, 255, 255, 0.1)"
                }`,
              ...paperProps.sx,
            },
            ...paperProps,
          }}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "right",
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
          slotProps={{
            backdrop: {
              sx: {
                backgroundColor: "transparent",
              },
            },
          }}
        >
          {children}
        </Popover>
      </Portal>
    </Box>
  );
};

export default DropdownButton;

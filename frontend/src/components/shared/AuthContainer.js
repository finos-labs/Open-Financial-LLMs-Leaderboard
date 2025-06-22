import React from "react";
import {
  Box,
  Typography,
  Button,
  Chip,
  Stack,
  Paper,
  CircularProgress,
} from "@mui/material";
import HFLogo from "../Logo/HFLogo";
import { useAuth } from "../../hooks/useAuth";
import LogoutIcon from "@mui/icons-material/Logout";
import { useNavigate } from "react-router-dom";

function AuthContainer({ actionText = "DO_ACTION" }) {
  const { isAuthenticated, user, login, logout, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    if (isAuthenticated && logout) {
      logout();
      navigate("/", { replace: true });
      window.location.reload();
    }
  };

  if (loading) {
    return (
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 4,
          border: "1px solid",
          borderColor: "grey.300",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
        }}
      >
        <CircularProgress size={24} />
      </Paper>
    );
  }

  if (!isAuthenticated) {
    return (
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 4,
          border: "1px solid",
          borderColor: "grey.300",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
        }}
      >
        <Typography variant="h6" align="center">
          Login to {actionText}
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center">
          You need to be logged in with your Hugging Face account to{" "}
          {actionText.toLowerCase()}
        </Typography>
        <Button
          variant="contained"
          onClick={login}
          startIcon={
            <Box
              sx={{
                width: 20,
                height: 20,
                display: "flex",
                alignItems: "center",
              }}
            >
              <HFLogo />
            </Box>
          }
          sx={{
            textTransform: "none",
            fontWeight: 600,
            py: 1,
            px: 2,
          }}
        >
          Sign in with Hugging Face
        </Button>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={0}
      sx={{ p: 2, border: "1px solid", borderColor: "grey.300", mb: 4 }}
    >
      <Stack
        direction="row"
        spacing={2}
        alignItems="center"
        justifyContent="space-between"
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="body1">
            Connected as <strong>{user?.username}</strong>
          </Typography>
          <Chip
            label={`Ready to ${actionText}`}
            color="success"
            size="small"
            variant="outlined"
          />
        </Stack>
        <Button
          variant="contained"
          onClick={handleLogout}
          endIcon={<LogoutIcon />}
          color="primary"
          sx={{
            minWidth: 120,
            height: 36,
            textTransform: "none",
            fontSize: "0.9375rem",
          }}
        >
          Logout
        </Button>
      </Stack>
    </Paper>
  );
}

export default AuthContainer;

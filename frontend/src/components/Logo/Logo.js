import React from "react";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { Box } from "@mui/material";
import HFLogo from "./HFLogo";
import { useLeaderboard } from "../../pages/LeaderboardPage/components/Leaderboard/context/LeaderboardContext";

const Logo = ({ height = "40px" }) => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const { actions } = useLeaderboard();

  const handleReset = () => {
    // Reset all leaderboard state first
    actions.resetAll();

    // Then clean URL in one go
    if (
      location.pathname !== "/" ||
      searchParams.toString() !== "" ||
      location.hash !== ""
    ) {
      window.history.replaceState(null, "", "/");
      navigate("/", { replace: true, state: { skipUrlSync: true } });
      setSearchParams({}, { replace: true, state: { skipUrlSync: true } });
    }
  };

  return (
    <Box
      onClick={handleReset}
      sx={{
        height,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
        transition: "opacity 0.2s ease",
        "&:hover": {
          opacity: 0.8,
        },
      }}
    >
        <Box
          component="img"
          src="/logofinai.png"
          alt="FinAI Logo"
          sx={{
            height: "80%",
            mx: 2,
            maxHeight: 80,
          }}
        />
        <Box
          component="img"
          src="/securefinailab.png"
          alt="SecureFinAI Logo"
          sx={{
            height: "80%",
            mx: 2,
            maxHeight: 80,
          }}
        />
        <Box
          component="img"
          src="/nactemlogo.png"
          alt="NACTEM Logo"
          sx={{
            height: "60%",
            mx: 2,
            maxHeight: 60,
          }}
        />
        <Box
          component="img"
          src="/archimedeslogo.png"
          alt="Archimedes Logo"
          sx={{
            height: "60%",
            mx: 2,
            maxHeight: 60,
          }}
        />
        <Box
          component="img"
          src="/airclogo.png"
          alt="AIRC Logo"
          sx={{
            height: "80%",
            mx: 2,
            maxHeight: 80,
          }}
        />
    </Box>
  );
};

export default Logo;

import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  List,
  ListItem,
  CircularProgress,
  Chip,
  Divider,
  IconButton,
  Stack,
  Link,
} from "@mui/material";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import PersonIcon from "@mui/icons-material/Person";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import HowToVoteIcon from "@mui/icons-material/HowToVote";
import { useAuth } from "../../hooks/useAuth";
import PageHeader from "../../components/shared/PageHeader";
import AuthContainer from "../../components/shared/AuthContainer";
import { alpha } from "@mui/material/styles";
import CheckIcon from "@mui/icons-material/Check";

const NoModelsToVote = () => (
  <Box
    sx={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      py: 8,
      textAlign: "center",
    }}
  >
    <HowToVoteIcon
      sx={{
        fontSize: 100,
        color: "grey.300",
        mb: 3,
      }}
    />
    <Typography
      variant="h4"
      component="h2"
      sx={{
        fontWeight: "bold",
        color: "grey.700",
        mb: 2,
      }}
    >
      No Models to Vote
    </Typography>
    <Typography
      variant="body1"
      sx={{
        color: "grey.600",
        maxWidth: 450,
        mx: "auto",
      }}
    >
      There are currently no models waiting for votes.
      <br />
      Check back later!
    </Typography>
  </Box>
);

function VoteModelPage() {
  const { isAuthenticated, user, loading } = useAuth();
  const [pendingModels, setPendingModels] = useState([]);
  const [loadingModels, setLoadingModels] = useState(true);
  const [error, setError] = useState(null);
  const [userVotes, setUserVotes] = useState(new Set());

  const formatWaitTime = (submissionTime) => {
    if (!submissionTime) return "N/A";

    const now = new Date();
    const submitted = new Date(submissionTime);
    const diffInHours = Math.floor((now - submitted) / (1000 * 60 * 60));

    // Less than 24 hours: show in hours
    if (diffInHours < 24) {
      return `${diffInHours}h`;
    }

    // Less than 7 days: show in days
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) {
      return `${diffInDays}d`;
    }

    // More than 7 days: show in weeks
    const diffInWeeks = Math.floor(diffInDays / 7);
    return `${diffInWeeks}w`;
  };

  // Fetch user's votes
  useEffect(() => {
    const fetchUserVotes = async () => {
      if (!isAuthenticated || !user) return;

      try {
        // Récupérer les votes du localStorage
        const localVotes = JSON.parse(
          localStorage.getItem(`votes_${user.username}`) || "[]"
        );
        const localVotesSet = new Set(localVotes);

        // Récupérer les votes du serveur
        const response = await fetch(`/api/votes/user/${user.username}`);
        if (!response.ok) {
          throw new Error("Failed to fetch user votes");
        }
        const data = await response.json();

        // Fusionner les votes du serveur avec les votes locaux
        const votedModels = new Set([
          ...data.map((vote) => vote.model),
          ...localVotesSet,
        ]);
        setUserVotes(votedModels);
      } catch (err) {
        console.error("Error fetching user votes:", err);
      }
    };

    fetchUserVotes();
  }, [isAuthenticated, user]);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch("/api/models/pending");
        if (!response.ok) {
          throw new Error("Failed to fetch pending models");
        }
        const data = await response.json();

        // Fetch votes for each model
        const modelsWithVotes = await Promise.all(
          data.map(async (model) => {
            const [provider, modelName] = model.name.split("/");
            const votesResponse = await fetch(
              `/api/votes/model/${provider}/${modelName}`
            );
            const votesData = await votesResponse.json();

            // Calculate total vote score from votes_by_revision
            const totalScore = Object.values(
              votesData.votes_by_revision || {}
            ).reduce((a, b) => a + b, 0);

            // Calculate wait time based on submission_time from model data
            const waitTimeDisplay = formatWaitTime(model.submission_time);

            return {
              ...model,
              votes: totalScore,
              votes_by_revision: votesData.votes_by_revision,
              wait_time: waitTimeDisplay,
              hasVoted: userVotes.has(model.name),
            };
          })
        );

        // Sort models by vote score in descending order
        const sortedModels = modelsWithVotes.sort((a, b) => b.votes - a.votes);

        setPendingModels(sortedModels);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, [userVotes]);

  const handleVote = async (modelName) => {
    if (!isAuthenticated) return;

    try {
      // Disable the button immediately by adding the model to userVotes
      setUserVotes((prev) => {
        const newSet = new Set([...prev, modelName]);
        // Sauvegarder dans le localStorage
        if (user) {
          const localVotes = JSON.parse(
            localStorage.getItem(`votes_${user.username}`) || "[]"
          );
          if (!localVotes.includes(modelName)) {
            localVotes.push(modelName);
            localStorage.setItem(
              `votes_${user.username}`,
              JSON.stringify(localVotes)
            );
          }
        }
        return newSet;
      });

      // Split modelName into provider and model
      const [provider, model] = modelName.split("/");

      const response = await fetch(
        `/api/votes/${modelName}?vote_type=up&user_id=${user.username}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        // Si le vote échoue, on retire le vote du localStorage et du state
        setUserVotes((prev) => {
          const newSet = new Set(prev);
          newSet.delete(modelName);
          if (user) {
            const localVotes = JSON.parse(
              localStorage.getItem(`votes_${user.username}`) || "[]"
            );
            const updatedVotes = localVotes.filter(
              (vote) => vote !== modelName
            );
            localStorage.setItem(
              `votes_${user.username}`,
              JSON.stringify(updatedVotes)
            );
          }
          return newSet;
        });
        throw new Error("Failed to submit vote");
      }

      // Refresh votes for this model
      const votesResponse = await fetch(
        `/api/votes/model/${provider}/${model}`
      );
      const votesData = await votesResponse.json();

      // Calculate total vote score from votes_by_revision
      const totalScore = Object.values(
        votesData.votes_by_revision || {}
      ).reduce((a, b) => a + b, 0);

      // Update model and resort the list
      setPendingModels((models) => {
        const updatedModels = models.map((model) =>
          model.name === modelName
            ? {
                ...model,
                votes: totalScore,
                votes_by_revision: votesData.votes_by_revision,
              }
            : model
        );
        return updatedModels.sort((a, b) => b.votes - a.votes);
      });
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%", maxWidth: 1200, margin: "0 auto", padding: 4 }}>
      <PageHeader
        title="Vote for the Next Models"
        subtitle={
          <>
            Help us <span style={{ fontWeight: 600 }}>prioritize</span> which
            models to evaluate next
          </>
        }
      />

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Auth Status */}
      {/* <Box sx={{ mb: 3 }}>
        {isAuthenticated ? (
          <Paper
            elevation={0}
            sx={{ p: 2, border: "1px solid", borderColor: "grey.300" }}
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
                  label="Ready to vote"
                  color="success"
                  size="small"
                  variant="outlined"
                />
              </Stack>
              <LogoutButton />
            </Stack>
          </Paper>
        ) : (
          <Paper
            elevation={0}
            sx={{
              p: 3,
              border: "1px solid",
              borderColor: "grey.300",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
            }}
          >
            <Typography variant="h6" align="center">
              Login to Vote
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              You need to be logged in with your Hugging Face account to vote
              for models
            </Typography>
            <AuthBlock />
          </Paper>
        )}
      </Box> */}
      <AuthContainer actionText="vote for models" />

      {/* Models List */}
      <Paper
        elevation={0}
        sx={{
          border: "1px solid",
          borderColor: "grey.300",
          borderRadius: 1,
          overflow: "hidden",
          minHeight: 400,
        }}
      >
        {/* Header - Always visible */}
        <Box
          sx={{
            px: 3,
            py: 2,
            borderBottom: "1px solid",
            borderColor: (theme) =>
              theme.palette.mode === "dark"
                ? alpha(theme.palette.divider, 0.1)
                : "grey.200",
            bgcolor: (theme) =>
              theme.palette.mode === "dark"
                ? alpha(theme.palette.background.paper, 0.5)
                : "grey.50",
          }}
        >
          <Typography
            variant="h6"
            sx={{ fontWeight: 600, color: "text.primary" }}
          >
            Models Pending Evaluation
          </Typography>
        </Box>

        {/* Table Header */}
        <Box
          sx={{
            px: 3,
            py: 1.5,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
            display: "grid",
            gridTemplateColumns: "1fr 200px 160px",
            gap: 3,
            alignItems: "center",
          }}
        >
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Model
            </Typography>
          </Box>
          <Box sx={{ textAlign: "right" }}>
            <Typography variant="subtitle2" color="text.secondary">
              Votes
            </Typography>
          </Box>
          <Box sx={{ textAlign: "right" }}>
            <Typography variant="subtitle2" color="text.secondary">
              Priority
            </Typography>
          </Box>
        </Box>

        {/* Content */}
        {loadingModels ? (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "200px",
              width: "100%",
              bgcolor: "background.paper",
            }}
          >
            <CircularProgress />
          </Box>
        ) : pendingModels.length === 0 && !loadingModels ? (
          <NoModelsToVote />
        ) : (
          <List sx={{ p: 0, bgcolor: "background.paper" }}>
            {pendingModels.map((model, index) => {
              const isTopThree = index < 3;
              return (
                <React.Fragment key={model.name}>
                  {index > 0 && <Divider />}
                  <ListItem
                    sx={{
                      py: 2.5,
                      px: 3,
                      display: "grid",
                      gridTemplateColumns: "1fr 200px 160px",
                      gap: 3,
                      alignItems: "center",
                      position: "relative",
                      "&:hover": {
                        bgcolor: "action.hover",
                      },
                    }}
                  >
                    {/* Left side - Model info */}
                    <Box>
                      <Stack spacing={1}>
                        {/* Model name and link */}
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Link
                            href={`https://huggingface.co/${model.name}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{
                              textDecoration: "none",
                              color: "primary.main",
                              fontWeight: 500,
                              "&:hover": {
                                textDecoration: "underline",
                              },
                            }}
                          >
                            {model.name}
                          </Link>
                          <IconButton
                            size="small"
                            href={`https://huggingface.co/${model.name}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{
                              ml: 0.5,
                              p: 0.5,
                              color: "action.active",
                              "&:hover": {
                                color: "primary.main",
                              },
                            }}
                          >
                            <OpenInNewIcon sx={{ fontSize: "1rem" }} />
                          </IconButton>
                        </Stack>
                        {/* Metadata row */}
                        <Stack direction="row" spacing={2} alignItems="center">
                          <Stack
                            direction="row"
                            spacing={0.5}
                            alignItems="center"
                          >
                            <AccessTimeIcon
                              sx={{
                                fontSize: "0.875rem",
                                color: "text.secondary",
                              }}
                            />
                            <Typography variant="body2" color="text.secondary">
                              {model.wait_time}
                            </Typography>
                          </Stack>
                          <Stack
                            direction="row"
                            spacing={0.5}
                            alignItems="center"
                          >
                            <PersonIcon
                              sx={{
                                fontSize: "0.875rem",
                                color: "text.secondary",
                              }}
                            />
                            <Typography variant="body2" color="text.secondary">
                              {model.submitter}
                            </Typography>
                          </Stack>
                        </Stack>
                      </Stack>
                    </Box>

                    {/* Vote Column */}
                    <Box sx={{ textAlign: "right" }}>
                      <Stack
                        direction="row"
                        spacing={2.5}
                        justifyContent="flex-end"
                        alignItems="center"
                      >
                        <Stack
                          alignItems="center"
                          sx={{
                            minWidth: "90px",
                          }}
                        >
                          <Typography
                            variant="h4"
                            component="div"
                            sx={{
                              fontWeight: 700,
                              lineHeight: 1,
                              fontSize: "2rem",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                            }}
                          >
                            <Typography
                              component="span"
                              sx={{
                                fontSize: "1.5rem",
                                fontWeight: 600,
                                color: "primary.main",
                                lineHeight: 1,
                                mr: 0.5,
                                mt: "-2px",
                              }}
                            >
                              +
                            </Typography>
                            <Typography
                              component="span"
                              sx={{
                                color:
                                  model.votes === 0
                                    ? "text.primary"
                                    : "primary.main",
                                fontWeight: 700,
                                lineHeight: 1,
                              }}
                            >
                              {model.votes > 999 ? "999" : model.votes}
                            </Typography>
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: "text.secondary",
                              fontWeight: 500,
                              mt: 0.5,
                              textTransform: "uppercase",
                              letterSpacing: "0.05em",
                              fontSize: "0.75rem",
                            }}
                          >
                            votes
                          </Typography>
                        </Stack>
                        <Button
                          variant={model.hasVoted ? "contained" : "outlined"}
                          size="large"
                          onClick={() => handleVote(model.name)}
                          disabled={!isAuthenticated || model.hasVoted}
                          color="primary"
                          sx={{
                            minWidth: "100px",
                            height: "40px",
                            textTransform: "none",
                            fontWeight: 600,
                            fontSize: "0.95rem",
                            ...(model.hasVoted
                              ? {
                                  bgcolor: "primary.main",
                                  "&:hover": {
                                    bgcolor: "primary.dark",
                                  },
                                  "&.Mui-disabled": {
                                    bgcolor: "primary.main",
                                    color: "white",
                                    opacity: 0.7,
                                  },
                                }
                              : {
                                  borderWidth: 2,
                                  "&:hover": {
                                    borderWidth: 2,
                                  },
                                }),
                          }}
                        >
                          {model.hasVoted ? (
                            <Stack
                              direction="row"
                              spacing={0.5}
                              alignItems="center"
                            >
                              <CheckIcon sx={{ fontSize: "1.2rem" }} />
                              <span>Voted</span>
                            </Stack>
                          ) : (
                            "Vote"
                          )}
                        </Button>
                      </Stack>
                    </Box>

                    {/* Priority Column */}
                    <Box sx={{ textAlign: "right" }}>
                      <Chip
                        label={
                          <Stack
                            direction="row"
                            spacing={0.5}
                            alignItems="center"
                          >
                            {isTopThree && (
                              <Typography
                                variant="body2"
                                sx={{
                                  fontWeight: 600,
                                  color: isTopThree
                                    ? "primary.main"
                                    : "text.primary",
                                  letterSpacing: "0.02em",
                                }}
                              >
                                HIGH
                              </Typography>
                            )}
                            <Typography
                              variant="body2"
                              sx={{
                                fontWeight: 600,
                                color: isTopThree
                                  ? "primary.main"
                                  : "text.secondary",
                                letterSpacing: "0.02em",
                              }}
                            >
                              #{index + 1}
                            </Typography>
                          </Stack>
                        }
                        size="medium"
                        variant={isTopThree ? "filled" : "outlined"}
                        sx={{
                          height: 36,
                          minWidth: "100px",
                          bgcolor: isTopThree
                            ? (theme) => alpha(theme.palette.primary.main, 0.1)
                            : "transparent",
                          borderColor: isTopThree ? "primary.main" : "grey.300",
                          borderWidth: 2,
                          "& .MuiChip-label": {
                            px: 2,
                            fontSize: "0.95rem",
                          },
                        }}
                      />
                    </Box>
                  </ListItem>
                </React.Fragment>
              );
            })}
          </List>
        )}
      </Paper>
    </Box>
  );
}

export default VoteModelPage;

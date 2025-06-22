import React from "react";
import { Box, CircularProgress } from "@mui/material";
import { useAuth } from "../../hooks/useAuth";
import PageHeader from "../../components/shared/PageHeader";
import EvaluationQueues from "./components/EvaluationQueues/EvaluationQueues";
import ModelSubmissionForm from "./components/ModelSubmissionForm/ModelSubmissionForm";
import SubmissionGuide from "./components/SubmissionGuide/SubmissionGuide";

function AddModelPage() {
  const { isAuthenticated, loading, user } = useAuth();

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
        title="Submit a Model for Evaluation"
        subtitle={
          <>
            Add <span style={{ fontWeight: 600 }}>your</span> model to the Open
            LLM Leaderboard
          </>
        }
      />

      <SubmissionGuide />

      <ModelSubmissionForm user={user} isAuthenticated={isAuthenticated} />

      <EvaluationQueues defaultExpanded={false} />
    </Box>
  );
}

export default AddModelPage;

import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Box, Paper, Typography, Button, Stack, Collapse } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

const DocLink = ({ href, children }) => (
  <Button
    variant="text"
    size="small"
    href={href}
    target="_blank"
    sx={{
      fontFamily: "monospace",
      textTransform: "none",
      color: "primary.main",
      fontSize: "0.875rem",
      p: 0,
      minWidth: "auto",
      justifyContent: "flex-start",
      "&:hover": {
        color: "primary.dark",
        backgroundColor: "transparent",
        textDecoration: "underline",
      },
    }}
  >
    {children} →
  </Button>
);

const StepNumber = ({ number }) => (
  <Box
    sx={{
      width: 32,
      height: 32,
      borderRadius: "50%",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      border: "1px solid",
      borderColor: "primary.main",
      color: "primary.main",
      fontSize: "0.875rem",
      fontWeight: 600,
      flexShrink: 0,
      bgcolor: "transparent",
    }}
  >
    {number}
  </Box>
);

const TUTORIAL_STEPS = [
  {
    title: "Model Information",
    content: (
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          Your model should be <strong>public</strong> on the Hub and follow the{" "}
          <strong>username/model-id</strong> format (e.g.
          mistralai/Mistral-7B-v0.1). Specify the <strong>revision</strong>{" "}
          (commit hash or branch) and <strong>model type</strong>.
        </Typography>
        <DocLink href="https://huggingface.co/docs/hub/models-uploading">
          Model uploading guide
        </DocLink>
      </Stack>
    ),
  },
  {
    title: "Technical Details",
    content: (
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          Make sure your model can be <strong>loaded locally</strong> before
          submitting:
        </Typography>
        <Box
          sx={{
            p: 2,
            bgcolor: (theme) =>
              theme.palette.mode === "dark" ? "grey.50" : "grey.900",
            borderRadius: 1,
            "& pre": {
              m: 0,
              p: 0,
              fontFamily: "monospace",
              fontSize: "0.875rem",
              color: (theme) =>
                theme.palette.mode === "dark" ? "grey.900" : "grey.50",
            },
          }}
        >
          <pre>
            {`from transformers import AutoConfig, AutoModel, AutoTokenizer

config = AutoConfig.from_pretrained("your-username/your-model", revision="main")
model = AutoModel.from_pretrained("your-username/your-model", revision="main")
tokenizer = AutoTokenizer.from_pretrained("your-username/your-model", revision="main")`}
          </pre>
        </Box>
        <DocLink href="https://huggingface.co/docs/transformers/installation">
          Transformers documentation
        </DocLink>
      </Stack>
    ),
  },
  {
    title: "License Requirements",
    content: (
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          A <strong>license tag</strong> is required.{" "}
          <strong>Open licenses</strong> (Apache, MIT, etc) are strongly
          recommended.
        </Typography>
        <DocLink href="https://huggingface.co/docs/hub/repositories-licenses">
          About model licenses
        </DocLink>
      </Stack>
    ),
  },
  {
    title: "Model Card Requirements",
    content: (
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          Your model card must include: <strong>architecture</strong>,{" "}
          <strong>training details</strong>,{" "}
          <strong>dataset information</strong>, intended use, limitations, and{" "}
          <strong>performance metrics</strong>.
        </Typography>
        <DocLink href="https://huggingface.co/docs/hub/model-cards">
          Model cards guide
        </DocLink>
      </Stack>
    ),
  },
  {
    title: "Final Checklist",
    content: (
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          Ensure your model is <strong>public</strong>, uses{" "}
          <strong>safetensors</strong> format, has a{" "}
          <strong>license tag</strong>, and <strong>loads correctly</strong>{" "}
          with the provided code.
        </Typography>
        <DocLink href="https://huggingface.co/docs/hub/repositories-getting-started">
          Sharing best practices
        </DocLink>
      </Stack>
    ),
  },
];

function SubmissionGuide() {
  const location = useLocation();
  const navigate = useNavigate();

  // Initialize state directly with URL value
  const initialExpanded = !new URLSearchParams(location.search).get("guide");
  const [expanded, setExpanded] = useState(initialExpanded);

  // Sync expanded state with URL changes after initial render
  useEffect(() => {
    const guideOpen = !new URLSearchParams(location.search).get("guide");
    if (guideOpen !== expanded) {
      setExpanded(guideOpen);
    }
  }, [location.search, expanded]);

  const handleAccordionChange = () => {
    const newExpanded = !expanded;
    setExpanded(newExpanded);
    const params = new URLSearchParams(location.search);
    if (newExpanded) {
      params.delete("guide");
    } else {
      params.set("guide", "closed");
    }
    navigate({ search: params.toString() }, { replace: true });
  };

  return (
    <Paper
      elevation={0}
      sx={{
        mb: 3,
        borderRadius: "8px !important",
        border: "1px solid",
        borderColor: (theme) =>
          theme.palette.mode === "dark" ? "grey.800" : "grey.200",
        overflow: "hidden",
      }}
    >
      <Box
        onClick={handleAccordionChange}
        sx={{
          p: 2,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          cursor: "pointer",
          bgcolor: (theme) =>
            theme.palette.mode === "dark" ? "grey.900" : "grey.50",
          borderBottom: "1px solid",
          borderColor: (theme) =>
            expanded
              ? theme.palette.mode === "dark"
                ? "grey.800"
                : "grey.200"
              : "transparent",
        }}
      >
        <Typography
          variant="h6"
          sx={{ fontWeight: 600, color: "text.primary" }}
        >
          Submission Guide
        </Typography>
        <ExpandMoreIcon
          sx={{
            transform: expanded ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.3s",
          }}
        />
      </Box>
      <Collapse in={expanded} appear={false}>
        <Box sx={{ py: 4 }}>
          <Stack spacing={4}>
            {TUTORIAL_STEPS.map((step, index) => (
              <Box key={step.title}>
                <Stack spacing={3}>
                  <Stack
                    direction="row"
                    spacing={2}
                    alignItems="center"
                    sx={{ px: 4 }}
                  >
                    <StepNumber number={index + 1} />
                    <Typography
                      variant="subtitle1"
                      sx={{
                        fontWeight: 600,
                        color: "text.primary",
                        letterSpacing: "-0.01em",
                      }}
                    >
                      {step.title}
                    </Typography>
                  </Stack>
                  <Box sx={{ px: 4, pl: 7 }}>{step.content}</Box>
                </Stack>
                {index < TUTORIAL_STEPS.length - 1 && (
                  <Box
                    sx={{
                      mt: 4,
                      borderTop: "1px solid",
                      borderColor: (theme) =>
                        theme.palette.mode === "dark" ? "grey.800" : "grey.100",
                    }}
                  />
                )}
              </Box>
            ))}
          </Stack>
        </Box>
      </Collapse>
    </Paper>
  );
}

export default SubmissionGuide;

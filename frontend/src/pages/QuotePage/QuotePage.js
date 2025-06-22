import React from "react";
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  Link,
} from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import PageHeader from "../../components/shared/PageHeader";

const citations = [
  {
    title: "Plutus: Benchmarking Large Language Models in Low-Resource Greek Finance",
    authors:
      "Xueqing Peng et al.",
    citation: `@misc{peng2025plutusbenchmarkinglargelanguage,
      title={Plutus: Benchmarking Large Language Models in Low-Resource Greek Finance}, 
      author={Xueqing Peng and Triantafillos Papadopoulos and Efstathia Soufleri and Polydoros Giannouris and Ruoyu Xiang and Yan Wang and Lingfei Qian and Jimin Huang and Qianqian Xie and Sophia Ananiadou},
      year={2025},
      eprint={2502.18772},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.18772}, 
}`,
    type: "main",
    url: "https://arxiv.org/abs/2502.18772",
  },
  {
    title: "Evaluation Framework",
    authors: "Leo Gao et al.",
    citation: `@software{eval-harness,
  author       = {Gao, Leo and Tow, Jonathan and Biderman, Stella and Black, Sid and DiPofi, Anthony and Foster, Charles and Golding, Laurence and Hsu, Jeffrey and McDonell, Kyle and Muennighoff, Niklas and Phang, Jason and Reynolds, Laria and Tang, Eric and Thite, Anish and Wang, Ben and Wang, Kevin and Zou, Andy},
  title        = {A framework for few-shot language model evaluation},
  month        = sep,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v0.0.1},
  doi          = {10.5281/zenodo.5371628},
  url          = {https://doi.org/10.5281/zenodo.5371628},
}`,
    url: "https://doi.org/10.5281/zenodo.5371628",
  },
];

const priorWork = [
  {
    title: "The financial narrative summarisation shared task (FNS 2023)",
    authors:
      "Elias Zavitsanos et al.",
    citation: `@inproceedings{zavitsanos2023financial,
  title={The financial narrative summarisation shared task (FNS 2023)},
  author={Zavitsanos, Elias and Kosmopoulos, Aris and Giannakopoulos, George and Litvak, Marina and Carbajo-Coronado, Blanca and Moreno-Sandoval, Antonio and El-Haj, Mo},
  booktitle={2023 IEEE International Conference on Big Data (BigData)},
  pages={2890--2896},
  year={2023},
  organization={IEEE}
}`,
    type: "main",
    url: "https://ieeexplore.ieee.org/document/10386228",
  },
  {
    title: "MultiFin: A dataset for multilingual financial NLP",
    authors:
      "Rasmus J{\o}rgensen et al.",
    citation: `@inproceedings{jorgensen2023multifin,
  title={MultiFin: A dataset for multilingual financial NLP},
  author={J{\o}rgensen, Rasmus and Brandt, Oliver and Hartmann, Mareike and Dai, Xiang and Igel, Christian and Elliott, Desmond},
  booktitle={Findings of the Association for Computational Linguistics: EACL 2023},
  pages={894--909},
  year={2023}
}`,
    type: "main",
    url: "https://aclanthology.org/2023.findings-eacl.66/",
  },
//   {
//     title: "PIXIU: a large language model, instruction data and evaluation benchmark for finance",
//     authors:
//       "Qianqian Xie et al.",
//     citation: `@inproceedings{10.5555/3666122.3667576,
// author = {Xie, Qianqian and Han, Weiguang and Zhang, Xiao and Lai, Yanzhao and Peng, Min and Lopez-Lira, Alejandro and Huang, Jimin},
// title = {PIXIU: a large language model, instruction data and evaluation benchmark for finance},
// year = {2024},
// publisher = {Curran Associates Inc.},
// address = {Red Hook, NY, USA},
// abstract = {Although large language models (LLMs) have shown great performance in natural language processing (NLP) in the financial domain, there are no publicly available financially tailored LLMs, instruction tuning datasets, and evaluation benchmarks, which is critical for continually pushing forward the open-source development of financial artificial intelligence (AI). This paper introduces PIXIU, a comprehensive framework including the first financial LLM based on fine-tuning LLaMA with instruction data, the first instruction data with 128K data samples to support the fine-tuning, and an evaluation benchmark with 8 tasks and 15 datasets. We first construct the large-scale multi-task instruction data considering a variety of financial tasks, financial document types, and financial data modalities. We then propose a financial LLM called FinMA by fine-tuning LLaMA with the constructed dataset to be able to follow instructions for various financial tasks. To support the evaluation of financial LLMs, we propose a standardized benchmark that covers a set of critical financial tasks, including six financial NLP tasks and two financial prediction tasks. With this benchmark, we conduct a detailed analysis of FinMA and several existing LLMs, uncovering their strengths and weaknesses in handling critical financial tasks. The model, datasets, benchmark, and experimental results are open-sourced to facilitate future research in financial AI.},
// booktitle = {Proceedings of the 37th International Conference on Neural Information Processing Systems},
// articleno = {1454},
// numpages = {16},
// location = {New Orleans, LA, USA},
// series = {NIPS '23}
// }`,
//     type: "main",
//   },
];

const benchmarks = [
  {
    title: "FinBen: A Holistic Financial Benchmark for Large Language Models",
    authors: "Qianqian Xie et al.",
    citation: `@article{xie2024finben,
  title={The finben: An holistic financial benchmark for large language models},
  author={Xie, Qianqian and Han, Weiguang and Chen, Zhengyu and Xiang, Ruoyu and Zhang, Xiao and He, Yueru and Xiao, Mengxi and Li, Dong and Dai, Yongfu and Feng, Duanyu and others},
  journal={arXiv preprint arXiv:2402.12659},
  year={2024}
}`,
    type: "main",
    url: "https://arxiv.org/abs/2402.12659",
  },
//   {
//     title: "MultiFin: Instruction-Following Evaluation",
//     authors: "Zhou et al.",
//     citation: `@inproceedings{jorgensen-etal-2023-multifin,
//     title = "{M}ulti{F}in: A Dataset for Multilingual Financial {NLP}",
//     author = "J{\o}rgensen, Rasmus  and
//       Brandt, Oliver  and
//       Hartmann, Mareike  and
//       Dai, Xiang  and
//       Igel, Christian  and
//       Elliott, Desmond",
//     editor = "Vlachos, Andreas  and
//       Augenstein, Isabelle",
//     booktitle = "Findings of the Association for Computational Linguistics: EACL 2023",
//     month = may,
//     year = "2023",
//     address = "Dubrovnik, Croatia",
//     publisher = "Association for Computational Linguistics",
//     url = "https://aclanthology.org/2023.findings-eacl.66/",
//     doi = "10.18653/v1/2023.findings-eacl.66",
//     pages = "894--909",
//     abstract = "Financial information is generated and distributed across the world, resulting in a vast amount of domain-specific multilingual data. Multilingual models adapted to the financial domain would ease deployment when an organization needs to work with multiple languages on a regular basis. For the development and evaluation of such models, there is a need for multilingual financial language processing datasets. We describe MultiFin {--} a publicly available financial dataset consisting of real-world article headlines covering 15 languages across different writing systems and language families. The dataset consists of hierarchical label structure providing two classification tasks: multi-label and multi-class. We develop our annotation schema based on a real-world application and annotate our dataset using both {\textquoteleft}label by native-speaker' and {\textquoteleft}translate-then-label' approaches. The evaluation of several popular multilingual models, e.g., mBERT, XLM-R, and mT5, show that although decent accuracy can be achieved in high-resource languages, there is substantial room for improvement in low-resource languages."
// }`,
//     url: "https://aclanthology.org/2023.findings-eacl.66/#:~:text=We%20describe%20MultiFin%20%2D%2D%20a,%2Dlabel%20and%20multi%2Dclass.",
//   },
];

const CitationBlock = ({ citation, title, authors, url, type }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(citation);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        border: "1px solid",
        borderColor: "grey.200",
        backgroundColor: "transparent",
        borderRadius: 2,
        position: "relative",
      }}
    >
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 0.5 }}>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {authors}
        </Typography>
        {url && (
          <Link
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            sx={{ fontSize: "0.875rem", display: "block", mt: 0.5 }}
          >
            View paper →
          </Link>
        )}
      </Box>
      <Box
        sx={{
          backgroundColor: "grey.900",
          borderRadius: 1,
          p: 2,
          position: "relative",
        }}
      >
        <Tooltip title="Copy citation" placement="top">
          <IconButton
            onClick={handleCopy}
            size="small"
            sx={{
              position: "absolute",
              top: 8,
              right: 8,
              color: "grey.500",
              "&:hover": {
                color: "grey.300",
              },
            }}
          >
            <ContentCopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Box
          component="pre"
          sx={{
            margin: 0,
            color: "#fff",
            fontSize: "0.875rem",
            fontFamily: "monospace",
            whiteSpace: "pre",
            textAlign: "left",
            overflow: "auto",
          }}
        >
          <code>{citation}</code>
        </Box>
      </Box>
    </Paper>
  );
};

function QuotePage() {
  return (
    <Box sx={{ width: "100%", maxWidth: 1200, margin: "0 auto", padding: 4 }}>
      <PageHeader
        title="Citation Information"
        subtitle="How to cite the Open Greek Financial LLM Leaderboard in your work"
      />

      <Alert severity="info" sx={{ mb: 4 }}>
        <Typography variant="body2">
          The citations below include both the leaderboard itself and the
          individual benchmarks used in our evaluation suite.
        </Typography>
      </Alert>

      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" sx={{ mb: 3 }}>
          Leaderboard
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {citations.map((citation, index) => (
            <CitationBlock key={index} {...citation} />
          ))}
        </Box>
      </Box>

      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" sx={{ mb: 3 }}>
          Benchmarks
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {benchmarks.map((benchmark, index) => (
            <CitationBlock key={index} {...benchmark} />
          ))}
        </Box>
      </Box>

      <Box>
        <Typography variant="h5" sx={{ mb: 3 }}>
          Prior Work
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {priorWork.map((citation, index) => (
            <CitationBlock key={index} {...citation} />
          ))}
        </Box>
      </Box>
    </Box>
  );
}

export default QuotePage;

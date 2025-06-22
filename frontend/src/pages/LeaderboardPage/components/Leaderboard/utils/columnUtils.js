import React from "react";
import { Box, Typography, Link, Tooltip, IconButton } from "@mui/material";
import { getModelTypeIcon } from "../constants/modelTypes";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import RemoveIcon from "@mui/icons-material/Remove";
import PushPinIcon from "@mui/icons-material/PushPin";
import PushPinOutlinedIcon from "@mui/icons-material/PushPinOutlined";
import { TABLE_DEFAULTS, HIGHLIGHT_COLORS } from "../constants/defaults";
import { looksLikeRegex, extractTextSearch } from "./searchUtils";
import { commonStyles } from "../styles/common";
import { typeColumnSort } from "../components/Table/hooks/useSorting";
import {
  COLUMN_TOOLTIPS,
  getTooltipStyle,
  TABLE_TOOLTIPS,
} from "../constants/tooltips";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { alpha } from "@mui/material/styles";
import InfoIconWithTooltip from "../../../../../components/shared/InfoIconWithTooltip";

const DatabaseIcon = () => (
  <svg
    className="mr-1.5 text-gray-400 group-hover:text-red-500"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    focusable="false"
    role="img"
    width="1.4em"
    height="1.4em"
    preserveAspectRatio="xMidYMid meet"
    viewBox="0 0 25 25"
  >
    <ellipse
      cx="12.5"
      cy="5"
      fill="currentColor"
      fillOpacity="0.25"
      rx="7.5"
      ry="2"
    ></ellipse>
    <path
      d="M12.5 15C16.6421 15 20 14.1046 20 13V20C20 21.1046 16.6421 22 12.5 22C8.35786 22 5 21.1046 5 20V13C5 14.1046 8.35786 15 12.5 15Z"
      fill="currentColor"
      opacity="0.5"
    ></path>
    <path
      d="M12.5 7C16.6421 7 20 6.10457 20 5V11.5C20 12.6046 16.6421 13.5 12.5 13.5C8.35786 13.5 5 12.6046 5 11.5V5C5 6.10457 8.35786 7 12.5 7Z"
      fill="currentColor"
      opacity="0.5"
    ></path>
    <path
      d="M5.23628 12C5.08204 12.1598 5 12.8273 5 13C5 14.1046 8.35786 15 12.5 15C16.6421 15 20 14.1046 20 13C20 12.8273 19.918 12.1598 19.7637 12C18.9311 12.8626 15.9947 13.5 12.5 13.5C9.0053 13.5 6.06886 12.8626 5.23628 12Z"
      fill="currentColor"
    ></path>
  </svg>
);

const HighlightedText = ({ text, searchValue }) => {
  if (!searchValue) return text;

  const searches = searchValue
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);
  let result = text;
  let fragments = [{ text: result, isMatch: false }];

  searches.forEach((search, searchIndex) => {
    if (!search) return;

    try {
      let regex;
      if (looksLikeRegex(search)) {
        regex = new RegExp(search, "gi");
      } else {
        regex = new RegExp(search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      }

      const newFragments = [];
      fragments.forEach((fragment) => {
        if (fragment.isMatch) {
          newFragments.push(fragment);
          return;
        }

        const parts = fragment.text.split(regex);
        const matches = fragment.text.match(regex);

        if (!matches) {
          newFragments.push(fragment);
          return;
        }

        parts.forEach((part, i) => {
          if (part) newFragments.push({ text: part, isMatch: false });
          if (i < parts.length - 1) {
            newFragments.push({
              text: matches[i],
              isMatch: true,
              colorIndex: searchIndex % HIGHLIGHT_COLORS.length,
            });
          }
        });
      });

      fragments = newFragments;
    } catch (e) {
      console.warn("Invalid regex:", search);
    }
  });

  return (
    <>
      {fragments.map((fragment, i) =>
        fragment.isMatch ? (
          <Box
            key={i}
            component="span"
            sx={{
              backgroundColor: HIGHLIGHT_COLORS[fragment.colorIndex],
              color: (theme) =>
                theme.palette.getContrastText(
                  HIGHLIGHT_COLORS[fragment.colorIndex]
                ),
              fontWeight: 500,
              px: 0.5,
              py: "2px",
              borderRadius: "3px",
              mx: "1px",
              overflow: "visible",
              display: "inline-block",
            }}
          >
            {fragment.text}
          </Box>
        ) : (
          <React.Fragment key={i}>{fragment.text}</React.Fragment>
        )
      )}
    </>
  );
};

const MEDAL_STYLES = {
  1: {
    color: "#B58A1B",
    background: "linear-gradient(135deg, #FFF7E0 0%, #FFD700 100%)",
    borderColor: "rgba(212, 160, 23, 0.35)",
    shadowColor: "rgba(212, 160, 23, 0.8)",
  },
  2: {
    color: "#667380",
    background: "linear-gradient(135deg, #FFFFFF 0%, #D8E3ED 100%)",
    borderColor: "rgba(124, 139, 153, 0.35)",
    shadowColor: "rgba(124, 139, 153, 0.8)",
  },
  3: {
    color: "#B85C2F",
    background: "linear-gradient(135deg, #FDF0E9 0%, #FFBC8C 100%)",
    borderColor: "rgba(204, 108, 61, 0.35)",
    shadowColor: "rgba(204, 108, 61, 0.8)",
  },
};

const getMedalStyle = (rank) => {
  if (rank <= 3) {
    const medalStyle = MEDAL_STYLES[rank];
    return {
      color: medalStyle.color,
      fontWeight: 900,
      fontStretch: "150%",
      fontFamily: '"Inter", -apple-system, sans-serif',
      width: "24px",
      height: "24px",
      background: medalStyle.background,
      border: "1px solid",
      borderColor: medalStyle.borderColor,
      borderRadius: "50%",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "0.95rem",
      lineHeight: 1,
      padding: 0,
      boxShadow: `1px 1px 0 ${medalStyle.shadowColor}`,
      position: "relative",
    };
  }
  return {
    color: "inherit",
    fontWeight: rank <= 10 ? 600 : 400,
  };
};

const getRankStyle = (rank) => getMedalStyle(rank);

const RankIndicator = ({ rank, previousRank, mode }) => {
  const rankChange = previousRank ? previousRank - rank : 0;

  const RankChangeIndicator = ({ change }) => {
    if (!change || mode === "dynamic") return null;

    const getChangeColor = (change) => {
      if (change > 0) return "success.main";
      if (change < 0) return "error.main";
      return "grey.500";
    };

    const getChangeIcon = (change) => {
      if (change > 0) return <TrendingUpIcon sx={{ fontSize: "1rem" }} />;
      if (change < 0) return <TrendingDownIcon sx={{ fontSize: "1rem" }} />;
      return <RemoveIcon sx={{ fontSize: "1rem" }} />;
    };

    return (
      <Tooltip
        title={`${Math.abs(change)} position${
          Math.abs(change) > 1 ? "s" : ""
        } ${change > 0 ? "up" : "down"}`}
        arrow
        placement="right"
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            color: getChangeColor(change),
            ml: 0.5,
            fontSize: "0.75rem",
          }}
        >
          {getChangeIcon(change)}
        </Box>
      </Tooltip>
    );
  };

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
      }}
    >
      <Typography
        sx={{
          ...getRankStyle(rank),
          display: "flex",
          alignItems: "center",
          lineHeight: 1,
          position: "relative",
        }}
      >
        {rank <= 3 ? (
          <>
            <Box component="span" sx={{ position: "relative", zIndex: 1 }}>
              {rank}
            </Box>
            <RankChangeIndicator change={rankChange} />
          </>
        ) : (
          <>
            <Box component="span" sx={{ position: "relative", zIndex: 1 }}>
              {rank}
            </Box>
            <RankChangeIndicator change={rankChange} />
          </>
        )}
      </Typography>
    </Box>
  );
};

const getDetailsUrl = (modelName) => {
  const formattedName = modelName.replace("/", "__");
  return `https://huggingface.co/datasets/TheFinAI/lm-eval-results-private`;
};

const HeaderLabel = ({ label, tooltip, className, isSorted }) => (
  <Tooltip
    title={label}
    arrow
    placement="top"
    enterDelay={1000}
    componentsProps={getTooltipStyle}
  >
    <Typography
      className={className}
      sx={{
        fontWeight: 600,
        color: isSorted ? "primary.main" : "grey.700",
        flex: 1,
        transition: "max-width 0.2s ease",
        maxWidth: "100%",
        ...(label === "Rank" || label === "Type"
          ? {
              overflow: "visible",
              whiteSpace: "normal",
              textOverflow: "clip",
              textAlign: "center",
            }
          : {
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }),
        "@media (hover: hover)": {
          ".MuiTableCell-root:hover &": {
            maxWidth: tooltip ? "calc(100% - 48px)" : "100%",
          },
        },
      }}
    >
      {label}
    </Typography>
  </Tooltip>
);

const InfoIcon = ({ tooltip }) => (
  <Box
    component="span"
    sx={{
      opacity: 0.5,
      display: "flex",
      alignItems: "center",
      ml: 0.5,
    }}
  >
    <InfoIconWithTooltip tooltip={tooltip} />
  </Box>
);

const createHeaderCell = (label, tooltip) => (header) =>
  (
    <Box
      className="header-content"
      sx={{
        display: "flex",
        alignItems: "center",
        width: "100%",
        position: "relative",
      }}
    >
      <HeaderLabel
        label={label}
        tooltip={tooltip}
        className="header-label"
        isSorted={header?.column?.getIsSorted()}
      />

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 0.5,
          ml: "auto",
          flexShrink: 0,
        }}
      >
        {tooltip && <InfoIcon tooltip={tooltip} />}
      </Box>
    </Box>
  );

const createModelHeader =
  (totalModels, officialProvidersCount = 0, isOfficialProviderActive = false) =>
  ({ table }) => {
    return (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <Typography
            sx={{
              fontWeight: 600,
              color: "grey.700",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            Model
          </Typography>
        </Box>
      </Box>
    );
  };

const BooleanValue = ({ value }) => {
  if (value === null || value === undefined)
    return <Typography variant="body2">-</Typography>;

  return (
    <Box
      sx={(theme) => ({
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "4px",
        px: 1,
        py: 0.5,
        backgroundColor: value
          ? theme.palette.mode === "dark"
            ? alpha(theme.palette.success.main, 0.1)
            : alpha(theme.palette.success.main, 0.1)
          : theme.palette.mode === "dark"
          ? alpha(theme.palette.error.main, 0.1)
          : alpha(theme.palette.error.main, 0.1),
      })}
    >
      <Typography
        variant="body2"
        sx={(theme) => ({
          color: value
            ? theme.palette.mode === "dark"
              ? theme.palette.success.light
              : theme.palette.success.dark
            : theme.palette.mode === "dark"
            ? theme.palette.error.light
            : theme.palette.error.dark,
        })}
      >
        {value ? "Yes" : "No"}
      </Typography>
    </Box>
  );
};

// 为Greek Financial LLM Leaderboard创建自定义标题组件
const createGreekLeaderboardHeader = (header) => (
  <Box
    className="header-content"
    sx={{
      display: "flex",
      alignItems: "center",
      width: "100%",
      position: "relative",
    }}
  >
    <HeaderLabel
      label="Greek Financial LLM Leaderboard"
      tooltip="Average performance on Greek financial tasks"
      className="header-label"
      isSorted={header?.column?.getIsSorted()}
    />

    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.5,
        ml: "auto",
        flexShrink: 0,
      }}
    >
      <InfoIcon tooltip="Average performance on Greek financial tasks" />
      <Link
        href="https://huggingface.co/spaces/TheFinAI/Open-Greek-Financial-LLM-Leaderboard#/"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="View Greek Financial LLM Leaderboard"
        sx={{
          color: "info.main",
          display: "flex",
          alignItems: "center",
          ml: 0.5,
          textDecoration: "none",
          "&:hover": {
            textDecoration: "underline",
            "& svg": {
              opacity: 0.8,
            },
          },
        }}
      >
        <OpenInNewIcon
          sx={{
            fontSize: "1rem",
            opacity: 0.6,
            transition: "opacity 0.2s ease-in-out",
          }}
        />
      </Link>
    </Box>
  </Box>
);

// 为各种类型的Leaderboard创建自定义标题组件
const createLeaderboardHeader = (label, tooltip, linkUrl) => (header) => (
  <Box
    className="header-content"
    sx={{
      display: "flex",
      alignItems: "center",
      width: "100%",
      position: "relative",
    }}
  >
    <HeaderLabel
      label={`${label} Leaderboard`}
      tooltip={tooltip}
      className="header-label"
      isSorted={header?.column?.getIsSorted()}
    />

    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.5,
        ml: "auto",
        flexShrink: 0,
      }}
    >
      <InfoIcon tooltip={tooltip} />
      {linkUrl && (
        <Link
          href={linkUrl}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`View ${label} Leaderboard`}
          sx={{
            color: "info.main",
            display: "flex",
            alignItems: "center",
            ml: 0.5,
            textDecoration: "none",
            "&:hover": {
              textDecoration: "underline",
              "& svg": {
                opacity: 0.8,
              },
            },
          }}
        >
          <OpenInNewIcon
            sx={{
              fontSize: "1rem",
              opacity: 0.6,
              transition: "opacity 0.2s ease-in-out",
            }}
          />
        </Link>
      )}
    </Box>
  </Box>
);

export const createColumns = (
  getColorForValue,
  scoreDisplay = "normalized",
  columnVisibility = {},
  totalModels,
  averageMode = "all",
  searchValue = "",
  rankingMode = "static",
  onTogglePin,
  hasPinnedRows = false
) => {
  // Adjust column sizes based on the presence of pinned rows
  const getColumnSize = (defaultSize) =>
    hasPinnedRows ? "auto" : `${defaultSize}px`;

  const baseColumns = [
    {
      accessorKey: "isPinned",
      header: () => null,
      cell: ({ row }) => (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              onTogglePin(row.original.id);
            }}
            sx={{
              padding: 0.5,
              color: row.original.isPinned ? "primary.main" : "grey.400",
              "&:hover": {
                color: "primary.main",
              },
            }}
          >
            {row.original.isPinned ? (
              <PushPinIcon fontSize="small" />
            ) : (
              <PushPinOutlinedIcon fontSize="small" />
            )}
          </IconButton>
        </Box>
      ),
      enableSorting: false,
      size: getColumnSize(40),
    },
    {
      accessorKey: "rank",
      header: createHeaderCell("Rank"),
      cell: ({ row }) => {
        const rank =
          rankingMode === "static"
            ? row.original.static_rank
            : row.original.dynamic_rank;
        const isMissing = row.original.isMissing === true;
        
        // Don't display rank for missing models
        if (isMissing) {
          return (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "100%",
              }}
            >
              <Typography
                sx={{
                  color: "text.secondary",
                  fontStyle: "italic",
                }}
              >
                -
              </Typography>
            </Box>
          );
        }

        return (
          <RankIndicator
            rank={rank}
            previousRank={row.original.previous_rank}
            mode="static"
          />
        );
      },
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["rank"],
    },
    {
      id: "model_type",
      accessorFn: (row) => row.model.type,
      header: createHeaderCell("Type"),
      sortingFn: typeColumnSort,
      cell: ({ row }) => {
        const isMissing = row.original.isMissing === true;
        
        // Don't display type icon for missing models
        if (isMissing) {
          return (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "100%",
              }}
            >
              <Typography
                sx={{
                  color: "text.secondary",
                  fontStyle: "italic",
                }}
              >
                -
              </Typography>
            </Box>
          );
        }
        
        return (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
          }}
        >
          <Tooltip title={row.original.model.type}>
            <Typography
              sx={{
                fontSize: "1.2rem",
                cursor: "help",
                lineHeight: 1,
                fontFamily:
                  '"Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif',
              }}
            >
              {getModelTypeIcon(row.original.model.type)}
            </Typography>
          </Tooltip>
        </Box>
        );
      },
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.type_icon"],
    },
    {
      accessorKey: "id",
      header: createModelHeader(totalModels),
      cell: ({ row }) => {
        const textSearch = extractTextSearch(searchValue);
        const modelName = row.original.model.name;
        const isMissing = row.original.isMissing === true;

        // Display special style for missing models
        if (isMissing) {
          return (
            <Box
              sx={{
                width: "100%",
                display: "flex",
                alignItems: "center",
              }}
            >
              <Typography
                sx={{
                  color: "text.secondary",
                  fontStyle: "italic",
                }}
              >
                {modelName}
              </Typography>
            </Box>
          );
        }

        return (
          <Box
            sx={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              gap: 1,
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                minWidth: 0,
                flex: 1,
              }}
            >
              <Link
                href={`https://huggingface.co/${modelName}`}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View ${modelName} on Hugging Face Hub`}
                title={TABLE_TOOLTIPS.HUB_LINK(modelName)}
                sx={{
                  textDecoration: "none",
                  color: "info.main",
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                  "&:hover": {
                    textDecoration: "underline",
                    color: (theme) =>
                      theme.palette.mode === "dark"
                        ? theme.palette.info.light
                        : theme.palette.info.dark,
                    "& svg": {
                      opacity: 0.8,
                    },
                  },
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  flex: 1,
                  minWidth: 0,
                  fontWeight: row.original.static_rank <= 3 ? 600 : "inherit",
                }}
              >
                <HighlightedText text={modelName} searchValue={textSearch} />
                <OpenInNewIcon
                  sx={{
                    fontSize: "0.75rem",
                    opacity: 0.6,
                    transition: "opacity 0.2s ease-in-out",
                    ml: 0.5,
                    flexShrink: 0,
                  }}
                />
              </Link>
              <Link
                href={getDetailsUrl(modelName)}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View detailed evaluation results for ${modelName}`}
                title={TABLE_TOOLTIPS.EVAL_RESULTS(modelName)}
                sx={{
                  textDecoration: "none",
                  "&:hover": {
                    textDecoration: "underline",
                    "& svg": {
                      color: "text.primary",
                    },
                  },
                  display: "flex",
                  alignItems: "center",
                  color: "text.secondary",
                  flexShrink: 0,
                  mr: 0,
                }}
              >
                <DatabaseIcon />
              </Link>
            </Box>
          </Box>
        );
      },
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["id"],
    },
    {
      accessorKey: "model.average_score",
      header: createHeaderCell("Average", COLUMN_TOOLTIPS.AVERAGE),
      cell: ({ row, getValue }) =>
        createScoreCell(getValue, row, "model.average_score"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"],
      meta: {
        headerStyle: {
          borderLeft: (theme) =>
            `2px solid ${alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            )}`,
          borderRight: (theme) =>
            `2px solid ${alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            )}`,
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          borderLeft: (theme) =>
            `2px solid ${alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            )}`,
          borderRight: (theme) =>
            `2px solid ${alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            )}`,
        }),
      },
    },
    {
      accessorKey: "model.openness",
      header: createHeaderCell("Openness", "Model openness classification"),
      cell: ({ row }) => {
        return (
          <Box
            sx={{
              width: "100%",
              display: "flex",
              alignItems: "center",
            }}
          >
            <Typography variant="body2">
              Class III-Open Model
            </Typography>
          </Box>
        );
      },
      size: 150,
      enableSorting: false,
      meta: {
        headerStyle: {
          borderRight: (theme) =>
            `2px solid ${alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            )}`,
        },
        cellStyle: () => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          borderRight: (theme) =>
            `2px solid ${alpha(
              theme.palette.divider,
              theme.palette.mode === "dark" ? 0.1 : 0.2
            )}`,
        }),
      },
    },
  ];
  const createScoreCell = (getValue, row, field) => {
    const value = getValue();
    const rawValue = field.includes("normalized")
      ? row.original.evaluations[field.split(".")[1]]?.value
      : value;

    const isAverageColumn = field === "model.average_score";
    const hasNoValue = value === null || value === undefined;
    const isMissing = row.original.isMissing === true;

    // Display special text for "missing" models
    if (isMissing) {
      return (
        <Box sx={commonStyles.cellContainer}>
          <Box
            sx={{
              position: "relative",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1,
            }}
          >
            <Typography 
              variant="body2"
              sx={{
                color: 'text.secondary',
                fontStyle: 'italic',
              }}
            >
              missing
            </Typography>
          </Box>
        </Box>
      );
    }

    return (
      <Box sx={commonStyles.cellContainer}>
        {!hasNoValue && (scoreDisplay === "normalized" || isAverageColumn) && (
          <Box
            sx={{
              position: "absolute",
              left: -16,
              top: -16,
              height: "calc(100% + 32px)",
              width: `calc(${value}% + 16px)`,
              backgroundColor: getColorForValue(value),
              opacity: (theme) => (theme.palette.mode === "light" ? 0.1 : 0.2),
              transition: "width 0.3s ease",
              zIndex: 0,
            }}
          />
        )}
        <Box
          sx={{
            position: "relative",
            display: "flex",
            alignItems: "center",
            gap: 1,
            zIndex: 1,
            pl: isAverageColumn && !hasNoValue ? 1 : 0,
          }}
        >
          {isAverageColumn && !hasNoValue && (
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                marginLeft: -1,
                backgroundColor: getColorForValue(value),
              }}
            />
          )}
          <Typography variant="body2">
            {hasNoValue ? (
              "-"
            ) : (
              <>
                {isAverageColumn ? (
                  <>
                    {value.toFixed(2)}
                    <span style={{ opacity: 0.5 }}> %</span>
                  </>
                ) : scoreDisplay === "normalized" ? (
                  <>
                    {value.toFixed(2)}
                    <span style={{ opacity: 0.5 }}> %</span>
                  </>
                ) : (
                  <>{rawValue.toFixed(2)}</>
                )}
              </>
            )}
          </Typography>
        </Box>
      </Box>
    );
  };

  const evaluationColumns = [
    {
      accessorKey: "evaluations.greek_average",
      header: createGreekLeaderboardHeader,
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.greek_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.info.light, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.info.light, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.vision_average",
      header: createLeaderboardHeader("Vision", "Average performance on vision tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.vision_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.primary.light, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.primary.light, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.audio_average",
      header: createLeaderboardHeader("Audio", "Average performance on audio tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.audio_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.secondary.light, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.secondary.light, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.english_average",
      header: createLeaderboardHeader("English", "Average performance on English language tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.english_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.success.light, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.success.light, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.chinese_average",
      header: createLeaderboardHeader("Chinese", "Average performance on Chinese language tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.chinese_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.warning.light, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.warning.light, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.japanese_average",
      header: createLeaderboardHeader("Japanese", "Average performance on Japanese language tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.japanese_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.error.light, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.error.light, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.spanish_average",
      header: createLeaderboardHeader("Spanish", "Average performance on Spanish language tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.spanish_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.info.main, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.info.main, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.bilingual_average",
      header: createLeaderboardHeader("Bilingual", "Average performance on bilingual tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.bilingual_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.05),
        }),
      },
    },
    {
      accessorKey: "evaluations.multilingual_average",
      header: createLeaderboardHeader("Multilingual", "Average performance on multilingual tasks", null),
      cell: ({ row, getValue }) => createScoreCell(getValue, row, "evaluations.multilingual_average"),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.average_score"] || 100,
      meta: {
        headerStyle: {
          backgroundColor: (theme) => alpha(theme.palette.secondary.main, 0.05),
        },
        cellStyle: (value) => ({
          position: "relative",
          overflow: "hidden",
          padding: "8px 16px",
          backgroundColor: (theme) => alpha(theme.palette.secondary.main, 0.05),
        }),
    },
    }
  ];

  const optionalColumns = [
    {
      accessorKey: "model.architecture",
      header: createHeaderCell("Architecture", COLUMN_TOOLTIPS.ARCHITECTURE),
      accessorFn: (row) => row.model.architecture,
      cell: ({ row }) => (
        <Tooltip title={row.original.model.architecture || "-"}>
          <span>{row.original.model.architecture || "-"}</span>
        </Tooltip>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.architecture"],
    },
    {
      accessorKey: "model.precision",
      header: createHeaderCell("Precision", COLUMN_TOOLTIPS.PRECISION),
      accessorFn: (row) => row.model.precision,
      cell: ({ row }) => (
        <Tooltip title={row.original.model.precision || "-"}>
          <span>{row.original.model.precision || "-"}</span>
        </Tooltip>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.precision"],
    },
    {
      accessorKey: "metadata.params_billions",
      header: createHeaderCell("Parameters", COLUMN_TOOLTIPS.PARAMETERS),
      cell: ({ row }) => (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-start",
          }}
        >
          <Typography variant="body2">
            {row.original.metadata.params_billions}
            <span style={{ opacity: 0.6 }}>B</span>
          </Typography>
        </Box>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.params_billions"],
    },
    {
      accessorKey: "metadata.hub_license",
      header: createHeaderCell("License", COLUMN_TOOLTIPS.LICENSE),
      cell: ({ row }) => (
        <Tooltip title={row.original.metadata.hub_license || "-"}>
          <Typography
            variant="body2"
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {row.original.metadata.hub_license || "-"}
          </Typography>
        </Tooltip>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.hub_license"],
    },
    {
      accessorKey: "metadata.hub_hearts",
      header: createHeaderCell(
        "Hub ❤️",
        "Number of likes received on the Hugging Face Hub"
      ),
      cell: ({ row }) => (
        <Typography variant="body2">
          {row.original.metadata.hub_hearts}
        </Typography>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.hub_hearts"],
    },
    {
      accessorKey: "metadata.upload_date",
      header: createHeaderCell(
        "Upload Date",
        "Date when the model was uploaded to the Hugging Face Hub"
      ),
      cell: ({ row }) => (
        <Tooltip title={row.original.metadata.upload_date || "-"}>
          <Typography
            variant="body2"
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {row.original.metadata.upload_date || "-"}
          </Typography>
        </Tooltip>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.upload_date"],
    },
    {
      accessorKey: "metadata.submission_date",
      header: createHeaderCell(
        "Submission Date",
        "Date when the model was submitted to the leaderboard"
      ),
      cell: ({ row }) => (
        <Tooltip title={row.original.metadata.submission_date || "-"}>
          <Typography
            variant="body2"
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {row.original.metadata.submission_date || "-"}
          </Typography>
        </Tooltip>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.submission_date"],
    },
    {
      accessorKey: "metadata.generation",
      header: createHeaderCell(
        "Generation",
        "The generation or version number of the model"
      ),
      cell: ({ row }) => (
        <Typography variant="body2">
          {row.original.metadata.generation}
        </Typography>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.generation"],
    },
    {
      accessorKey: "metadata.base_model",
      header: createHeaderCell(
        "Base Model",
        "The original model this model was derived from"
      ),
      cell: ({ row }) => (
        <Tooltip title={row.original.metadata.base_model || "-"}>
          <Typography
            variant="body2"
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {row.original.metadata.base_model || "-"}
          </Typography>
        </Tooltip>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.base_model"],
    },
    {
      accessorKey: "metadata.co2_cost",
      header: createHeaderCell("CO₂ Cost", COLUMN_TOOLTIPS.CO2_COST),
      cell: ({ row }) => (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-start",
          }}
        >
          <Typography variant="body2">
            {row.original.metadata.co2_cost?.toFixed(2) || "0"}
            <span style={{ opacity: 0.6 }}> kg</span>
          </Typography>
        </Box>
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["metadata.co2_cost"],
    },
    {
      accessorKey: "model.has_chat_template",
      header: createHeaderCell(
        "Chat Template",
        "Whether this model has a chat template defined"
      ),
      cell: ({ row }) => (
        <BooleanValue value={row.original.model.has_chat_template} />
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["model.has_chat_template"],
    },
    {
      accessorKey: "features.is_not_available_on_hub",
      header: createHeaderCell(
        "Hub Availability",
        "Whether the model is available on the Hugging Face Hub"
      ),
      cell: ({ row }) => (
        <BooleanValue value={row.original.features.is_not_available_on_hub} />
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES[
        "features.is_not_available_on_hub"
      ],
    },
    {
      accessorKey: "features.is_highlighted_by_maintainer",
      header: createHeaderCell(
        "Official Providers",
        "Models that are officially provided and maintained by their original creators or organizations"
      ),
      cell: ({ row }) => (
        <BooleanValue
          value={row.original.features.is_highlighted_by_maintainer}
        />
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES[
        "features.is_highlighted_by_maintainer"
      ],
      enableSorting: true,
    },
    {
      accessorKey: "features.is_moe",
      header: createHeaderCell(
        "Mixture of Experts",
        "Whether this model uses a Mixture of Experts architecture"
      ),
      cell: ({ row }) => <BooleanValue value={row.original.features.is_moe} />,
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["features.is_moe"],
    },
    {
      accessorKey: "features.is_flagged",
      header: createHeaderCell(
        "Flag Status",
        "Whether this model has been flagged for any issues"
      ),
      cell: ({ row }) => (
        <BooleanValue value={row.original.features.is_flagged} />
      ),
      size: TABLE_DEFAULTS.COLUMNS.COLUMN_SIZES["features.is_flagged"],
    },
  ];

  // Utiliser directement columnVisibility
  const finalColumns = [
    ...baseColumns,
    ...evaluationColumns,
    ...optionalColumns
      .filter((col) => columnVisibility[col.accessorKey])
      .sort((a, b) => {
        // Définir l'ordre personnalisé des colonnes
        const order = {
          "model.architecture": 1,
          "model.precision": 2,
          "metadata.params_billions": 3,
          "metadata.hub_license": 4,
          "metadata.co2_cost": 5,
          "metadata.hub_hearts": 6,
          "metadata.upload_date": 7,
          "metadata.submission_date": 8,
          "metadata.generation": 9,
          "metadata.base_model": 10,
          "model.has_chat_template": 11,
          "features.is_not_available_on_hub": 12,
          "features.is_highlighted_by_maintainer": 13,
          "features.is_moe": 14,
          "features.is_flagged": 15,
        };
        return order[a.accessorKey] - order[b.accessorKey];
      }),
  ];

  return finalColumns;
};

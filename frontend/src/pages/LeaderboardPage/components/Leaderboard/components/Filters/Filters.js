import React, {
  useState,
  useEffect,
  useMemo,
  useRef,
  forwardRef,
  useCallback,
} from "react";
import {
  Box,
  Typography,
  Collapse,
  Slider,
  Grid,
  Accordion,
  AccordionDetails,
  alpha,
  useTheme,
  TextField,
} from "@mui/material";
import {
  TABLE_DEFAULTS,
  BOOLEAN_FILTER_OPTIONS,
  FILTER_PRECISIONS,
} from "../../constants/defaults";
import FilterTag from "../../../../../../components/shared/FilterTag";
import { MODEL_TYPE_ORDER, MODEL_TYPES } from "../../constants/modelTypes";
import { useLeaderboard } from "../../context/LeaderboardContext";
import InfoIconWithTooltip from "../../../../../../components/shared/InfoIconWithTooltip";
import { COLUMN_TOOLTIPS } from "../../constants/tooltips";

const getTooltipContent = (title) => {
  switch (title) {
    case "Model Type":
      return COLUMN_TOOLTIPS.ARCHITECTURE;
    case "Precision format":
      return COLUMN_TOOLTIPS.PRECISION;
    case "Flags":
      return COLUMN_TOOLTIPS.FLAGS;
    case "Parameters":
      return COLUMN_TOOLTIPS.PARAMETERS;
    default:
      return null;
  }
};

const FilterGroup = ({
  title,
  tooltip,
  children,
  paramsRange,
  onParamsRangeChange,
}) => {
  const theme = useTheme();
  const [localParamsRange, setLocalParamsRange] = useState(paramsRange);
  const stableTimerRef = useRef(null);

  // Handle local range change
  const handleLocalRangeChange = useCallback((event, newValue) => {
    setLocalParamsRange(newValue);
  }, []);

  // Handle input change
  const handleInputChange = useCallback(
    (index) => (event) => {
      const value = event.target.value === "" ? "" : Number(event.target.value);
      if (value === "" || (value >= -1 && value <= 140)) {
        const newRange = [...localParamsRange];
        newRange[index] = value;
        setLocalParamsRange(newRange);
      }
    },
    [localParamsRange]
  );

  // Sync local state with props
  useEffect(() => {
    setLocalParamsRange(paramsRange);
  }, [paramsRange]);

  // Propagate changes to parent after delay
  useEffect(() => {
    if (stableTimerRef.current) {
      clearTimeout(stableTimerRef.current);
    }

    stableTimerRef.current = setTimeout(() => {
      if (Array.isArray(localParamsRange) && localParamsRange.length === 2) {
        onParamsRangeChange(localParamsRange);
      }
    }, 300);

    return () => {
      if (stableTimerRef.current) {
        clearTimeout(stableTimerRef.current);
      }
    };
  }, [localParamsRange, onParamsRangeChange]);

  const renderContent = () => {
    if (title === "Parameters") {
      return (
        <Box
          sx={{
            px: 1,
          }}
        >
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 2,
            }}
          >
            <Box
              sx={{
                display: "flex",
                gap: 1,
                position: "absolute",
                right: 0,
                top: "-5px",
              }}
            >
              <TextField
                value={localParamsRange[0]}
                onChange={handleInputChange(0)}
                variant="outlined"
                size="small"
                type="number"
                inputProps={{
                  min: -1,
                  max: 140,
                  style: {
                    width: "45px",
                    textAlign: "center",
                    padding: "4px",
                    fontSize: "0.875rem",
                  },
                }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 1,
                    height: "28px",
                  },
                }}
              />
              <TextField
                value={localParamsRange[1]}
                onChange={handleInputChange(1)}
                variant="outlined"
                size="small"
                type="number"
                inputProps={{
                  min: -1,
                  max: 140,
                  style: {
                    width: "45px",
                    textAlign: "center",
                    padding: "4px",
                    fontSize: "0.875rem",
                  },
                }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 1,
                    height: "28px",
                  },
                }}
              />
            </Box>
          </Box>
          <Slider
            value={localParamsRange}
            onChange={handleLocalRangeChange}
            valueLabelDisplay="auto"
            min={-1}
            max={140}
            step={1}
            marks={[
              { value: -1, label: "All" },
              { value: 7, label: "7" },
              { value: 70, label: "70" },
              { value: 140, label: "140" },
            ]}
            valueLabelFormat={(value) => (value === -1 ? "All" : `${value}B`)}
            sx={{
              "& .MuiSlider-rail": {
                height: 10,
                backgroundColor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                opacity: 1,
              },
              "& .MuiSlider-track": {
                height: 10,
                border: "1px solid",
                borderColor: (theme) =>
                  alpha(
                    theme.palette.primary.main,
                    theme.palette.mode === "light" ? 0.3 : 0.5
                  ),
                backgroundColor: (theme) =>
                  alpha(
                    theme.palette.primary.main,
                    theme.palette.mode === "light" ? 0.1 : 0.2
                  ),
              },
              "& .MuiSlider-thumb": {
                width: 20,
                height: 20,
                backgroundColor: "background.paper",
                border: "1px solid",
                borderColor: "primary.main",
                "&:hover, &.Mui-focusVisible": {
                  boxShadow: (theme) =>
                    `0 0 0 8px ${alpha(
                      theme.palette.primary.main,
                      theme.palette.mode === "light" ? 0.08 : 0.16
                    )}`,
                },
                "&.Mui-active": {
                  boxShadow: (theme) =>
                    `0 0 0 12px ${alpha(
                      theme.palette.primary.main,
                      theme.palette.mode === "light" ? 0.08 : 0.16
                    )}`,
                },
              },
              "& .MuiSlider-valueLabel": {
                backgroundColor: theme.palette.primary.main,
              },
              "& .MuiSlider-mark": {
                width: 2,
                height: 10,
                backgroundColor: "divider",
              },
              "& .MuiSlider-markLabel": {
                fontSize: "0.875rem",
                "&::after": {
                  content: '"B"',
                  marginLeft: "1px",
                  opacity: 0.5,
                },
                '&[data-index="0"]::after': {
                  content: '""',
                },
              },
            }}
          />
        </Box>
      );
    }
    return (
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          gap: 0.5,
        }}
      >
        {children}
      </Box>
    );
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 0.5,
          mb: 1.5,
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <InfoIconWithTooltip
          tooltip={getTooltipContent(title)}
          iconProps={{ sx: { fontSize: "1rem" } }}
        />
      </Box>
      {renderContent()}
    </Box>
  );
};

const CustomCollapse = forwardRef((props, ref) => {
  const { children, style = {}, ...other } = props;
  const collapsedHeight = "0px";
  const timeout = 300;

  const wrapperRef = useRef(null);
  const [animatedHeight, setAnimatedHeight] = useState(
    props.in ? "auto" : collapsedHeight
  );

  useEffect(() => {
    if (!wrapperRef.current) return;

    if (props.in) {
      const contentHeight = wrapperRef.current.scrollHeight;
      setAnimatedHeight(`${contentHeight}px`);
    } else {
      setAnimatedHeight(collapsedHeight);
    }
  }, [props.in, children]);

  const handleEntered = (node) => {
    setAnimatedHeight("auto");
    if (props.onEntered) {
      props.onEntered(node);
    }
  };

  return (
    <Collapse
      ref={ref}
      style={{
        ...style,
        height: animatedHeight,
      }}
      timeout={timeout}
      onEntered={handleEntered}
      {...other}
    >
      <div ref={wrapperRef}>{children}</div>
    </Collapse>
  );
});

const LeaderboardFilters = ({
  selectedPrecisions = FILTER_PRECISIONS,
  onPrecisionsChange = () => {},
  selectedTypes = MODEL_TYPE_ORDER,
  onTypesChange = () => {},
  paramsRange = [-1, 140],
  onParamsRangeChange = () => {},
  selectedBooleanFilters = [],
  onBooleanFiltersChange = () => {},
  data = [],
  expanded,
  onToggleExpanded,
  loading = false,
}) => {
  const [localParamsRange, setLocalParamsRange] = useState(paramsRange);
  const stableTimerRef = useRef(null);
  const { state, actions } = useLeaderboard();
  const { normal: filterCounts, officialOnly: officialOnlyCounts } =
    state.filterCounts;
  const isOfficialProviderActive = state.filters.isOfficialProviderActive;
  const currentCounts = useMemo(
    () => (isOfficialProviderActive ? officialOnlyCounts : filterCounts),
    [isOfficialProviderActive, officialOnlyCounts, filterCounts]
  );

  useEffect(() => {
    setLocalParamsRange(paramsRange);
  }, [paramsRange]);

  // Clean up timer when component unmounts
  useEffect(() => {
    return () => {
      if (stableTimerRef.current) {
        clearTimeout(stableTimerRef.current);
      }
    };
  }, []);

  const handleParamsRangeChange = (event, newValue) => {
    setLocalParamsRange(newValue);
  };

  const handleParamsRangeChangeCommitted = (event, newValue) => {
    // Reset timer on each change
    if (stableTimerRef.current) {
      clearTimeout(stableTimerRef.current);
    }

    // Update URL immediately
    onParamsRangeChange(newValue);

    // Trigger data update after debounce
    stableTimerRef.current = setTimeout(() => {
      actions.updateFilteredData();
    }, TABLE_DEFAULTS.DEBOUNCE.SEARCH);
  };

  const handlePrecisionToggle = (precision) => {
    const newPrecisions = selectedPrecisions.includes(precision)
      ? selectedPrecisions.filter((p) => p !== precision)
      : [...selectedPrecisions, precision];
    onPrecisionsChange(newPrecisions);
  };

  const handleBooleanFilterToggle = (filter) => {
    const newFilters = selectedBooleanFilters.includes(filter)
      ? selectedBooleanFilters.filter((f) => f !== filter)
      : [...selectedBooleanFilters, filter];
    onBooleanFiltersChange(newFilters);
  };

  // Filter options based on their hide property
  const showFilterOptions = BOOLEAN_FILTER_OPTIONS.filter(
    (option) => !option.hide
  );
  const hideFilterOptions = BOOLEAN_FILTER_OPTIONS.filter(
    (option) => option.hide
  );

  const handleOfficialProviderToggle = () => {
    actions.toggleOfficialProvider();
  };

  return loading ? null : (
    <Box>
      <Accordion
        expanded={expanded}
        onChange={onToggleExpanded}
        elevation={0}
        TransitionComponent={CustomCollapse}
        disableGutters
        sx={{
          backgroundColor: "transparent",
          border: "1px solid transparent !important",
          "& .MuiAccordion-region": {
            margin: 0,
          },
          "&.MuiAccordion-root": {
            margin: 0,
          },
          "& .MuiCollapse-root": {
            margin: 0,
          },
        }}
      >
        <AccordionDetails
          sx={{
            p: 0,
            m: 0,
          }}
        >
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12} md={9} sx={{ display: "flex" }}>
                <Box
                  sx={{
                    backgroundColor: (theme) =>
                      alpha(theme.palette.primary.main, 0.02),
                    border: "1px solid",
                    borderColor: (theme) =>
                      alpha(theme.palette.primary.main, 0.2),
                    borderRadius: 1,
                    p: 3,
                    position: "relative",
                    width: "100%",
                    display: "flex",
                    flexDirection: "column",
                    "&:hover": {
                      borderColor: (theme) =>
                        alpha(theme.palette.primary.main, 0.3),
                      backgroundColor: (theme) =>
                        alpha(theme.palette.primary.main, 0.03),
                    },
                    transition: (theme) =>
                      theme.transitions.create(
                        ["border-color", "background-color"],
                        {
                          duration: theme.transitions.duration.short,
                        }
                      ),
                  }}
                >
                  <Typography
                    variant="h6"
                    sx={{
                      mb: 3,
                      fontWeight: 600,
                      color: "text.primary",
                      fontSize: "1.1rem",
                    }}
                  >
                    Advanced Filters
                  </Typography>
                  <Box sx={{ flex: 1 }}>
                    <Grid container spacing={3} sx={{ flex: 1 }}>
                      <Grid item xs={12} md={6}>
                        <Box>
                          <FilterGroup
                            title="Precision format"
                            tooltip={COLUMN_TOOLTIPS.PRECISION}
                          >
                            {FILTER_PRECISIONS.map((precision) => (
                              <FilterTag
                                key={precision}
                                label={precision}
                                checked={selectedPrecisions.includes(precision)}
                                onChange={() =>
                                  handlePrecisionToggle(precision)
                                }
                                count={currentCounts.precisions[precision]}
                                showCheckbox={true}
                              />
                            ))}
                          </FilterGroup>
                        </Box>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Box sx={{ position: "relative" }}>
                          <FilterGroup
                            title="Parameters"
                            tooltip={COLUMN_TOOLTIPS.PARAMETERS}
                            paramsRange={paramsRange}
                            onParamsRangeChange={onParamsRangeChange}
                          >
                            <Box
                              sx={{
                                width: "100%",
                                display: "flex",
                                alignItems: "center",
                                gap: 2,
                              }}
                            >
                              <Box sx={{ flex: 1 }}>
                                <Slider
                                  value={localParamsRange}
                                  onChange={handleParamsRangeChange}
                                  onChangeCommitted={
                                    handleParamsRangeChangeCommitted
                                  }
                                  valueLabelDisplay="auto"
                                  min={-1}
                                  max={140}
                                  step={1}
                                  marks={[
                                    { value: -1, label: "" },
                                    { value: 0, label: "0" },
                                    { value: 7, label: "7" },
                                    { value: 70, label: "70" },
                                    { value: 140, label: "140" },
                                  ]}
                                  sx={{
                                    "& .MuiSlider-rail": {
                                      height: 10,
                                      backgroundColor: "background.paper",
                                      border: "1px solid",
                                      borderColor: "divider",
                                      opacity: 1,
                                    },
                                    "& .MuiSlider-track": {
                                      height: 10,
                                      border: "1px solid",
                                      borderColor: (theme) =>
                                        alpha(
                                          theme.palette.primary.main,
                                          theme.palette.mode === "light"
                                            ? 0.3
                                            : 0.5
                                        ),
                                      backgroundColor: (theme) =>
                                        alpha(
                                          theme.palette.primary.main,
                                          theme.palette.mode === "light"
                                            ? 0.1
                                            : 0.2
                                        ),
                                    },
                                    "& .MuiSlider-thumb": {
                                      width: 20,
                                      height: 20,
                                      backgroundColor: "background.paper",
                                      border: "1px solid",
                                      borderColor: "primary.main",
                                      "&:hover, &.Mui-focusVisible": {
                                        boxShadow: (theme) =>
                                          `0 0 0 8px ${alpha(
                                            theme.palette.primary.main,
                                            theme.palette.mode === "light"
                                              ? 0.08
                                              : 0.16
                                          )}`,
                                      },
                                      "&.Mui-active": {
                                        boxShadow: (theme) =>
                                          `0 0 0 12px ${alpha(
                                            theme.palette.primary.main,
                                            theme.palette.mode === "light"
                                              ? 0.08
                                              : 0.16
                                          )}`,
                                      },
                                    },
                                    "& .MuiSlider-mark": {
                                      backgroundColor: "text.disabled",
                                      height: 2,
                                      width: 2,
                                      borderRadius: "50%",
                                    },
                                    "& .MuiSlider-markLabel": {
                                      color: "text.secondary",
                                    },
                                  }}
                                />
                              </Box>
                            </Box>
                          </FilterGroup>
                        </Box>
                      </Grid>

                      {/* Deuxième ligne */}
                      <Grid item xs={12} md={6}>
                        <Box>
                          <FilterGroup
                            title="Model Type"
                            tooltip={COLUMN_TOOLTIPS.ARCHITECTURE}
                          >
                            {MODEL_TYPE_ORDER.sort(
                              (a, b) =>
                                MODEL_TYPES[a].order - MODEL_TYPES[b].order
                            ).map((type) => (
                              <FilterTag
                                key={type}
                                label={`${MODEL_TYPES[type]?.icon} ${
                                  MODEL_TYPES[type]?.label || type
                                }`}
                                checked={selectedTypes.includes(type)}
                                onChange={() => {
                                  const newTypes = selectedTypes.includes(type)
                                    ? selectedTypes.filter((t) => t !== type)
                                    : [...selectedTypes, type];
                                  onTypesChange(newTypes);
                                }}
                                count={currentCounts.modelTypes[type]}
                                variant="tag"
                                showCheckbox={true}
                              />
                            ))}
                          </FilterGroup>
                        </Box>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Box>
                          <FilterGroup
                            title="Flags"
                            tooltip={COLUMN_TOOLTIPS.FLAGS}
                          >
                            {hideFilterOptions.map((filter) => (
                              <FilterTag
                                key={filter.value}
                                label={filter.label}
                                checked={
                                  !selectedBooleanFilters.includes(filter.value)
                                }
                                onChange={() => {
                                  const newFilters =
                                    selectedBooleanFilters.includes(
                                      filter.value
                                    )
                                      ? selectedBooleanFilters.filter(
                                          (f) => f !== filter.value
                                        )
                                      : [
                                          ...selectedBooleanFilters,
                                          filter.value,
                                        ];
                                  onBooleanFiltersChange(newFilters);
                                }}
                                count={
                                  filter.value === "is_moe"
                                    ? currentCounts.mixtureOfExperts
                                    : filter.value === "is_flagged"
                                    ? currentCounts.flagged
                                    : filter.value === "is_merged"
                                    ? currentCounts.merged
                                    : filter.value === "is_not_available_on_hub"
                                    ? currentCounts.notOnHub
                                    : 0
                                }
                                isHideFilter={false}
                                totalCount={data.length}
                                showCheckbox={true}
                              />
                            ))}
                          </FilterGroup>
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} md={3} sx={{ display: "flex" }}>
                <Box
                  sx={{
                    backgroundColor: (theme) =>
                      alpha(theme.palette.secondary.main, 0.02),
                    border: "1px solid",
                    borderColor: (theme) =>
                      alpha(theme.palette.secondary.main, 0.15),
                    borderRadius: 1,
                    p: 3,
                    position: "relative",
                    width: "100%",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    textAlign: "center",
                    minHeight: "100%",
                    "&:hover": {
                      borderColor: (theme) =>
                        alpha(theme.palette.secondary.main, 0.25),
                      backgroundColor: (theme) =>
                        alpha(theme.palette.secondary.main, 0.03),
                    },
                    transition: (theme) =>
                      theme.transitions.create(
                        ["border-color", "background-color"],
                        {
                          duration: theme.transitions.duration.short,
                        }
                      ),
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: 2,
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "1.1rem",
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                      }}
                    >
                      Official Models
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: "text.secondary",
                        fontSize: "0.8rem",
                        lineHeight: 1.4,
                        maxWidth: "280px",
                      }}
                    >
                      Show only models that are officially provided and
                      maintained by their original creators.
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 1,
                        width: "100%",
                        alignItems: "center",
                      }}
                    >
                      {showFilterOptions.map((filter) => (
                        <Box
                          key={filter.value}
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: 1,
                          }}
                        >
                          <FilterTag
                            label={filter.label}
                            checked={
                              filter.value === "is_highlighted_by_maintainer"
                                ? isOfficialProviderActive
                                : selectedBooleanFilters.includes(filter.value)
                            }
                            onChange={
                              filter.value === "is_highlighted_by_maintainer"
                                ? handleOfficialProviderToggle
                                : () => handleBooleanFilterToggle(filter.value)
                            }
                            count={
                              filter.value === "is_highlighted_by_maintainer"
                                ? currentCounts.maintainersHighlight
                                : 0
                            }
                            showCheckbox={true}
                            variant="secondary"
                          />
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                              color: "text.secondary",
                              fontSize: "0.75rem",
                            }}
                          >
                            <Box
                              component="span"
                              sx={{
                                width: 6,
                                height: 6,
                                borderRadius: "50%",
                                backgroundColor: (
                                  filter.value ===
                                  "is_highlighted_by_maintainer"
                                    ? isOfficialProviderActive
                                    : selectedBooleanFilters.includes(
                                        filter.value
                                      )
                                )
                                  ? "success.main"
                                  : "text.disabled",
                              }}
                            />
                            {(
                              filter.value === "is_highlighted_by_maintainer"
                                ? isOfficialProviderActive
                                : selectedBooleanFilters.includes(filter.value)
                            )
                              ? "Filter active"
                              : "Filter inactive"}
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default LeaderboardFilters;

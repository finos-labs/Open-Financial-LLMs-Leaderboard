import React, { useRef, useCallback, useMemo } from "react";
import {
  Paper,
  Table,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Box,
  Typography,
  Skeleton,
} from "@mui/material";
import { flexRender } from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import UnfoldMoreIcon from "@mui/icons-material/UnfoldMore";
import SearchOffIcon from "@mui/icons-material/SearchOff";
import {
  TABLE_DEFAULTS,
  ROW_SIZES,
  SKELETON_COLUMNS,
} from "../../constants/defaults";
import { alpha } from "@mui/material/styles";
import TableOptions from "../DisplayOptions/DisplayOptions";
import ColumnSelector from "../ColumnSelector/ColumnSelector";

const NoResultsFound = () => (
  <Box
    sx={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      py: 8,
      textAlign: "center",
      height: "100%",
      backgroundColor: "background.paper",
    }}
  >
    <SearchOffIcon
      sx={{
        fontSize: 80,
        color: "grey.300",
        mb: 2,
      }}
    />
    <Typography
      variant="h4"
      component="h2"
      sx={{
        fontWeight: "bold",
        color: "grey.700",
        mb: 1,
      }}
    >
      No models found
    </Typography>
    <Typography
      variant="body1"
      sx={{
        color: "grey.600",
        maxWidth: 450,
        mx: "auto",
      }}
    >
      Try modifying your filters or search to see more models.
    </Typography>
  </Box>
);

const TableSkeleton = ({ rowSize = "normal" }) => {
  const currentRowHeight = Math.floor(ROW_SIZES[rowSize]);
  const headerHeight = Math.floor(currentRowHeight * 1.25);
  const skeletonRows = 10;

  return (
    <TableContainer
      sx={{
        border: (theme) =>
          `1px solid ${alpha(
            theme.palette.divider,
            theme.palette.mode === "dark" ? 0.05 : 0.1
          )}`,
        borderRadius: 1,
      }}
    >
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            {SKELETON_COLUMNS.map((width, index) => (
              <TableCell
                key={index}
                sx={{
                  width,
                  minWidth: width,
                  height: `${headerHeight}px`,
                  padding: `${headerHeight * 0.25}px 16px`,
                  fontWeight: 400,
                  textAlign: index > 3 ? "right" : "left",
                  borderRight: (theme) => `1px solid ${theme.palette.divider}`,
                  "&:last-child": {
                    borderRight: "none",
                  },
                  position: "sticky",
                  top: 0,
                  backgroundColor: (theme) => theme.palette.background.paper,
                  zIndex: 2,
                }}
              />
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {[...Array(skeletonRows)].map((_, index) => (
            <TableRow
              key={index}
              sx={{
                height: `${currentRowHeight}px !important`,
                backgroundColor: (theme) =>
                  index % 2 === 0 ? "transparent" : theme.palette.action.hover,
              }}
            >
              {SKELETON_COLUMNS.map((width, cellIndex) => (
                <TableCell
                  key={cellIndex}
                  sx={{
                    width,
                    minWidth: width,
                    height: `${currentRowHeight}px`,
                    padding: `${currentRowHeight * 0.25}px 16px`,
                    borderRight: (theme) =>
                      `1px solid ${theme.palette.divider}`,
                    "&:last-child": {
                      borderRight: "none",
                    },
                  }}
                >
                  <Skeleton
                    variant={cellIndex === 1 ? "circular" : "text"}
                    width={cellIndex === 2 ? "60%" : "80%"}
                    height={
                      cellIndex === 1
                        ? Math.min(24, currentRowHeight - 4)
                        : Math.min(20, currentRowHeight - 8)
                    }
                    sx={{
                      transform: "none",
                      marginLeft: cellIndex > 3 ? "auto" : 0,
                      backgroundColor: (theme) =>
                        alpha(theme.palette.text.primary, 0.11),
                      "&::after": {
                        background: (theme) =>
                          `linear-gradient(90deg, ${alpha(
                            theme.palette.text.primary,
                            0.11
                          )}, ${alpha(
                            theme.palette.text.primary,
                            0.14
                          )}, ${alpha(theme.palette.text.primary, 0.11)})`,
                      },
                    }}
                  />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

const TableControls = React.memo(
  ({
    loading,
    rowSize,
    onRowSizeChange,
    scoreDisplay,
    onScoreDisplayChange,
    averageMode,
    onAverageModeChange,
    rankingMode,
    onRankingModeChange,
    hasTableOptionsChanges,
    searchParams,
    setSearchParams,
    table,
    handleColumnReset,
    hasColumnFilterChanges,
    onColumnVisibilityChange,
  }) => (
    <Box
      sx={{
        display: "flex",
        justifyContent: { xs: "center", md: "flex-end" },
        gap: 1,
        mb: 2,
        pt: { xs: 2, md: 0 },
      }}
    >
      <TableOptions
        loading={loading}
        rowSize={rowSize}
        onRowSizeChange={onRowSizeChange}
        scoreDisplay={scoreDisplay}
        onScoreDisplayChange={onScoreDisplayChange}
        averageMode={averageMode}
        onAverageModeChange={onAverageModeChange}
        rankingMode={rankingMode}
        onRankingModeChange={onRankingModeChange}
        hasChanges={hasTableOptionsChanges}
        searchParams={searchParams}
        setSearchParams={setSearchParams}
      />
      <ColumnSelector
        loading={loading}
        table={table}
        onReset={handleColumnReset}
        hasChanges={hasColumnFilterChanges}
        onColumnVisibilityChange={onColumnVisibilityChange}
      />
    </Box>
  )
);

TableControls.displayName = "TableControls";

const LeaderboardTable = ({
  table,
  rowSize = "normal",
  loading = false,
  hasTableOptionsChanges,
  hasColumnFilterChanges,
  onColumnVisibilityChange,
  scoreDisplay,
  onScoreDisplayChange,
  averageMode,
  onAverageModeChange,
  rankingMode,
  onRankingModeChange,
  onRowSizeChange,
  searchParams,
  setSearchParams,
  pinnedModels = [],
}) => {
  const { rows } = table.getRowModel();
  const parentRef = useRef(null);

  const currentRowHeight = useMemo(() => ROW_SIZES[rowSize], [rowSize]);
  const headerHeight = useMemo(
    () => Math.floor(currentRowHeight * 1.25),
    [currentRowHeight]
  );

  // Separate pinned rows from normal rows while preserving original order
  const pinnedRows = useMemo(() => {
    const pinnedModelRows = rows.filter((row) => row.original.isPinned);
    // Sort pinned models according to their original order in pinnedModels
    return pinnedModelRows.sort((a, b) => {
      const aIndex = pinnedModels.indexOf(a.original.id);
      const bIndex = pinnedModels.indexOf(b.original.id);
      return aIndex - bIndex;
    });
  }, [rows, pinnedModels]);

  const unpinnedRows = useMemo(
    () => rows.filter((row) => !row.original.isPinned),
    [rows]
  );
  const pinnedHeight = useMemo(
    () => pinnedRows.length * currentRowHeight,
    [pinnedRows.length, currentRowHeight]
  );

  const virtualizerOptions = useMemo(
    () => ({
      count: unpinnedRows.length,
      getScrollElement: () => parentRef.current,
      estimateSize: () => currentRowHeight,
      overscan: 15,
      scrollMode: "sync",
      scrollPaddingStart: pinnedHeight,
      scrollPaddingEnd: 0,
      initialRect: { width: 0, height: currentRowHeight * 15 },
    }),
    [currentRowHeight, unpinnedRows.length, pinnedHeight]
  );

  const rowVirtualizer = useVirtualizer(virtualizerOptions);

  const virtualRows = rowVirtualizer.getVirtualItems();

  // Adjust paddings to account for pinned rows
  const paddingTop = virtualRows.length > 0 ? virtualRows[0].start : 0;
  const paddingBottom =
    virtualRows.length > 0
      ? unpinnedRows.length * currentRowHeight -
        virtualRows[virtualRows.length - 1].end
      : 0;

  // Handle column reset
  const handleColumnReset = useCallback(() => {
    onColumnVisibilityChange(TABLE_DEFAULTS.COLUMNS.DEFAULT_VISIBLE);
  }, [onColumnVisibilityChange]);

  const cellStyles = (theme) => ({
    borderRight: `1px solid ${alpha(
      theme.palette.divider,
      theme.palette.mode === "dark" ? 0.05 : 0.1
    )}`,
    "&:last-child": {
      borderRight: "none",
    },
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    padding: "8px 16px",
  });

  const headerCellStyles = (theme) => ({
    ...cellStyles(theme),
    padding: "6px 16px",
    height: "36px",
    position: "sticky !important",
    top: 0,
    zIndex: 10,
    "& > .header-content": {
      display: "flex",
      alignItems: "center",
      width: "100%",
      gap: "4px",
      flexDirection: "row",
    },
  });

  const getSortingIcon = (column) => {
    if (
      column.id === "rank" ||
      column.id === "model_type" ||
      column.id === "isPinned"
    ) {
      return null;
    }

    if (!column.getIsSorted()) {
      return <UnfoldMoreIcon sx={{ fontSize: "1rem", opacity: 0.3 }} />;
    }
    return column.getIsSorted() === "desc" ? (
      <KeyboardArrowDownIcon sx={{ fontSize: "1rem" }} />
    ) : (
      <KeyboardArrowUpIcon sx={{ fontSize: "1rem" }} />
    );
  };

  const renderHeaderContent = (header) => {
    const sortIcon = getSortingIcon(header.column);
    return (
      <Box
        className="header-content"
        sx={{
          display: "flex",
          alignItems: "center",
          width: "100%",
          gap: "4px",
        }}
      >
        {flexRender(header.column.columnDef.header, header.getContext())}
        <Typography
          className="sort-icon"
          sx={{
            opacity: header.column.getIsSorted() ? 1 : 0.3,
            fontSize: "0.75rem",
            fontWeight: header.column.getIsSorted() ? 700 : 400,
            transition: "none 0.2s ease",
            display: "flex",
            alignItems: "center",
            visibility: sortIcon ? "visible" : "hidden",
            "&:hover": {
              opacity: 1,
            },
          }}
        >
          {sortIcon || <UnfoldMoreIcon sx={{ fontSize: "1rem" }} />}
        </Typography>
      </Box>
    );
  };

  const renderRow = (row, isSticky = false, stickyIndex = 0) => {
    // Get row index in the sorted data model
    const sortedIndex = table
      .getSortedRowModel()
      .rows.findIndex((r) => r.id === row.id);

    return (
      <TableRow
        key={row.id}
        sx={(theme) => ({
          height: `${currentRowHeight}px !important`,
          backgroundColor: isSticky
            ? theme.palette.background.paper
            : (sortedIndex + 1) % 2 === 0
            ? "transparent"
            : alpha(theme.palette.mode === "dark" ? "#fff" : "#000", 0.02),
          position: isSticky ? "sticky" : "relative",
          top: isSticky
            ? `${headerHeight + stickyIndex * currentRowHeight}px`
            : "auto",
          zIndex: isSticky ? 2 : 1,
          boxShadow: isSticky
            ? `0 1px 1px ${alpha(
                theme.palette.common.black,
                theme.palette.mode === "dark" ? 0.1 : 0.05
              )}`
            : "none",
          "&::after": isSticky
            ? {
                content: '""',
                position: "absolute",
                left: 0,
                right: 0,
                height: "1px",
                bottom: -1,
                backgroundColor: alpha(
                  theme.palette.divider,
                  theme.palette.mode === "dark" ? 0.1 : 0.2
                ),
                zIndex: 1,
              }
            : {},
        })}
      >
        {row.getVisibleCells().map((cell) => (
          <TableCell
            key={cell.id}
            sx={(theme) => ({
              width: `${cell.column.columnDef.size}px !important`,
              minWidth: `${cell.column.columnDef.size}px !important`,
              height: `${currentRowHeight}px`,
              backgroundColor: isSticky
                ? theme.palette.background.paper
                : "inherit",
              borderBottom: isSticky
                ? "none"
                : `1px solid ${theme.palette.divider}`,
              ...cellStyles(theme),
              ...(cell.column.columnDef.meta?.cellStyle?.(cell.getValue()) ||
                {}),
              "& .MuiBox-root": {
                overflow: "visible",
              },
            })}
          >
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </TableCell>
        ))}
      </TableRow>
    );
  };

  if (!loading && (!rows || rows.length === 0)) {
    return (
      <Box sx={{ width: "100%" }}>
        <TableControls
          loading={loading}
          rowSize={rowSize}
          onRowSizeChange={onRowSizeChange}
          scoreDisplay={scoreDisplay}
          onScoreDisplayChange={onScoreDisplayChange}
          averageMode={averageMode}
          onAverageModeChange={onAverageModeChange}
          rankingMode={rankingMode}
          onRankingModeChange={onRankingModeChange}
          hasTableOptionsChanges={hasTableOptionsChanges}
          searchParams={searchParams}
          setSearchParams={setSearchParams}
          table={table}
          handleColumnReset={handleColumnReset}
          hasColumnFilterChanges={hasColumnFilterChanges}
          onColumnVisibilityChange={onColumnVisibilityChange}
        />
        <Paper
          sx={{
            height: "calc(100vh - 380px)",
            minHeight: "500px",
            resize: "vertical",
            overflow: "hidden",
            boxShadow: "none",
            backgroundColor: "background.paper",
            borderRadius: 1,
          }}
        >
          <NoResultsFound />
        </Paper>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ width: "100%" }}>
        <TableControls
          loading={loading}
          rowSize={rowSize}
          onRowSizeChange={onRowSizeChange}
          scoreDisplay={scoreDisplay}
          onScoreDisplayChange={onScoreDisplayChange}
          averageMode={averageMode}
          onAverageModeChange={onAverageModeChange}
          rankingMode={rankingMode}
          onRankingModeChange={onRankingModeChange}
          hasTableOptionsChanges={hasTableOptionsChanges}
          searchParams={searchParams}
          setSearchParams={setSearchParams}
          table={table}
          handleColumnReset={handleColumnReset}
          hasColumnFilterChanges={hasColumnFilterChanges}
          onColumnVisibilityChange={onColumnVisibilityChange}
        />
        <Paper
          sx={{
            borderRadius: 1,
            overflow: "hidden",
          }}
        >
          <TableSkeleton rowSize={rowSize} />
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%" }}>
      <TableControls
        loading={loading}
        rowSize={rowSize}
        onRowSizeChange={onRowSizeChange}
        scoreDisplay={scoreDisplay}
        onScoreDisplayChange={onScoreDisplayChange}
        averageMode={averageMode}
        onAverageModeChange={onAverageModeChange}
        rankingMode={rankingMode}
        onRankingModeChange={onRankingModeChange}
        hasTableOptionsChanges={hasTableOptionsChanges}
        searchParams={searchParams}
        setSearchParams={setSearchParams}
        table={table}
        handleColumnReset={handleColumnReset}
        hasColumnFilterChanges={hasColumnFilterChanges}
        onColumnVisibilityChange={onColumnVisibilityChange}
      />
      <Paper
        elevation={0}
        sx={{
          height: "calc(100vh - 380px)",
          minHeight: "500px",
          resize: "vertical",
          overflow: "hidden",
          boxShadow: "none",
          backgroundColor: "background.paper",
          borderRadius: 1,
          "&:hover::after": {
            opacity: 1,
          },
        }}
      >
        <TableContainer
          ref={parentRef}
          sx={(theme) => ({
            height: "100%",
            overflow: "auto",
            border: "none",
            boxShadow: "none",
            "&::-webkit-scrollbar": {
              width: "8px",
              height: "8px",
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: alpha(
                theme.palette.common.black,
                theme.palette.mode === "dark" ? 0.4 : 0.2
              ),
              borderRadius: "4px",
            },
            "&::-webkit-scrollbar-corner": {
              backgroundColor: theme.palette.background.paper,
            },
            willChange: "transform",
            transform: "translateZ(0)",
            WebkitOverflowScrolling: "touch",
            scrollBehavior: "auto",
          })}
        >
          <Table
            sx={{
              margin: 0,
              width: "100%",
              borderCollapse: "separate",
              borderSpacing: 0,
              tableLayout: pinnedRows.length > 0 ? "fixed" : "fixed",
              border: "none",
              "& td, & th":
                pinnedRows.length > 0
                  ? {
                      width: `${100 / table.getAllColumns().length}%`,
                    }
                  : {},
            }}
          >
            <colgroup>
              {table.getAllColumns().map((column, index) => (
                <col
                  key={column.id}
                  style={
                    index < 4
                      ? {
                          width: column.columnDef.size,
                          minWidth: column.columnDef.size,
                          maxWidth: column.columnDef.size,
                        }
                      : {
                          minWidth: column.columnDef.size,
                          width: `${100 / (table.getAllColumns().length - 4)}%`,
                        }
                  }
                />
              ))}
            </colgroup>

            <TableHead
              sx={{
                position: "sticky",
                top: 0,
                zIndex: 10,
                backgroundColor: (theme) => theme.palette.background.paper,
                "& th": {
                  backgroundColor: (theme) => theme.palette.background.paper,
                },
              }}
            >
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableCell
                      key={header.id}
                      onClick={header.column.getToggleSortingHandler()}
                      data-column={header.column.accessorKey}
                      sx={(theme) => ({
                        cursor: header.column.getCanSort()
                          ? "pointer"
                          : "default",
                        width: header.column.columnDef.size,
                        minWidth: header.column.columnDef.size,
                        ...headerCellStyles(theme),
                        textAlign: "left",
                        fontWeight: header.column.getIsSorted() ? 700 : 400,
                        userSelect: "none",
                        height: `${headerHeight}px`,
                        padding: `${headerHeight * 0.25}px 16px`,
                        backgroundColor: theme.palette.background.paper,
                      })}
                    >
                      {renderHeaderContent(header)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableHead>

            <TableBody>
              {/* Pinned rows */}
              {pinnedRows.map((row, index) => renderRow(row, true, index))}

              {/* Padding for virtualized rows */}
              {paddingTop > 0 && (
                <TableRow>
                  <TableCell
                    colSpan={table.getAllColumns().length}
                    style={{
                      height: `${paddingTop}px`,
                      padding: 0,
                      border: "none",
                      backgroundColor: "transparent",
                    }}
                  />
                </TableRow>
              )}

              {/* Virtualized unpinned rows */}
              {virtualRows.map((virtualRow) => {
                const row = unpinnedRows[virtualRow.index];
                if (!row) return null;
                return renderRow(row);
              })}

              {/* Bottom padding */}
              {paddingBottom > 0 && (
                <TableRow>
                  <TableCell
                    colSpan={table.getAllColumns().length}
                    style={{
                      height: `${paddingBottom}px`,
                      padding: 0,
                      border: "none",
                    }}
                  />
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export { TableSkeleton };
export default LeaderboardTable;

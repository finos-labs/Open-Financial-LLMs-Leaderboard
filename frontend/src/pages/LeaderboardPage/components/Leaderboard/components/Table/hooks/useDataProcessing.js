import { useMemo } from "react";
import {
  useReactTable,
  getSortedRowModel,
  getCoreRowModel,
  getFilteredRowModel,
} from "@tanstack/react-table";
import { createColumns } from "../../../utils/columnUtils";
import {
  useAverageRange,
  useColorGenerator,
  useProcessedData,
  useFilteredData,
  useColumnVisibility,
} from "../../../hooks/useDataUtils";

export const useDataProcessing = (
  data,
  searchValue,
  selectedPrecisions,
  selectedTypes,
  paramsRange,
  selectedBooleanFilters,
  sorting,
  rankingMode,
  averageMode,
  visibleColumns,
  scoreDisplay,
  pinnedModels,
  onTogglePin,
  setSorting,
  isOfficialProviderActive
) => {
  // Call hooks directly at root level
  const { minAverage, maxAverage } = useAverageRange(data);
  const getColorForValue = useColorGenerator(minAverage, maxAverage);
  const processedData = useProcessedData(data, averageMode, visibleColumns);
  const columnVisibility = useColumnVisibility(visibleColumns);

  // Memoize filters
  const filterConfig = useMemo(
    () => ({
      selectedPrecisions,
      selectedTypes,
      paramsRange,
      searchValue,
      selectedBooleanFilters,
      rankingMode,
      pinnedModels,
      isOfficialProviderActive,
    }),
    [
      selectedPrecisions,
      selectedTypes,
      paramsRange,
      searchValue,
      selectedBooleanFilters,
      rankingMode,
      pinnedModels,
      isOfficialProviderActive,
    ]
  );

  // Call useFilteredData at root level
  const filteredData = useFilteredData(
    processedData,
    filterConfig.selectedPrecisions,
    filterConfig.selectedTypes,
    filterConfig.paramsRange,
    filterConfig.searchValue,
    filterConfig.selectedBooleanFilters,
    filterConfig.rankingMode,
    filterConfig.pinnedModels,
    filterConfig.isOfficialProviderActive
  );

  // Memoize columns creation
  const columns = useMemo(
    () =>
      createColumns(
        getColorForValue,
        scoreDisplay,
        columnVisibility,
        data.length,
        averageMode,
        searchValue,
        rankingMode,
        onTogglePin
      ),
    [
      getColorForValue,
      scoreDisplay,
      columnVisibility,
      data.length,
      averageMode,
      searchValue,
      rankingMode,
      onTogglePin,
    ]
  );

  // Memoize table configuration
  const tableConfig = useMemo(
    () => ({
      data: filteredData,
      columns,
      state: {
        sorting: Array.isArray(sorting) ? sorting : [],
        columnVisibility,
      },
      getCoreRowModel: getCoreRowModel(),
      getFilteredRowModel: getFilteredRowModel(),
      getSortedRowModel: getSortedRowModel(),
      onSortingChange: setSorting,
      enableColumnVisibility: true,
      defaultColumn: {
        sortingFn: (rowA, rowB, columnId) => {
          const isDesc = sorting?.[0]?.desc;

          if (rowA.original.isPinned && rowB.original.isPinned) {
            return (
              pinnedModels.indexOf(rowA.original.id) -
              pinnedModels.indexOf(rowB.original.id)
            );
          }

          if (isDesc) {
            if (rowA.original.isPinned) return -1;
            if (rowB.original.isPinned) return 1;
          } else {
            if (rowA.original.isPinned) return -1;
            if (rowB.original.isPinned) return 1;
          }

          const aValue = rowA.getValue(columnId);
          const bValue = rowB.getValue(columnId);

          if (typeof aValue === "number" && typeof bValue === "number") {
            return aValue - bValue;
          }

          return String(aValue).localeCompare(String(bValue));
        },
      },
    }),
    [filteredData, columns, sorting, columnVisibility, pinnedModels, setSorting]
  );

  const table = useReactTable(tableConfig);

  return {
    table,
    minAverage,
    maxAverage,
    getColorForValue,
    processedData,
    filteredData,
    columns,
    columnVisibility,
  };
};

export const typeColumnSort = (rowA, rowB) => {
  const aValue = rowA.getValue("model_type");
  const bValue = rowB.getValue("model_type");

  // If both values are arrays, compare their first elements
  if (Array.isArray(aValue) && Array.isArray(bValue)) {
    return String(aValue[0] || "").localeCompare(String(bValue[0] || ""));
  }

  // If one is array and other isn't, array comes first
  if (Array.isArray(aValue)) return -1;
  if (Array.isArray(bValue)) return 1;

  // If neither is array, compare as strings
  return String(aValue || "").localeCompare(String(bValue || ""));
};

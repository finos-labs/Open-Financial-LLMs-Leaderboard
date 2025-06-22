// Utility function to detect if a string looks like a regex
export const looksLikeRegex = (str) => {
  const regexSpecialChars = /[\\^$.*+?()[\]{}|]/;
  return regexSpecialChars.test(str);
};

// Function to map search fields to correct paths
const getFieldPath = (field) => {
  const fieldMappings = {
    precision: "model.precision",
    architecture: "model.architecture",
    license: "metadata.hub_license",
    type: "model.type",
  };
  return fieldMappings[field] || field;
};

// Function to extract special searches and normal text
export const parseSearchQuery = (query) => {
  const specialSearches = [];
  let remainingText = query;

  // Look for all @field:value patterns
  const prefixRegex = /@\w+:/g;
  const matches = query.match(prefixRegex) || [];

  matches.forEach((prefix) => {
    const regex = new RegExp(`${prefix}([^\\s@]+)`, "g");
    remainingText = remainingText.replace(regex, (match, value) => {
      const field = prefix.slice(1, -1);
      specialSearches.push({
        field: getFieldPath(field),
        displayField: field,
        value,
      });
      return "";
    });
  });

  return {
    specialSearches,
    textSearch: remainingText.trim(),
  };
};

// Function to extract simple text search
export const extractTextSearch = (searchValue) => {
  return searchValue
    .split(";")
    .map((query) => {
      const { textSearch } = parseSearchQuery(query);
      return textSearch;
    })
    .filter(Boolean)
    .join(";");
};

// Utility function to access nested object properties
export const getValueByPath = (obj, path) => {
  return path.split(".").reduce((acc, part) => acc?.[part], obj);
};

// Function to generate natural language description of the search
export const generateSearchDescription = (searchValue) => {
  if (!searchValue) return null;

  const searchGroups = searchValue
    .split(";")
    .map((group) => group.trim())
    .filter(Boolean);

  return searchGroups.map((group, index) => {
    const { specialSearches, textSearch } = parseSearchQuery(group);

    let parts = [];
    if (textSearch) {
      parts.push(textSearch);
    }

    if (specialSearches.length > 0) {
      const specialParts = specialSearches.map(
        ({ displayField, value }) => `@${displayField}:${value}`
      );
      parts = parts.concat(specialParts);
    }

    return {
      text: parts.join(" "),
      index,
    };
  });
};

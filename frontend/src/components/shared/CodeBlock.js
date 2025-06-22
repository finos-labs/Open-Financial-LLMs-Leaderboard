import React from 'react';
import { Box, IconButton } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const CodeBlock = ({ code }) => (
  <Box sx={{ position: 'relative' }}>
    <IconButton
      onClick={() => navigator.clipboard.writeText(code)}
      sx={{
        position: 'absolute',
        top: 8,
        right: 8,
        color: 'grey.500',
        '&:hover': { color: 'grey.300' },
      }}
    >
      <ContentCopyIcon fontSize="small" />
    </IconButton>
    <Box
      sx={{
        backgroundColor: 'grey.900',
        color: 'grey.100',
        p: 2,
        borderRadius: 1,
        fontFamily: 'monospace',
        fontSize: '0.875rem',
        overflowX: 'auto',
        textAlign: 'left',
        whiteSpace: 'pre',
      }}
    >
      {code}
    </Box>
  </Box>
);

export default CodeBlock; 
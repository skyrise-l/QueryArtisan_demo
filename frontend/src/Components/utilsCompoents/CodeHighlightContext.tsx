// CodeHighlightContext.tsx
import React from 'react';

type CodeHighlightContextType = {
  highlightedLines: Set<number>;
  setHighlightedLines: (lines: Set<number>) => void;
};

export const CodeHighlightContext = React.createContext<CodeHighlightContextType>({
  highlightedLines: new Set<number>(),
  setHighlightedLines: () => {},
});

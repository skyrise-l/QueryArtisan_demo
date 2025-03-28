import React from 'react';

interface SearchPromptProps {
  height: string;
}

const SearchPrompt: React.FC<SearchPromptProps> = ({ height }) => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center', 
      alignItems: 'center', 
      height: height,  // 确保这里获取到正确的 height 值
    }}>
      <div style={{
        textAlign: 'center',
        padding: '20px',
        fontSize: '18px',
        color: '#555',
        border: '2px dashed #bbb',
        borderRadius: '10px',
      }}>
        Please enter a query and click <b>Query</b> to begin.
      </div>
    </div>
  );
};

export default SearchPrompt;

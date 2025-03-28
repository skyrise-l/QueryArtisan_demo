import React, { useEffect, useState, useContext, useRef } from 'react';
import axios from 'axios';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import 'highlight.js/styles/github.css';
import { CodeHighlightContext } from '../utilsCompoents/CodeHighlightContext';
import "./CodeDisplay.css";
import SearchPrompt from '../utilsCompoents/SearchPrompt';

hljs.registerLanguage('python', python);

const BASE_URL = 'http://127.0.0.1:8080/api/Home';

interface CodeDisplayProps {
  id: string;
  hasSearched: boolean;
  preContainerClassName?: string;
}

const CodeDisplay: React.FC<CodeDisplayProps> = ({ id, hasSearched, preContainerClassName }) => {
  const [code, setCode] = useState<string[]>([]);
  const { highlightedLines } = useContext(CodeHighlightContext);
  const [highlightedCode, setHighlightedCode] = useState<string[]>([]);
  const lineRefs = useRef<(HTMLDivElement | null)[]>([]);
  const { setHighlightedLines } = useContext(CodeHighlightContext);
  const [cardPosition, setCardPosition] = useState<{ top: number; left: number } | null>(null);

  useEffect(() => {
    const fetchCode = async () => {
      try {
        const response = await axios.get(`${BASE_URL}/GetCode`, { params: { QueryId: id } });
        if (response.data.code === 0) {
          const codeString: string = response.data.data;
          setCode(codeString.split('\n'));
        } else {
          console.error('Failed to fetch code:', response.data.message);
        }
      } catch (error) {
        console.error('Error while fetching code:', error);
      }
    };
    setHighlightedLines(new Set([]));
    fetchCode();
  }, []);

  useEffect(() => {
    const highlighted = hljs.highlight(code.join('\n'), { language: 'python' }).value;
    setHighlightedCode(highlighted.split('\n'));
  }, [code]);

  useEffect(() => {
    if (highlightedLines.size > 0 && lineRefs.current.length > 0) {
      const firstHighlightLine = Math.min(...Array.from(highlightedLines));
      const targetLineEl = lineRefs.current[firstHighlightLine - 1];
      if (targetLineEl) {
        targetLineEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        const rect = targetLineEl.getBoundingClientRect();
        setCardPosition({
          top: rect.top + window.scrollY, 
          left: rect.right + 20, 
        });
      }
    }
  }, [highlightedLines, highlightedCode]);

  const decodeEntities = (encodedString: string) => {
    const textArea = document.createElement("textarea");
    textArea.innerHTML = encodedString;
    return textArea.value;
  };

  // 获取第一个高亮行的位置
  const firstHighlightedLine = Math.min(...Array.from(highlightedLines));
  const firstHighlightedRef = lineRefs.current[firstHighlightedLine - 1];
 
  return (
    <div className="code-display-container">

      {hasSearched ? (
        <SearchPrompt height="420px" />
      ) : (
        <div style={{ position: 'relative' }}>
          <pre className={preContainerClassName || "pre-container"}>
            <code className="python">
              {highlightedCode.map((htmlLine, index) => {
                const lineNumber = index + 1;
                const isHighlighted = highlightedLines.has(lineNumber);
                return (
                  <div
                    key={index}
                    ref={(el) => (lineRefs.current[index] = el)}
                    className={`line ${isHighlighted ? 'highlighted-line' : ''}`}
                    title={decodeEntities(htmlLine.replace(/<[^>]*>/g, ""))}
                  >
                    <span className="line-number">{lineNumber}</span>
                    <span dangerouslySetInnerHTML={{ __html: htmlLine }} />
                  </div>
                );
              })}
            </code>
          </pre>
          {/* 显示高亮行详细内容的浮动卡片 */}
          {highlightedLines.size > 0 && cardPosition && (
            <div
              className="highlight-card"
              style={{
                position: 'absolute',
                top: 200,
                left: 40,
                width: 400,
              }}
            >

              {Array.from(highlightedLines).map((lineNumber) => (
                <p key={lineNumber}>
                  {decodeEntities(highlightedCode[lineNumber - 1]?.replace(/<[^>]*>/g, ""))}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeDisplay;

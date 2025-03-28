import React, { useState, useEffect } from 'react';
import FlowChart from './FlowChart';
import CodeDisplay from './CodeDisplay';
import "./ProcessPage.css"
import { CodeHighlightContext } from '../utilsCompoents/CodeHighlightContext';

interface ChatMessage {
    author: "user" | "system";
    message: string;
    timestamp: number;
  }
  
  interface QueryHistory {
    id: string;
    query: string;
    executeTime: number;
    decomposeQueryArray: string;    
    decomposeAnalysisArray: string; 
    command: string
  }

interface ProcessPagePageProps {
    id: string;
}

const ProceePage: React.FC<ProcessPagePageProps> = ({ id }) => {

    const [highlightedLines, setHighlightedLines] = useState<Set<number>>(new Set());
      const [currentQuery, setCurrentQuery] = useState<string>("");
      const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
      const [queryBreakdown, setQueryBreakdown] = useState<string[]>([]);
      const [analysisBreakdown, setAnalysisBreakdown] = useState<string[]>([]);
      const [loading, setLoading] = useState<boolean>(true);
    
    
      useEffect(() => {

        console.log(id);
        // 清理或重置数据
        setLoading(true);
        setCurrentQuery("");
        setChatHistory([]);
        setQueryBreakdown([]);
        setAnalysisBreakdown([]);
    
        fetch(`http://127.0.0.1:8080/api/Report/GetFullChat?QueryId=${id}`)
          .then((res) => res.json())
          .then((resData) => {
            if (resData.code === 0 && resData.data) {
              const data: QueryHistory = resData.data;
    
              let parsedMessages: ChatMessage[] = [];
              if (data.command) {
                try {
                  parsedMessages = JSON.parse(data.command) as ChatMessage[];
                } catch (err) {
                  console.error("解析 messages 出错：", err);
                }
                setChatHistory(parsedMessages);
              }
    
              setCurrentQuery(data.query);
    
              let parsedQueryArray: string[] = [];
              let parsedAnalysisArray: string[] = [];
              try {
                parsedQueryArray = JSON.parse(data.decomposeQueryArray);
                parsedAnalysisArray = JSON.parse(data.decomposeAnalysisArray);
              } catch (err) {
                console.error("解析分解内容出错：", err);
              }
    
              setQueryBreakdown(parsedQueryArray);
              setAnalysisBreakdown(parsedAnalysisArray);
            } else {
              console.error("接口返回错误或者 data 为空：", resData);
            }
          })
          .catch((err) => {
            console.error("请求失败：", err);
          })
          .finally(() => {
            setLoading(false);
          });
      }, [id]);
    


    return (
        <CodeHighlightContext.Provider value={{ highlightedLines, setHighlightedLines }}>
            <div className="process-page-container">

                <div className="TaskDecompose-grid">
                  <div className="DataLineage-header">
                      <div className="DataLineage-title2">Task Decompose</div>
                  </div>
           

                    <div className="scrollable-container">
                    {/* Query Breakdown */}
                    <div className="breakdown-section">
                        <div className="breakdown-content">
                        {loading ? (
                            <div className="breakdown-item">Loading...</div>
                        ) : queryBreakdown.length > 0 ? (
                            queryBreakdown.map((subQuery, index) => (
                            <div key={index} className="breakdown-item">
                                <strong>Query {index + 1}:</strong> {subQuery}
                            </div>
                            ))
                        ) : (
                            <div className="breakdown-item">No query breakdown</div>
                        )}
                        </div>
                    </div>

                    {/* Divider */}
                    <div className="divider"></div>

                    {/* Analysis Breakdown */}
                    <div className="breakdown-section">
                        <div className="breakdown-content">
                        {loading ? (
                            <div className="breakdown-item">Loading...</div>
                        ) : analysisBreakdown.length > 0 ? (
                            analysisBreakdown.map((analysis, index) => (
                            <div key={index} className="breakdown-item">
                                <strong>Analysis {index + 1}:</strong> {analysis}
                            </div>
                            ))
                        ) : (
                            <div className="breakdown-item">No analysis breakdown</div>
                        )}
                        </div>
                    </div>
                    </div>
                </div>

                <div className="CodeDisplay-grid">
                  <div className="DataLineage-header">
                      <div className="DataLineage-title2">Generated Code</div>
                  </div>
        
                    <CodeDisplay id={id!} hasSearched={false} preContainerClassName="pre-container_report" /> 
                </div>

                {/* 第三块区域：占据第二行的第二列及之后的区域 */}
                <div className="FlowChart-grid">
                  <div className="DataLineage-header">
                      <div className="DataLineage-title2">Query Graph and Optimization</div>
                  </div>

                    <FlowChart id={id} />
                </div>
            </div>
        </CodeHighlightContext.Provider>
    );
};

export default ProceePage;

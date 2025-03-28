import React, { useState, useEffect } from 'react';
import './ReportPage.css';
import DataLineage from "./DataLineage"
import AnalyzeResult from "./AnalyzeResult";
import axios from "axios";

interface ReportPagePageProps {
  id: string;
}

// 主报告页面
const ReportPage: React.FC<ReportPagePageProps> = ({ id }) => {
  const [currentQuery, setCurrentQuery] = useState<string>("");
  // 状态管理
  const [query, setQuery] = useState<string>('');  // 输入框内容
  const [loading, setLoading] = useState<boolean>(false); // 是否加载中
  const [refreshKey, setRefreshKey] = useState<number>(0); // 用于强制刷新子组件

  const [codeResult, setCodeResult] = useState("");
  const [LLMResult, setLLMResult] = useState("");
  const [images, setImages] = useState<string[]>([]); 
  const [code_result, setCode_result] = useState<any[]>([]); 

  
  const [commandHistory, setCommandHistory] = useState<String[]>([]);
  
  // 处理回车事件
  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      await sendQuery();
    }
  };

  const fetchData = async (id:string) => {
    setLoading(true); // Start loading animation
    
    try {
      // Fetch code result data
      const codeResultResponse = await axios.get(`http://127.0.0.1:8080/api/Report/code_result?QueryId=${id}`);
      const { code_output, llm_result, images, code_result } = codeResultResponse.data.data;
      setCodeResult(code_output);
      setLLMResult(llm_result);
      setImages(images || []);
      setCode_result(Array.isArray(code_result) ? code_result : []);
      
      // Fetch command history
      const commandHistoryResponse = await fetch(`http://127.0.0.1:8080/api/Report/getCommandHistory?QueryId=${id}`);
      const resData = await commandHistoryResponse.json();
      if (resData.code === 0 && resData.data) {
        const { history, current_query } = resData.data;
        if (Array.isArray(history)) {
          setCommandHistory(history);
        } else {
          console.error("历史命令数据格式错误：", history);
        }

        if (current_query) {
          setCurrentQuery(current_query);
        } else {
          console.error("当前查询数据缺失");
        }
      } else {
        console.error("获取历史命令失败：", resData);
      }
    } catch (error) {
      console.error("请求错误:", error);
    } finally {
      setLoading(false); // Stop loading animation
    }
  };


  const sendQuery = async () => {
    if (!query.trim()) return;

    setLoading(true); // 显示加载动画

    try {
      const response = await fetch('http://127.0.0.1:8080/api/Report/sendCommand', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, query }),
      });

      const data = await response.json();
      fetchData(id)
      setRefreshKey(prev => prev + 1); 
    } catch (error) {
      console.error('请求错误:', error);
    } finally {
      setLoading(false); // 隐藏加载动画
      setQuery(''); // 清空输入框
    }
  };
    
  useEffect(() => {
    fetchData(id)
  }, [id]);

    

  return (
      <div className="Report-container">

      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
        </div>
      )}

        <div className="command-grid">
            <div className="DataLineage-header">
                <div className="DataLineage-title2">Command Chat</div>
            </div>


              <div className="query-content">
                <strong>Current Query:</strong> {currentQuery}
              </div>

          

              <div className="command-content">
                {commandHistory.length > 0 ? (
                  commandHistory.map((cmd, idx) => (
                    <div key={idx} className="command-item">
                      <div className="command-header">
                        <strong>History Command {idx + 1}:</strong>
                      </div>
                      <div className="command-body">
                        {cmd}
                      </div>
          
                    </div>
                  ))
                ) : (
                  <div className="no-command">No command</div>
                )}
              </div>

              <div className="input-container">
                <input
                  type="text"
                  placeholder="Input any command..."
                  className="query-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <button className="history-btn" onClick={sendQuery}>ENTER</button>
              </div>

        </div>





        <div className="dataline-grid">
            <DataLineage id={id!} code_result={code_result} key={refreshKey} />
        </div>

        <div className="Anlysis-result-grid">
          <AnalyzeResult id={id!} images={images} codeResult={codeResult} LLMResult={LLMResult}  key={refreshKey}/>
        </div>

      </div>
  );
};

export default ReportPage;

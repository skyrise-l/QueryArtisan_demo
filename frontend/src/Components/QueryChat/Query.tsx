import React, { useState, useEffect, ReactNode } from 'react';
import CustomSearch from './CustomSearch';
import BatchQueryComponent from './BatchQueryComponent';
import QueryReuse from './QueryReuse';
import ApplyButton from '../utilsCompoents/ApplyButton';
import '../utilsCompoents/ApplyButton.css';
import "./Query.css";
import { Select,Popover  } from 'antd';

interface ChatMessage {
  author: 'user' | 'system';
  message: string;
  timestamp: number;
}

interface QueryData {
  id: string;
  title: string;
  hashValue: string;
  messages: ChatMessage[];
  query_id: string;
}

interface ChatComponentProps {
  onQueryIdChange?: (queryId: string) => void; 
}


const ChatComponent: React.FC<ChatComponentProps> = ({ onQueryIdChange }) => {

  const { Option } = Select;
  const [searchText, setSearchText] = useState<string>('');
  const [showBatchQuery, setShowBatchQuery] = useState<boolean>(false); 
  const [ShowQueryReuse, setShowQueryReuse] = useState<boolean>(false);
  const [ShowCustomTools, setShowTaskAnalyzer] = useState<boolean>(false);
  const [titles, setTitles] = useState<QueryData[]>([]);
  const [queryData, setQueryData] = useState<QueryData>({
    id: "0x0",
    title: 'New Title',
    hashValue: '',  
    messages: [],
    query_id: ""
  });


  const handleBatchQueryClick = () => {
    setShowBatchQuery(true);  
  };

  const handleHistoryReuseClick = () => {
    setShowQueryReuse(true);
  };

  const handleCustomToolsClick = () => {
    setShowTaskAnalyzer(true);
  };


  const handleSearchTextChange = (newText: string) => {
    setSearchText(newText);  
  };

  const renderMessageText = (msg: ChatMessage): ReactNode => {
    // 只处理 user 发送的消息
    if (msg.author !== 'system') {
      return msg.message;
    }
  
    // 正则匹配 "Please check the report:" 后的 UUID
    const reportIdRegex = /\b(?:please check the report|check report)\s*:\s*([a-f0-9\-]{36})\b/gi;
    let match;
    const result: ReactNode[] = [];
    let lastIndex = 0;
  
    // 使用 while + exec() 兼容低版本 TypeScript

    while ((match = reportIdRegex.exec(msg.message)) !== null) {
      const reportId = match[1]; // 获取 UUID
      const matchIndex = match.index || 0;
  
      // 追加 UUID 之前的普通文本
      result.push(msg.message.substring(lastIndex, matchIndex));
  
      // 追加超链接
      result.push(
        <a
          key={`link-${reportId}`}
          href={`http://127.0.0.1:3000/report/${reportId}`}
          style={{ color: 'blue', textDecoration: 'underline' }}
          target="_blank"
          rel="noopener noreferrer"
        >
          {reportId}
        </a>
      );
  
      lastIndex = matchIndex + match[0].length; // 更新 lastIndex
    }
  
    // 添加剩余的文本部分
    result.push(msg.message.substring(lastIndex));
  
    return <>{result}</>;
  };
  

  useEffect(() => {
    const fetchTitles = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8080/api/Home/GetTitles');
        const data = await response.json();
        if (data.code === 0) {
          // 这里 data.data 应该是一个 QueryData[] 列表
          setTitles(data.data || []);
        } else {
          throw new Error(data.message);
        }
      } catch (error) {
        console.error("Error fetching titles:", error);
      }
    };
    fetchTitles();
  });


  const handleTitleChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = event.target.value;  // Get the selected value from the event
    if (selectedId === '0x0') {
      setQueryData({
        id: '0x0',
        title: 'New Title',
        hashValue: '',
        messages: [],
        query_id: ""
      });
    } else {
      console.log(selectedId)
      const selectedTitle = titles.find(t => t.id === selectedId);
      if (selectedTitle) {
        try {
          const chatResponse = await fetch(`http://127.0.0.1:8080/api/Home/GetChat?QueryId=${selectedTitle.id}`);
          const chatData = await chatResponse.json();
          if (chatData.code === 0) {
            setQueryData(chatData.data); 
          } 
          if (onQueryIdChange) {
            onQueryIdChange(chatData.data.query_id);
          }
        } catch (error) {
          console.error('Failed to fetch chat history:', error);
        }
      }
    }
  };

  const sendMessage = async (inputValue: string) => {
    const userMessage: ChatMessage = {
      author: 'user',
      message: inputValue.trim(),
      timestamp: Date.now(),
    };
    if (!userMessage.message) {
      return;
    }

    const tempSystemMessage: ChatMessage = {
      author: 'system',
      message: 'System searching, please waitting...',
      timestamp: Date.now() + 1, 
    };


    try {
      const requestBody = {
        id: queryData.id,
        title: queryData.title,
        hashValue: queryData.hashValue,
        messages: [...queryData.messages, userMessage],
        query_id: queryData.query_id
      };
      

      setQueryData(prevState => ({
        ...prevState,
        messages: [...prevState.messages, userMessage, tempSystemMessage],
      }));

      const response = await fetch('http://127.0.0.1:8080/api/Home/Query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const responseData = await response.json();
      if (responseData.code === 0 && responseData.data) {
        setQueryData(prevState => ({
          ...prevState,
          messages: [...prevState.messages.slice(0, -2), ...responseData.data.messages],
          id: responseData.data.id,
          title: responseData.data.title,
          hashValue: responseData.data.hashValue,
          query_id: responseData.data.query_id
        }));
        
        if (onQueryIdChange) {
          onQueryIdChange(responseData.data.query_id);
        }
      } else {
        console.error('Failed to load messages:', responseData.message);
      }
    } catch (error) {
      console.error('Failed to send message', error);
    } 
  };


  return (
    <div className="chat-container">
      {/* Query Chat Header */}
      <div className="query-header">
        <div className="query-header-content">
          <img src="/think.png" alt="icon" className="query-icon" />
          <h2 className="query-title">Query Chat</h2>
        </div>
        <div className="menu-bar">
          {/* Batch Query Button */}
          <ApplyButton
            tooltip="Batch Query"
            onClick={handleBatchQueryClick}
            className="allpy-button-QueryChatMenu"
          />
          <ApplyButton
            tooltip="Query Reuse"
            onClick={handleHistoryReuseClick}
            className="allpy-button-QueryChatMenu"
          />
          <div className="query-dropdown">
            <select
              value={queryData.id} 
              onChange={handleTitleChange}
            >
              <option value="0x0">New Title</option>
              {titles.map((title) => (
                <option key={title.id} value={title.id}>
                  {title.title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>



      {/* 分割线，适应背景与输入框区域的分割 */}
      <div className="background-divider"></div>

      {showBatchQuery && (
        <BatchQueryComponent closeBatchQuery={() => setShowBatchQuery(false)} /> 
      )}

      {ShowQueryReuse && (
        <QueryReuse closeQueryReuse={() => setShowQueryReuse(false)} onReuse={handleSearchTextChange} />
      )}



      <div className='chat-messages'>
      {queryData.messages.length === 0 && !ShowQueryReuse && !showBatchQuery? (
              <div className="no-messages">
                <div className="no-messages-icon">
                  <img src="/query.png" className="icon"  alt="qeury icon"/>
                </div>
                <div className="no-messages-text">How can I help you today?</div>
              </div>
            ) :
        (queryData.messages.map((msg: ChatMessage, index: number) => (
          <div key={index} className={`message ${msg.author === 'user' ? 'user-message' : 'system-message'}`}>
            <span className="message-icon"></span>
            <span className="message-author">{msg.author === 'user' ? 'User:' : 'QueryArtisan:'}</span>
            <div className={`message-text ${msg.author === 'user' ? 'text-user' : 'text-system'}`}>
              {renderMessageText(msg)}
            </div> {/* 消息文本 */}
          </div>
        )))
       }
       
      </div>
      <div className="chat-input">
        <CustomSearch
          placeholder="Enter your question..."
          onSearch={sendMessage}  
          NewsearchText={searchText}
          />
      </div>
    </div>
    
  );
  
};

export default ChatComponent;

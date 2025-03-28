import React, { useState } from 'react';
import Navbar from '../utilsCompoents/Navbar';
import ReportPage from '../ReportPage/ReportPage';
import ProcessPage from "../ProceePage/ProcessPage";
import QueryPage from '../QueryChat/QueryPage';
import "./HomePage.css";

const HomePage: React.FC = () => {
  const [selectedContent, setSelectedContent] = useState<string>('QueryChat');
  const [queryId, setQueryId] = useState<string>('7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5');
  const [queryId2, setQueryId2] = useState<string>('7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5');
  // 切换后要渲染的主体内容
  const renderContent = () => {
    switch (selectedContent) {
      case 'QueryChat':
        return <QueryPage onQueryIdChange={setQueryId2} />;
      case 'Process':
        return <ProcessPage id={queryId} />;
      case 'Report':
        return <ReportPage id={queryId} />;
      default:
        return <div>Select a section to view</div>;
    }
  };

  return (
    <div className="OptPage-container">
      {/* 导航栏 */}
      <Navbar
        selectedContent={selectedContent}
        setSelectedContent={setSelectedContent}
      />

      {/* 新增的步骤进度条/行 */}
      <div className="step-indicator-container">
        <div
          className={`step-item ${selectedContent === 'QueryChat' ? 'active' : ''}`}
          onClick={() => setSelectedContent('QueryChat')}
        >
          <span className="step-number">1</span>
          <span className="step-text">System Configuration and Query Interaction</span>
        </div>
        <span className="home-separator">{'>>>>>'}</span>
        <div
          className={`step-item ${selectedContent === 'Process' ? 'active' : ''}`}
          onClick={() => setSelectedContent('Process')}
        >
          <span className="step-number">2</span>
          <span className="step-text">Query Processing and Analysis</span>
        </div>
        <span className="home-separator">{'>>>>>'}</span>
        <div
          className={`step-item ${selectedContent === 'Report' ? 'active' : ''}`}
          onClick={() => setSelectedContent('Report')}
        >
          <span className="step-number">3</span>
          <span className="step-text">Visualization and Final Report</span>
        </div>
      </div>

      {/* 主体内容 */}
      <div className="OptPage-maincontent">
        {renderContent()}
      </div>
    </div>
  );
};

export default HomePage;

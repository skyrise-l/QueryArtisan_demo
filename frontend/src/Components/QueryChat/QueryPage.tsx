import React from 'react';

import ChatComponent from './Query';
import DatabaseSchemaGraph from './DatabaseSchemaGraph';
import SettingsComponent from './SettingsComponent';
import OperatorControlPanel from './OperatorControlPanel';
import './QueryPage.css';


interface QueryPageProps {
  onQueryIdChange?: (queryId: string) => void; 
}

const QueryPage: React.FC<QueryPageProps> = ({ onQueryIdChange }) => {

  return (

    <div className="Query-page-container">
       <div className="Setttings-grid">
        <SettingsComponent />
      </div>

      <div className="operator-grid">
        <OperatorControlPanel />
      </div>

      {/* 第三块区域：占据第二行的第二列及之后的区域 */}
      <div className="ChatComponent-grid">
          <ChatComponent 
                onQueryIdChange={onQueryIdChange}
              />
      </div>

      <div className="datalake-grid">
        <DatabaseSchemaGraph />
      </div>
          
    </div>
  );
};

    
export default QueryPage;

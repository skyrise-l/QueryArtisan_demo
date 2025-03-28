import React, { useState, useEffect } from 'react';
import ApplyButton from '../utilsCompoents/ApplyButton';
import "./SettingsComponent.css"
import { Button, Pagination, Table, Modal, Input, Select } from 'antd';

// Fetch data from backend
const fetchLLMRecommendations = async (taskDescription: string) => {
  const response = await fetch('http://127.0.0.1:8080/api/Home/GetTaskRecommend?query=' + encodeURIComponent(taskDescription), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await response.json();
  return data;
};

const fetchNewTaskSetting = async () => {
  const response = await fetch('http://127.0.0.1:8080/api/Home/GetNewTaskSetting');
  const data = await response.json();
  console.log(data);
  return data;
};

const deleteMaxIdTaskSetting = async () => {
  const response = await fetch('http://127.0.0.1:8080/api/Home/DeleteNewTaskSetting', { method: 'GET' });
  const data = await response.json();
  return data;
};

type FixedSettings = {
  [key: string]: string[];
};


const SettingsComponent: React.FC = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [taskRecommendations, setTaskRecommendations] = useState<any>(null);
  const [llmJudgment, setLlmJudgment] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [loadingQuery, setLoadingQuery] = useState(false);
  const [editMode, setEditMode] = useState(false);

  const fixedSettings: FixedSettings = {
    'Model Select': ['GPT-3.5-turbo-16k', 'GPT-4-turbo-preview', 'LLama3-70B', 'Deepseek-R1'],
    'Task Mode': ['CombinedAnalysis', 'AnalyzeOnly', 'QueryOnly'],
    'System Prompt': ['Default mode', 'Simple mode', 'Precision mode'],
  };

  const applySettingConstraints = (
    setting: string,
    value: string | number,
    taskRecommendations: any[],
    setTaskRecommendations: React.Dispatch<React.SetStateAction<any[]>>
  ) => {
    const newRecommendations = [...taskRecommendations];
  
    switch (setting) {
      case 'Model Select':
        // Apply dropdown constraints for Model Select
        newRecommendations[0].value = value;
        setTaskRecommendations(newRecommendations);
        break;
      case 'Max tokens':
        // Apply numeric constraint for Max tokens (example: max 1000 tokens)
        const maxTokens = 16384;
        if (typeof value !== 'number' || value > maxTokens) {
          alert(`Max tokens should not exceed ${maxTokens}`);
          return;
        }
        newRecommendations[0].value = value;
        setTaskRecommendations(newRecommendations);
        break;
      case 'Temperature':
        if (typeof value !== 'number' || value < 0 || value > 1) {
          alert('Temperature must be a decimal between 0 and 1');
          return;
        }
        newRecommendations[0].value = value;
        setTaskRecommendations(newRecommendations);
        break;
      
      default:
        // For any other setting, just update the value freely
        newRecommendations[0].value = value;
        setTaskRecommendations(newRecommendations);
        break;
    }
  };

  useEffect(() => {
    const getNewTaskSetting = async () => {
      setLoading(true);
      const data = await fetchNewTaskSetting();
      const parsedData = JSON.parse(data.data);
      setTaskRecommendations(parsedData.task_recommendations);
      setLoading(false);
    };
    getNewTaskSetting();
  }, []);

  const fetchRecommendations = async (description: string) => {
    setLoadingQuery(true);
    const data = await fetchLLMRecommendations(description);
    const parsedData = JSON.parse(data.data);
    setLlmJudgment(parsedData.judgment);
    setTaskRecommendations(parsedData.task_recommendations);
    setLoadingQuery(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTaskDescription(e.target.value);
  };

  const handleSearch = () => {
    if (taskDescription.trim()) {
      fetchRecommendations(taskDescription);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleUndo = async () => {
    const result = await deleteMaxIdTaskSetting();
    if (result.code === 0) {
      const data = await fetchNewTaskSetting();
      const parsedData = JSON.parse(data.data);
      setTaskRecommendations(parsedData.task_recommendations);
      setLlmJudgment('');
    }
  };

  const handleApplyChanges = () => {
    setLoading(true);
    fetch('http://127.0.0.1:8080/api/Home/UpdateRecommend', {
      method: 'POST',
      body: JSON.stringify(taskRecommendations),
      headers: { 'Content-Type': 'application/json' },
    })
      .then((res) => res.json())
      .then((data) => {
        setLoading(false);
        if (data.code === 0) {
          alert('Update Successful');
        } else {
          alert('Update Failed');
        }
      });
  };

  const handleEditCell = (e: React.ChangeEvent<HTMLInputElement>, index: number, field: string) => {
    const newRecommendations = [...taskRecommendations];
    newRecommendations[index][field] = e.target.value;
    setTaskRecommendations(newRecommendations);
  };

  const handleSelectChange = (value: string, index: number, field: string) => {
    applySettingConstraints(field, value, taskRecommendations, setTaskRecommendations);
  };

  const handleNumericChange = (value: number, index: number, field: string) => {
    applySettingConstraints(field, value, taskRecommendations, setTaskRecommendations);
  };


  return (
    <div className="task-analyzer">
        <div className="DataLineage-header">
          <div className="DataLineage-title2" >Intelligent Personalized Settings</div>
        </div>

      <div className="input-section">
        <Input
          type="text"
          value={taskDescription}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder= "Tell us what you need, and we’ll customize the settings for you."
          
        />
        <ApplyButton tooltip="Search" onClick={handleSearch} className="allpy-button-TaskAnalyzer-search" />
      </div>

      <div className="task-analyzer-text">
          {loadingQuery ? (
            <span>Generating LLM recommendations...</span> // loading 时的文本
          ) : llmJudgment && !loadingQuery  ? (
            <span>{llmJudgment}</span> // 成功获取 LLM 判断后的文本
          ) : (
            <span>Here are our recommended settings:</span> // 默认文本
          )}
        </div>

        <div className="setting-content">
        {loading || loadingQuery ? (
          <div className="loading-backdrop">
            <div className="spinner"></div>
          </div>
        ) : null}

        {!loading && taskRecommendations && (
          <div className="recommendation-section">
            <table className="recommendation-table">
              <thead>
                <tr>
                  <th>Setting</th>
                  <th>Value</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {taskRecommendations.map((task: any, index: number) => (
                  <tr key={index}>
                    <td>{task.setting}</td>
                    <td>
                      {editMode ? (
                        fixedSettings[task.setting] ? (
                          <Select
                            defaultValue={task.value}
                            onChange={(value) => handleSelectChange(value, index, 'value')}
                          >
                            {fixedSettings[task.setting].map((option: string) => (
                              <Select.Option key={option} value={option}>
                                {option}
                              </Select.Option>
                            ))}
                          </Select>
                        ) : (
                          <Input
                            type="text"
                            value={task.value}
                            onChange={(e) => handleNumericChange(Number(e.target.value), index, 'value')}
                          />
                        )
                      ) : (
                        task.value
                      )}
                    </td>
                    <td>{task.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="actions">
        <ApplyButton tooltip={editMode ? 'Save' : 'Edit'} onClick={() => setEditMode(!editMode)} className="allpy-button-TaskAnalyzer" />
        <ApplyButton tooltip="Undo" onClick={handleUndo} className="allpy-button-TaskAnalyzer" />
        <ApplyButton tooltip="Apply" onClick={handleApplyChanges} className="allpy-button-TaskAnalyzer" />
      </div>
    </div>
  );
};

export default SettingsComponent;
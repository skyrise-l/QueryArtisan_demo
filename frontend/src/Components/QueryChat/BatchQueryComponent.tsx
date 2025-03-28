import React, { useState } from 'react';
import './BatchQueryComponent.css';  // 引入CSS
import ApplyButton from '../utilsCompoents/ApplyButton';
import { Upload, message, Button } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { UploadFile, UploadChangeParam } from 'antd/lib/upload/interface';

interface BatchQueryComponentProps {
  closeBatchQuery: () => void;  // 关闭批量查询组件的函数
}

const BatchQueryComponent: React.FC<BatchQueryComponentProps> = ({ closeBatchQuery }) => {
  const [queries, setQueries] = useState<string>('');  // 用于存储用户输入的查询
  const [isProcessing, setIsProcessing] = useState<boolean>(false);  // 是否正在执行查询
  const [downloadLink, setDownloadLink] = useState<string | null>(null);  // 分析报告下载链接
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  // 处理用户输入查询
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQueries(e.target.value);
  };

  // 批量上传查询
  const handleBatchQuery = async () => {
    if (queries.trim() === '' && fileList.length === 0) {
      message.error('Please enter a query or upload a report.');
      return;
    }

    setIsProcessing(true);

    // 创建FormData并添加查询文本和文件
    const formData = new FormData();
    formData.append('queries', queries); // 添加查询文本

    // 添加上传的文件
    fileList.forEach(file => {
      formData.append('files', file.originFileObj as Blob); // 上传的文件
    });

    try {
      const response = await fetch('http://127.0.0.1:8080/api/Home/batchQuery', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data)
        if (data.code === 0 && data.data) {
          setDownloadLink(data.data);  // 获取到的报告URL
        } else {
          message.error('Failed to process the query.');
        }
      } else {
        message.error('Server error. Please try again later.');
      }
    } catch (error) {
      message.error('Request failed. Please try again later.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUploadRequest = async (options: any) => {
    const { file, onSuccess, onError } = options;

    console.log(`File ${file.name} is added to the list (not uploaded to backend)`);

    setFileList((prevFiles) => [...prevFiles, file]);

    onSuccess("ok");
    message.success(`${file.name} uploaded successfully`);
  };

  // 处理文件上传
  const handleChange = (info: UploadChangeParam) => {
    setFileList(info.fileList);
  };

  const handleFileRemove = (file: UploadFile) => {
    return true; // Or implement actual remove logic here
  };

  return (
    <div className="batch-query-container">
      <h3 className="batch-query-title">Batch Query Execution</h3>

      {/* 文本输入框 */}
      <textarea
        className="batch-query-textarea"
        placeholder="We will attempt to break down your query input, but in order to improve the readability of the analysis report, please enter batch queries here, each on a new line."
        value={queries}
        rows={12}
        onChange={handleInputChange}
        disabled={isProcessing}
      />

      <div className="file-upload-section">
        <Upload
          fileList={fileList}
          customRequest={handleUploadRequest}
          onChange={handleChange}
          onRemove={handleFileRemove}
          showUploadList={{ showRemoveIcon: true }}
        >
          <Button className="custom-upload-button" icon={<UploadOutlined />}>Upload Analysis Report</Button>
        </Upload>
        <span className="upload-description">
          <strong>Tip:</strong> You can upload a previous analysis report as the basis for this query. This helps improve the analysis results.
        </span>
      </div>

      {/* 执行查询和取消按钮 */}
      <div className="batch-query-actions">
        <ApplyButton tooltip="Confirm Analysis" onClick={handleBatchQuery} className='allpy-button-confirm'/>
        <ApplyButton tooltip="Cancel" onClick={closeBatchQuery} className='allpy-button-cancel'/>
      </div>

      {/* 等待图标 */}
      {isProcessing && <div className="loading-spinner"></div>}

      {/* 查询完成后显示下载按钮 */}
      {downloadLink && (
        <div className="query-completion">
          <p>Query completed! Please click below to download the analysis report:</p>
          <a href={downloadLink} className="download-link" download>Download Analysis Report</a>
        </div>
      )}
    </div>
  );
};

export default BatchQueryComponent;

import React, { useState, useEffect } from 'react';
import { Button, Spin, message, Upload, Select } from 'antd';
import type { UploadProps } from 'antd/es/upload/interface';
import "./ManageDataMenuComponent.css";
import SourceDataComponent from './SourceDataComponent2';
import axios from 'axios';

// --------------------- 后端接口 ---------------------
async function fetchDataSourceDetails(datasource: string) {
  try {
    const response = await axios.get(
      'http://localhost:8080/api/Report/FindDataSourceDeatils',
      { params: { datasource } }
    );
    if (response.data.code === 0) {
      return response.data.data.details || [];
    } else {
      console.error('Failed to fetch code:', response.data.message);
      return [];
    }
  } catch (error) {
    console.error('Error while fetching code:', error);
    return [];
  }
}

// --------------------- 上传接口 ---------------------
async function uploadFileToBackend(file: File, datasource: string) {
  // 1. 构造 FormData
  const formData = new FormData();
  formData.append('datasource', datasource); // 额外参数
  formData.append('file', file);            // 文件本体

  // 2. 发起 POST 请求
  const response = await axios.post('http://localhost:8080/api/Report/UploadDataFile', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  // 3. 根据后端返回的结果进行判断
  const data = response.data;
  if (data.code !== 0) {
    throw new Error(`Upload failed: ${data.message}`);
  }
  // 否则即上传成功
  return data;
}


// --------------------- 类型定义 ---------------------
interface ManageDataMenuComponentProps {
  datasource: string;
}


interface TableMetadataRecord {
  table_name: string;
  column_name: string;
  table_type: string;
  data_format: string;
  primary_key: string | null;
  foreign_key: string | null;
}

interface ColumnConfig {
  title: string;
  dataKey: keyof TableMetadataRecord; // 注意这里
  width: number;
}


// 列配置：可随需求调整列宽、列名、字段
const columns: ColumnConfig[] = [
  { title: 'Column', dataKey: 'column_name', width: 110 },
  { title: 'Table Type',  dataKey: 'table_type',  width: 120 },
  { title: 'Format', dataKey: 'data_format', width: 130 },
  { title: 'Primary Key', dataKey: 'primary_key', width: 140 },
  { title: 'Foreign Key', dataKey: 'foreign_key', width: 140 },
];

const ManageDataMenuComponent: React.FC<ManageDataMenuComponentProps> = ({
  datasource,
}) => {

  const [loading, setLoading] = useState(false);
  // 分组后的结构：[{ tableName, columns[] }]
  const [groupedData, setGroupedData] = useState<Array<{
    tableName: string;
    columns: TableMetadataRecord[];
  }>>([]);

  // 当前正在浏览第几个表
  const [currentTableIndex, setCurrentTableIndex] = useState(0);

  const [showSourceDataComponent, setShowSourceDataComponent] = useState(false);

  // --------------------- 加载数据 ---------------------
  const loadTableData = async () => {
    setLoading(true);
    const details = await fetchDataSourceDetails(datasource);

    // 按 table_name 分组
    const map = new Map<string, TableMetadataRecord[]>();
    details.forEach((item: TableMetadataRecord) => {
      if (!map.has(item.table_name)) {
        map.set(item.table_name, []);
      }
      map.get(item.table_name)!.push(item);
    });

    const groups = Array.from(map.entries()).map(([tableName, columns]) => ({
      tableName,
      columns,
    }));

    setGroupedData(groups);
    setCurrentTableIndex(0);
    setLoading(false);
  };

  useEffect(() => {
    loadTableData();
  }, [datasource]);

  // --------------------- 文件上传 ---------------------
  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      // 调用上传函数，datasource 可以从组件的 props 或 state 中获取
      await uploadFileToBackend(file, datasource); 
      message.success('File uploaded successfully');
  
      // 重新加载表数据
      await loadTableData();
    } catch (err) {
      console.error(err);
      message.error('Upload failed');
    } finally {
      setLoading(false);
    }
  };
  // AntD Upload props
  const uploadProps: UploadProps = {
    beforeUpload: (file) => {
      handleFileUpload(file);
      // 返回 false 阻止默认上传动作
      return false;
    },
    showUploadList: false,
  };

  // --------------------- 上下切换表格 ---------------------
  const handleSelectChange = (value: number) => {
    setCurrentTableIndex(value);
  };

  const handleViewClick = () => {
    setShowSourceDataComponent(true);
  };

  const handleCancelClick = () => {
    setShowSourceDataComponent(false);
  };


  // 当前表
  const currentTable = groupedData[currentTableIndex];

  return (
    <div className="manage-data-menu">
      <div className="DataLineage-header">
        <div className="DataLineage-title2">Manage Data</div>
      </div>


      <Spin spinning={loading} tip="Uploading or Loading...">

        {/* 顶部操作区 */}
        <div className="manage-data-menu-header">
          <div className="manage-data-menu-header-left">
              <Select<number> // 指定泛型，确保 value 是 number
                style={{ width: 200 }}
                value={currentTableIndex}
                onChange={handleSelectChange}
                placeholder="Select Table"
                disabled={groupedData.length === 0}
              >
                {groupedData.map((group, index) => (
                  <Select.Option key={index.toString()} value={index}>
                    {group.tableName}
                  </Select.Option>
                ))}
              </Select>
          </div>

          <div className="manage-data-menu-header-center">
            <Upload {...uploadProps}>
              <Button className="manage-data-menu-upload-btn">Upload</Button>
            </Upload>
          </div>

          <div className="manage-data-menu-header-right">
            <Button
              onClick={handleViewClick}
              className="manage-data-menu-View-btn"
            >
              View Data
            </Button>
            <Button
              onClick={handleCancelClick}
              className="manage-data-menu-cancel-btn"
            >
              Return
            </Button>
          </div>
        </div>


        <div className="table-container">
          {showSourceDataComponent ? (
            <SourceDataComponent
              showFilters={false}
              dataName={currentTable?.tableName || ''}
              dataType={currentTable?.columns[0]?.table_type || ''}
              id={"null"}
            />
          ) : (
            currentTable && (
              <table className="custom-table">
                <thead>
                  <tr>
                    {columns.map((col) => (
                      <th key={col.dataKey} style={{ width: col.width }}>
                        {col.title}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {currentTable.columns.map((row, idx) => (
                    <tr key={idx}>
                      {columns.map((col) => (
                        <td key={col.dataKey}>{row[col.dataKey] ?? ''}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}
        </div>
      </Spin>
      



    </div>
  );
};

export default ManageDataMenuComponent;

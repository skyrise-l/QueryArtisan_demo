import React, { useState, useEffect } from 'react';
import { Button, Pagination, Table, Modal, Input } from 'antd';
import { useNavigate } from 'react-router-dom'; 
import './QueryReuse.css'; // 你可以添加样式来美化这个组件
import ApplyButton from '../utilsCompoents/ApplyButton';

interface HistoryQuery {
  id: string;
  query: string;
  executeTime: string;
  decomposeQueryArray: string;
  decomposeAnalysisArray: string;
  command: string;
}

interface QueryReuseProps {
  closeQueryReuse: () => void;
  onReuse: (query: string) => void;
}

const QueryReuse: React.FC<QueryReuseProps> = ({ closeQueryReuse, onReuse }) => {
  const [historyQueries, setHistoryQueries] = useState<HistoryQuery[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize] = useState<number>(4); // 每页显示4条
  const [isDeleteConfirmVisible, setIsDeleteConfirmVisible] = useState(false);
  const [deleteQueryId, setDeleteQueryId] = useState<string | null>(null);
  const [searchText, setSearchText] = useState<string>(''); 
  const navigate = useNavigate(); 

  // 重新从后台获取历史查询数据
  const fetchHistoryQueries = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8080/api/Home/GetHistoryQueries'); 

      const data = await response.json();
      if (data.code === 0) {
        setHistoryQueries(data.data);
      } else {
        console.error('Failed to fetch history queries');
      }
    } catch (error) {
      console.error('Error fetching history queries:', error);
    }
  };

  useEffect(() => {
    fetchHistoryQueries(); // 初始化时获取数据
  }, []);

  // 删除历史查询记录的确认框
  const handleDeleteConfirm = (id: string) => {
    setDeleteQueryId(id);
    setIsDeleteConfirmVisible(true);  // 显示删除确认框
  };

  const handleDelete = async () => {
    if (deleteQueryId === null) return;

    try {
      const response = await fetch(`http://127.0.0.1:8080/api/Home/DeleteHistoryQuery?QueryId=${deleteQueryId}`);
      const data = await response.json();
      if (data.code === 0) {
        // 删除成功后，重新获取数据
        await fetchHistoryQueries();
        setDeleteQueryId(null);  // 重置删除ID
      } else {
        console.error('Failed to delete history query');
      }
    } catch (error) {
      console.error('Error deleting history query:', error);
    } finally {
      setIsDeleteConfirmVisible(false);  // 关闭确认框
    }
  };

  // 处理分页切换
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // 处理搜索框输入变化
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value);
  };

  // 过滤查询数据
  const filteredQueries = historyQueries.filter(query =>
    query.query.toLowerCase().includes(searchText.toLowerCase())
  );

  const handleReportClick = (id: string) => {
    navigate(`/report/${id}`); // 跳转并传递 ID 参数
  };

  const handleQueryClick = (query: string) => {
    onReuse(query);  
  };

  // 设置表格的列
  const columns = [
    {
      title: 'Query',
      dataIndex: 'query',
      key: 'query',
      render: (text: string) => (
        <span
        onClick={() => handleQueryClick(text)}
        style={{
          color: 'black',
          textDecoration: 'none', 
          cursor: 'pointer',
          transition: 'color 0.3s, text-decoration 0.3s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = 'blue'; 
          e.currentTarget.style.textDecoration = 'underline'; 
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = 'black'; 
          e.currentTarget.style.textDecoration = 'none'; 
        }}
      >
        {text}
      </span>

      ),
      width: '55%',
    },
    {
      title: 'Execute Time',
      dataIndex: 'executeTime',
      key: 'executeTime',
      render: (text: string) => <span>{text}</span>,
      width: '20%',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: HistoryQuery) => (
        <div>
          <Button onClick={() => handleReportClick(record.id)} className="report-button">Report</Button>
          <Button onClick={() => handleDeleteConfirm(record.id)} className="delete-button">Delete</Button>
        </div>
      ),
    },
  ];
  

  return (
    <div className="query-reuse-container">
      <div className="query-reuse-header">
        <h3>Query Reuse</h3>
        <Input
          placeholder="Search queries... (The current history query saves a maximum of 5000 records.)"
          value={searchText}
          onChange={handleSearchChange}
          style={{ width: 180 }} // 添加输入框样式
        />
      </div>
      <div className="separator"></div>

      <div className="query-reuse-info">
        <p>The current history query saves a maximum of 5000 records.</p>
      </div>

      <Table
        dataSource={filteredQueries}  // 使用过滤后的数据
        columns={columns}
        rowKey="id"
        pagination={false}
        className="query-reuse-table"
        scroll={{ y: 250 }} // 设置固定表格高度，允许垂直滚动
      />

      <div className="query-reuse-actions">
        <Pagination
          current={currentPage}
          pageSize={pageSize}
          total={filteredQueries.length}
          onChange={handlePageChange}
          showSizeChanger={false}
          className="pagination"
        />
        <ApplyButton tooltip="Cancel" onClick={closeQueryReuse} className='allpy-button-cancel-small'/>
      </div>

      {/* 删除确认框 */}
      <Modal
        title="Confirm Deletion"
        visible={isDeleteConfirmVisible}
        onOk={handleDelete}
        onCancel={() => setIsDeleteConfirmVisible(false)}
        okText="Yes"
        cancelText="No"
        width={400} // 设置宽度
        centered // 居中显示
        bodyStyle={{ padding: '20px' }} // 调整 Modal 内容的内边距
        footer={null} // 去掉默认的按钮，自己定义
        >
        <div className="modal-content">
            <p className="modal-text">Are you sure you want to delete this query record?</p>
            <div className="modal-buttons">
            <Button onClick={handleDelete} className="modal-button yes-button">Yes</Button>
            <Button onClick={() => setIsDeleteConfirmVisible(false)} className="modal-button no-button">No</Button>
            </div>
        </div>
        </Modal>
    </div>
  );
};

export default QueryReuse;

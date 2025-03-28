import React, { useState, useEffect } from 'react';
import { Button, Modal, Input, Tooltip, Card, Form, Pagination, message } from 'antd';
import axios from 'axios';
import './OperatorControlPanel.css';
import ApplyButton from '../utilsCompoents/ApplyButton';

type Operator = {
  id: number;
  operator: string;
  description: string;
  codeExample: string;
  format: string;
  status: number;      // 1=Active, 0=InActive
  isStandard?: boolean; // 新增字段，用于标记是否是 standard
};

type AddOperatorPojo = {
  operator: string;
  description: string;
  codeExample: string;
  format: string;
};

type EditOperatorPojo = {
  id: number;
  operator: string;
  description: string;
  codeExample: string;
  format: string;
};

const BASE_URL = 'http://127.0.0.1:8080/api/Home';

// 读取 operator 的函数，可以分别获取 standard / custom，然后合并
const readOperators = async (isStandard: boolean) => {
  try {
    const response = await axios.get(`${BASE_URL}/ReadOperator`, {
      params: { isStandard }
    });
    if (response.data.code === 0 && Array.isArray(response.data.data)) {
      return response.data.data;
    } else {
      console.error(response.data.message);
      return [];
    }
  } catch (error) {
    console.error('Error fetching operators', error);
    return [];
  }
};

const addOperator = async (operatorData: AddOperatorPojo) => {
  try {
    const response = await axios.post(`${BASE_URL}/AddOperator`, operatorData);
    if (response.data.code === 0) {
      message.success(response.data.data);
      return true;
    } else {
      console.error(response.data.message);
      return false;
    }
  } catch (error) {
    console.error('Error adding operator', error);
    return false;
  }
};

const editOperator = async (operatorData: EditOperatorPojo) => {
  try {
    const response = await axios.post(`${BASE_URL}/EditOperator`, operatorData);
    if (response.data.code === 0) {
      message.success(response.data.data);
      return true;
    } else {
      console.error(response.data.message);
      return false;
    }
  } catch (error) {
    console.error('Error editing operator', error);
    return false;
  }
};

const activateOperator = async (operatorId: number) => {
  try {
    const response = await axios.get(`${BASE_URL}/ActiveOperator`, {
      params: { 
        // 假设后端不再需要 isStandard 参数，如果需要可再加上
        operatorId 
      }
    });
    if (response.data.code === 0) {
      message.success(response.data.data);
      return true;
    } else {
      console.error(response.data.message);
      return false;
    }
  } catch (error) {
    console.error('Error activating operator', error);
    return false;
  }
};

const deleteOperator = async (operatorId: number) => {
  try {
    const response = await axios.get(`${BASE_URL}/DeleteOperator`, {
      params: { operatorId }
    });
    if (response.data.code === 0) {
      message.success(response.data.data);
      return true;
    } else {
      console.error(response.data.message);
      return false;
    }
  } catch (error) {
    console.error('Error deleting operator', error);
    return false;
  }
};

// 定义一个管理动作的类型
type ManageAction = 'add' | 'delete' | 'edit' | 'activate' | null;

const OperatorControlPanel: React.FC = () => {
  const PAGE_SIZE = 9;

  // 存储所有 operator
  const [operators, setOperators] = useState<Operator[]>([]);
  // 当前分页
  const [currentPage, setCurrentPage] = useState(1);

  // 用于弹窗的表单
  const [formOperator] = Form.useForm();    // 新增 operator 表单
  const [editForm] = Form.useForm();        // 编辑 operator 表单

  // 对话框的显隐
  const [isAddModalVisible, setIsAddModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);

  // 当前选中操作：add / delete / edit / activate / null
  const [selectedAction, setSelectedAction] = useState<ManageAction>(null);

  // 编辑时需要存一下当前要编辑的对象
  const [currentEditOperator, setCurrentEditOperator] = useState<Operator | null>(null);

  // 组件挂载后一次性读取所有 operator
  useEffect(() => {
    fetchAllOperators();
  }, []);

  // 同时读取 standard + custom，然后合并
  const fetchAllOperators = async () => {
    const standardList = await readOperators(true);
    const customList = await readOperators(false);

    // 给 standardList 里的每一项打上 isStandard = true，customList 打上 false
    const standardOperators = standardList.map((op: Operator) => ({
      ...op,
      isStandard: true
    }));
    const customOperators = customList.map((op: Operator) => ({
      ...op,
      isStandard: false
    }));

    setOperators([...standardOperators, ...customOperators]);
  };

  // 点击菜单栏某个管理按钮时，记录动作
  const handleSelectAction = (action: ManageAction) => {
    setSelectedAction(action);

    // 如果点击的是 "add"，直接打开弹窗；其他操作等用户再点击某个 operator
    if (action === 'add') {
      setIsAddModalVisible(true);
    }
  };

  // 当用户点击某个 operator 卡片时，根据 selectedAction 来执行对应操作
  const handleOperatorClick = async (operator: Operator) => {
    if (!selectedAction) {
      // 未选择任何管理动作，则可提示或直接返回
      message.info('Please select a manage action first.');
      return;
    }

    if (selectedAction === 'activate') {
      // 激活
      await activateOperator(operator.id);
      await fetchAllOperators();
      setSelectedAction(null); // 操作完后复位
    } else if (selectedAction === 'delete') {
      // 如果是 standard 不允许删除
      if (operator.isStandard) {
        message.warning('Standard operator cannot be deleted.');
      } else {
        await deleteOperator(operator.id);
        await fetchAllOperators();
      }
      setSelectedAction(null);
    } else if (selectedAction === 'edit') {
      // 打开编辑弹窗
      setCurrentEditOperator(operator);
      editForm.setFieldsValue({
        operator: operator.operator,
        description: operator.description,
        codeExample: operator.codeExample,
        format: operator.format,
      });
      setIsEditModalVisible(true);
    }
    // "add" 操作不需要点 operator 执行，所以不会进入这里
  };

  // 处理添加 operator 对话框的确认
  const handleAddOk = () => {
    formOperator
      .validateFields()
      .then(async (values: AddOperatorPojo) => {
        const success = await addOperator(values);
        if (success) {
          setIsAddModalVisible(false);
          formOperator.resetFields();
          fetchAllOperators();
        }
        // 新增完成后，退出 "add" 状态
        setSelectedAction(null);
      })
      .catch((info) => {
        console.log('Validate Failed:', info);
      });
  };

  const handleAddCancel = () => {
    setIsAddModalVisible(false);
    formOperator.resetFields();
    setSelectedAction(null);
  };

  // 处理编辑 operator 对话框的确认
  const handleEditOk = async () => {
    try {
      const values = await editForm.validateFields();
      if (currentEditOperator) {
        const success = await editOperator({
          id: currentEditOperator.id,
          ...values
        });
        if (success) {
          setIsEditModalVisible(false);
          editForm.resetFields();
          fetchAllOperators();
        }
      }
      setSelectedAction(null);
    } catch (errorInfo) {
      console.log('Failed:', errorInfo);
    }
  };

  const handleEditCancel = () => {
    setIsEditModalVisible(false);
    editForm.resetFields();
    setSelectedAction(null);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // 分页切片
  const paginatedOperators = operators.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  return (
    <div className="operator-control-panel">
      <div className="DataLineage-header">
        <div className="DataLineage-title2">Operator Control Panel</div>
      </div>

      <div className="operator-menu-bar">
        <ApplyButton tooltip="Add" onClick={() => handleSelectAction('add')} className="allpy-button-operator-menu" />
        <ApplyButton tooltip="Activate" onClick={() => handleSelectAction('activate')} className="allpy-button-operator-menu" />
        <ApplyButton tooltip="Edit" onClick={() => handleSelectAction('edit')} className="allpy-button-operator-menu" />
        <ApplyButton tooltip="Delete" onClick={() => handleSelectAction('delete')} className="allpy-button-operator-menu" />
      </div>

      <div className="operator-list-container">
        <div className="operator-grid">
          {paginatedOperators.map((operator) => (
            <Tooltip
              key={operator.id}
              overlayStyle={{ minWidth: '500px', maxWidth: '500px' }} 
              title={
                <div>
                  <p style={{ color: 'yellow' }}>
                    Operator: <span style={{ color: 'white' }}>{operator.operator}</span>
                  </p>
                  <p style={{ color: 'yellow' }}>
                    Description: <span style={{ color: 'white' }}>{operator.description}</span>
                  </p>
                  <p style={{ color: 'yellow' }}>
                    CodeExample: <code style={{ color: 'white' }}>{operator.codeExample}</code>
                  </p>
                  <p style={{ color: 'yellow' }}>
                    Format: {operator.format.split('\\n').map((line, idx) => (
                      <span key={idx} style={{ color: 'white' }}>
                        {line}
                        <br />
                      </span>
                    ))}
                  </p>
                  <p style={{ color: 'yellow' }}>
                    Status: <span style={{ color: 'white' }}>
                      {operator.status === 1 ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                  <p style={{ color: 'yellow' }}>
                    Type: <span style={{ color: 'white' }}>
                      {operator.isStandard ? 'Standard' : 'Custom'}
                    </span>
                  </p>
                </div>
              }
            >
              <div
                className={`
                  operator-card
                  ${operator.isStandard ? 'operator-card-standard' : 'operator-card-custom'}
                  ${operator.status === 0 ? 'operator-card-inactive' : ''}
                `}
                onClick={() => handleOperatorClick(operator)}
              >

                {operator.operator}
              </div>
            </Tooltip>
          ))}
        </div>
      </div>


      <div className="pagination-container">
          <Pagination
            current={currentPage}
            onChange={handlePageChange}
            pageSize={PAGE_SIZE}
            total={operators.length}
          />
        </div>

      {/* 新增操作符对话框 */}
      <Modal
        title="Add Operator"
        visible={isAddModalVisible}
        onOk={handleAddOk}
        onCancel={handleAddCancel}
        footer={[
          <Button key="back" onClick={handleAddCancel}>
            Cancel
          </Button>,
          <Button key="submit" onClick={handleAddOk}>
            Confirm
          </Button>,
        ]}
      >
        <Form form={formOperator} layout="vertical">
          <Form.Item
            name="operator"
            label="Operator Name"
            rules={[{ required: true, message: 'Please input the name of the operator!' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please input the description!' }]}
          >
            <Input.TextArea />
          </Form.Item>
          <Form.Item
            name="codeExample"
            label="Code Example"
            rules={[{ required: true, message: 'Please input the Code Example!' }]}
          >
            <Input.TextArea />
          </Form.Item>
          <Form.Item
            name="format"
            label="Format"
            rules={[{ required: true, message: 'Please input the logical format!' }]}
          >
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑操作符对话框 */}
      <Modal
        title="Edit Operator"
        visible={isEditModalVisible}
        onOk={handleEditOk}
        onCancel={handleEditCancel}
        footer={[
          <Button key="back" onClick={handleEditCancel}>
            Cancel
          </Button>,
          <Button key="submit" onClick={handleEditOk}>
            Confirm
          </Button>,
        ]}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="operator"
            label="Operator Name"
            rules={[{ required: true, message: 'Please input the name of the operator!' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please input the description!' }]}
          >
            <Input.TextArea />
          </Form.Item>
          <Form.Item
            name="codeExample"
            label="Code Example"
            rules={[{ required: true, message: 'Please input the Code Example!' }]}
          >
            <Input.TextArea />
          </Form.Item>
          <Form.Item
            name="format"
            label="Format"
            rules={[{ required: true, message: 'Please input the logical format!' }]}
          >
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OperatorControlPanel;

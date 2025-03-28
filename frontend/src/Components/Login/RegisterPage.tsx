import React, { useState } from 'react';
import { Button, Form, Input, message } from 'antd';
import { Link, useNavigate } from 'react-router-dom'; // 确保你导入了Link组件
import { LockOutlined, UserOutlined, UserAddOutlined , MailOutlined } from '@ant-design/icons';
import axios from 'axios';
import './LoginPage.css'; // 确保你创建了一个对应的CSS文件

const RegisterPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/register', {
        username: values.username,
        password: values.password,
      });
      const { code, message: msg, data } = response.data;
      if (code === 0) {
        message.success('Register successful');
        console.log('Token:', data.token);
        setLoading(false);
        navigate('/login');
      } else {
        message.error(msg);
        setLoading(false);
      }
    } catch (error) {
      message.error('Register failed');
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <UserAddOutlined className="login-icon" />
        <span className="login-title">Create Account</span>
        <Form
          name="login_form"
          className="login-form"
          onFinish={onFinish}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your Username!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Username" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your Password!' }]}
          >
            <Input
              prefix={<LockOutlined />}
              type="password"
              placeholder="Password"
            />
          </Form.Item>
          <Form.Item
            name="email"
            rules={[{ required: true, message: 'Please input your email!' }]}
          >
            <Input
              prefix={<MailOutlined />}
              type="email"
              placeholder="email"
            />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" className="login-form-button-custom" loading={loading}>
              Register
            </Button>
            <div className="login-form-footer">
          <p>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default RegisterPage;

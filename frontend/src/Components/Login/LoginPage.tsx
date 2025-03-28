import React, { useState, useEffect } from 'react';
import { Button, Form, Input, message } from 'antd';
import { useLocation,Link, useNavigate } from 'react-router-dom'; // 确保你导入了Link组件
import { LockOutlined, UserOutlined, MonitorOutlined } from '@ant-design/icons';
import axios from 'axios';
import './LoginPage.css'; // 确保你创建了一个对应的CSS文件

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // If we were redirected to login, check for the state passed in redirect
    if (location.state?.message) {
      message.info(location.state.message);
    }
  }, [location, navigate]);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8080/api/login', {
        username: values.username,
        password: values.password,

      });
      const { code, message: msg, data } = response.data;
      if (code === 0) {
        message.success('Login successful');
        console.log('Token:', data.token);
        localStorage.setItem('token', data.token);
        setLoading(false);
        navigate('/');
      } else {
        message.error(msg);
        setLoading(false);
      }
    } catch (error) {
      message.error('Login failed');
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <MonitorOutlined className="login-icon" />
        <span className="login-title">Please Login</span>
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
          <Form.Item>
            <Button type="primary" htmlType="submit" className="login-form-button-custom" loading={loading}>
              login
            </Button>
            <div className="login-form-footer">
          <p>
            No account? <Link to="/register">Sign up</Link>
          </p>
          <p>
            Forgot password? <Link to="/reset-password">Reset Password</Link>
          </p>
        </div>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default LoginPage;

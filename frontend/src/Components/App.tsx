import React from 'react';

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import LoginPage from './Login/LoginPage';
import RegisterPage from './Login/RegisterPage';
import RequireAuth from './Login/RequireAuth';
import HomePage from './HomePage/HomePage'
import axios from 'axios';

axios.interceptors.request.use(function (config) {
  // 获取 token
  const token = localStorage.getItem('token');
  // 如果 token 存在，则附加到请求头中
  if (token) {
    config.headers.Authorization = 'Bearer ' + token;
  }
  return config;
}, function (error) {
  // 处理请求错误
  return Promise.reject(error);
});

const App: React.FC = () => (
  <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
    <Router>
      <Routes>
        <Route path="/" element={<RequireAuth><HomePage /></RequireAuth>} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/HomePage" element={<HomePage />} />
      </Routes>
    </Router>
  </ConfigProvider>
)

export default App;

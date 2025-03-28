import React from 'react';
import { useNavigate } from 'react-router-dom'; // 导入useNavigate钩子
import { LoginOutlined  } from '@ant-design/icons'; 
import "./custom_antd_button.css"

interface LogOutProps {
   
}

const LogOut: React.FC<LogOutProps> = ({}) => {
    const navigate = useNavigate();

    const handleLogOut = () => {
        localStorage.removeItem('token');

        navigate('/login');
    };

  return (
    <button className="CustomButton" onClick={handleLogOut} >
      < LoginOutlined   />Log out
    </button>
  );
};

export default LogOut;

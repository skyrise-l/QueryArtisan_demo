import React from 'react';
import { QuestionCircleOutlined } from '@ant-design/icons'; 
import "./custom_antd_button.css"

interface CustomHelpProps {
  href: string; // 链接地址
  newTab?: boolean; // 是否在新标签页中打开
}

const CustomHelp: React.FC<CustomHelpProps> = ({ href, newTab = false }) => {
  const handleOnClick = () => {
    if (newTab) {
      // 在新标签页打开链接
      window.open(href, '_blank');
    } else {
      // 在当前页面跳转到指定链接
      window.location.href = href;
    }
  };

  return (
    <button className="CustomButton" onClick={handleOnClick}>
      <QuestionCircleOutlined />  Help
    </button>
  );
};

export default CustomHelp;

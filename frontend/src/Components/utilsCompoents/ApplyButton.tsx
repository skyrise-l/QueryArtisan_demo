// ApplyButton.tsx
import React from 'react';
import {  Tooltip } from 'antd';

import './ApplyButton.css'; // 引入CSS样式文件

interface ApplyButtonProps {
    tooltip: string;
    onClick: () => void;
    className?: string;
}

const ApplyButton: React.FC<ApplyButtonProps> = ({ tooltip, onClick, className }) => {
  return (
    <Tooltip title={tooltip}>
      <button className={className} onClick={onClick}>{tooltip}</button>
    </Tooltip>
  );
};

export default ApplyButton;

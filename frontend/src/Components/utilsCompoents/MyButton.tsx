// Button.tsx
import React from 'react';
import { Button, Tooltip } from 'antd';
import './MyButton.css'

interface MyButtonProps {
    tooltip: string;
    onClick: () => void; 
}

const MyButton: React.FC<MyButtonProps> = ({ tooltip, onClick }) => {
  return (
    <Tooltip title={tooltip}>
      <Button type="primary" onClick={onClick}>
        {tooltip}
      </Button>
    </Tooltip>
  );
};

export default MyButton;

import React, { useState } from 'react';
import { Handle, Position } from 'react-flow-renderer';
import './CustomNodeComponent.css'

interface CustomNodeData {
  label: string;
  operator: string;
  targetColumns: string;
  targetSteps: string;
  details: string;
}

interface CustomNodeComponentProps {
  data: CustomNodeData;
}

const CustomNodeComponent: React.FC<CustomNodeComponentProps> = ({ data }) => {
  const [showDetails, setShowDetails] = useState(false);

  const toggleDetailsOnClick = () => {
    setShowDetails((prevState) => !prevState);
  };

  const renderDetailsPopup = () => (
    <div className="detailsPopup">
      <p><strong>Operator:</strong> {data.operator}</p>
      <p><strong>Target columns:</strong> {data.targetColumns}</p>
      <p><strong>Target steps:</strong> {data.targetSteps}</p>
      <p><strong>Operation details:</strong> {data.details}</p>
    </div>
  );

  return (
    <div className="customNode" onClick={toggleDetailsOnClick} style={{ position: 'relative', border: '1px solid #ddd', padding: '10px', borderRadius: '5px', background: 'white', cursor: 'pointer' }}>
      <Handle type="target" position={Position.Top} />
      <div>{data.label}</div>
      {showDetails && renderDetailsPopup()}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

export default CustomNodeComponent;

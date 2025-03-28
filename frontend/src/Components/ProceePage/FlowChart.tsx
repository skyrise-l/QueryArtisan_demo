import React, { useEffect, useState, useContext, useRef } from 'react';
import ReactFlow, {
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  ReactFlowInstance
} from 'react-flow-renderer';
import { Modal, Button } from 'antd'; 
import dagre from 'dagre';
import { CodeHighlightContext } from '../utilsCompoents/CodeHighlightContext';
import axios from 'axios';
import { Handle, Position } from 'react-flow-renderer';
import "./FlowChart.css"
import ApplyButton from '../utilsCompoents/ApplyButton';

interface LogicalNode {
  id: number;
  label: string;
  operator: string;
  targetColumns: string;
  targetSteps: string;
  details: string;
  relatedCodeLines: number[];
}

interface LogicalEdge {
  id: number;
  source: number;
  target: number;
}

interface FlowChartNodeData {
  id: number;
  label: string;
  operator: string;
  targetColumns: string;
  targetSteps: string;
  details: string;
  relatedCodeLines: number[];
}

interface FlowChartNode extends Node<FlowChartNodeData> {}
interface FlowChartEdge extends Edge {}

const nodeWidth = 120;
const nodeHeight = 40;
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

function getOperatorColor(operator: string): string {
  const operatorColors: { [key: string]: string } = {
    read: '#90c2f1',
    write: '#c9fbde',
    filter: '#f8febc',
    join: '#9cff9c',
    group_by: '#c9e8fb',
    having: '#6af4a4',
    select: '#3bf187',
  };

  return operatorColors[operator] || '#ddd'; 
}

interface FlowChartNodeProps {
  data: FlowChartNodeData;
}

const getLayoutedElements = (nodes: FlowChartNode[], edges: FlowChartEdge[]) => {
  dagreGraph.setGraph({ rankdir: 'TB' });

  nodes.forEach(node => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach(edge => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach(node => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };
  });

  return { nodes, edges };
};

const CustomNodeComponent: React.FC<FlowChartNodeProps> = ({ data }) => {
  const backgroundColor = getOperatorColor(data.operator);
  const { setHighlightedLines } = useContext(CodeHighlightContext);

  const style = {
    padding: '4px',
    border: '1px solid #ddd',
    backgroundColor,
    fontSize: '20px',
    width: '150px', 
    height: '40px', 
    borderRadius: '10px',
  };

    // 鼠标进入事件：高亮对应代码
    const handleMouseEnter = () => {
      setHighlightedLines(new Set(data.relatedCodeLines));
    };
  
    // 鼠标离开事件：取消高亮
    const handleMouseLeave = () => {
      setHighlightedLines(new Set());
    };
  
  return (
    <div 
      style={style} 
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        textAlign: 'center',
        height: '100%',
      }}>
        <Handle type="target" position={Position.Top} />
        <div>{data.label}</div>
        <Handle type="source" position={Position.Bottom} />
      </div>
    </div>
  );
};

const nodeTypes = {
  customNodeType: CustomNodeComponent, 
};

interface FlowChartProps {
  id: string;
}

interface OptimizationPoint {
  description: string;
  impact: string;
}

interface OptimizationResult {
  executionTime: string;
  optimizationPoints: OptimizationPoint[];
  estimatedTimeBefore: string;
  timeImprovement: number;
  cpuUsageReduction: string;
  memoryUsageReduction: string;
}

const FlowChart: React.FC<FlowChartProps> = ({ id }) => {

  const [leftComponent, setLeftComponent] = useState(''); 
  const [rightComponent, setRightComponent] = useState('optimization'); 
  
  const [leftNodes, setLeftNodes, onLeftNodesChange] = useNodesState([]);
  const [leftEdges, setLeftEdges, onLeftEdgesChange] = useEdgesState([]);
  const [rightNodes, setRightNodes, onRightNodesChange] = useNodesState([]);
  const [rightEdges, setRightEdges, onRightEdgesChange] = useEdgesState([]);

  const { setHighlightedLines } = useContext(CodeHighlightContext);
  const { highlightedLines } = useContext(CodeHighlightContext);

  const [selectedNode, setSelectedNode] = useState<LogicalNode | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);


  useEffect(() => {
    const baseUrlLeft = 'http://127.0.0.1:8080/api/Home/FlowChart_final';
    const baseUrlRight = 'http://127.0.0.1:8080/api/Home/FlowChart_raw';

    const fetchFlowChartData = async (dataset: number) => {
      const baseUrl = dataset === 1 ? baseUrlLeft : baseUrlRight;
      const url = `${baseUrl}?QueryId=${id}`;

      try {
        const response = await axios.get(url);
        const { logicalNodes, logicalEdges } = response.data.data;

        const nodesData = logicalNodes.map((node: LogicalNode) => ({
          id: node.id.toString(),
          type: 'customNodeType',
          data: { ...node, label: `${node.label}: ${node.operator}` },
          position: { x: 0, y: 0 },
        }));

        const edgesData = logicalEdges.map((edge: LogicalEdge) => ({
          id: `e${edge.source}-${edge.target}`,
          source: edge.source.toString(),
          target: edge.target.toString(),
          animated: true,
        }));

        const { nodes, edges } = getLayoutedElements(nodesData, edgesData);

        // Depending on the dataset, update the respective flowchart state
        if (dataset === 1) {
          setLeftNodes(nodes);
          setLeftEdges(edges);
        } else {
          setRightNodes(nodes);
          setRightEdges(edges);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    fetchFlowChartData(1);
    fetchFlowChartData(0);  
  }, [id, setLeftNodes, setLeftEdges, setRightNodes, setRightEdges]);

  useEffect(() => {
    const fetchOptimizationResult = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8080/api/Report/Query_optimization_result?QueryId=${id}`
        );
        setOptimizationResult(response.data.data);
      } catch (error) {
        console.error("Error fetching optimization result", error);
      }
    };

    fetchOptimizationResult();
  }, [id]);


  const renderLogicalPlan = () => {
    return leftNodes.map((node: any) => {
      const { label, operator, targetColumns, targetSteps, details } = node.data;
  
      // Ensure all fields have a value, replacing empty ones with "NULL"
      const displayLabel = label || "NULL";
      const displayDetails = details || "NULL";
  
      return (
        <div key={node.id} className="logical-plan-step">
          {/* Display the step in the format "Step X: details" */}
          <p><strong>Step {node.data.id}: </strong>{displayDetails}</p>
        </div>
      );
    });
  }
  

  const handleNodeClick = (event: React.MouseEvent, node: FlowChartNode) => {

    console.log(node.data.relatedCodeLines)

    setHighlightedLines(new Set(node.data.relatedCodeLines));
    setSelectedNode(node.data);
    setIsModalVisible(true);
  };

  useEffect(() => {
    console.log('highlightedLines 已更新:', highlightedLines);
  }, [highlightedLines]);
  

  const handleCloseModal = () => {
    setIsModalVisible(false);
    setSelectedNode(null);
  };

  const renderOptimizationContent = () => {
    if (!optimizationResult) {
      return <div>Loading optimization analysis results...</div>;  // 数据为空时显示
    }

    return (
      <div className='optimization-container'>
        <div className='time-header'>
          <div className="execution-time">
            <strong>Execution time: </strong> <span>{optimizationResult.executionTime}s</span>
          </div>
          <strong>Estimated execution time variation：</strong>
            <span>
              {optimizationResult.estimatedTimeBefore}s.  
            </span>
          </div>
        <div className="cpu-memory">
          <div className="cpu">
            <span>📊</span> <strong>Time usage:</strong> Decline about{" "}{optimizationResult.timeImprovement}%
          </div>
          <div className="cpu">
            <span>📊</span> <strong>CPU usage:</strong> Decline about{" "}
            {optimizationResult.cpuUsageReduction}%
          </div>
          <div className="memory">
            <span>📊</span> <strong>Memory usage:</strong> Decline about{" "}
            {optimizationResult.memoryUsageReduction}%
          </div>
        </div>
        <div className="optimization-points">
          <h3>Optimization-points: </h3>
          <ul>
            {optimizationResult.optimizationPoints.map((point, index) => (
              <li key={index}>
                <span className="checkbox">✅</span>
                <span>{point.description}</span>
                <span className="impact">{point.impact}</span>
              </li>
            ))}
          </ul>
        </div>
    
      </div>
    );
  };



  return (
    <div className="flowchart-container">
      <div className="flowchart-plan">
        <div className="flow-chart-header">Final Graph</div>
          <ReactFlow
            nodes={leftNodes}
            edges={leftEdges}
            onNodesChange={onLeftNodesChange}
            onEdgesChange={onLeftEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
            nodeTypes={nodeTypes}

          >
            <Background />
          </ReactFlow>
      </div>
      <div className="flowchart-plan-raw">
        <div className="flow-chart-header">Original Graph</div>
        <div className="react-flow-wrapper">
          <ReactFlow
            nodes={rightNodes}
            edges={rightEdges}
            onNodesChange={onRightNodesChange}
            onEdgesChange={onRightEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
            nodeTypes={nodeTypes}
            style={{ width: '100%', height: '100%' }}
          >
            <Background />
          </ReactFlow>
        </div>
      </div>
      <div className="flowchart-text">
        <div className="flow-chart-header2">Logical Plan</div>
        {renderLogicalPlan()}
      </div>
      <div className="flowchart-result">
        <div className="flow-chart-header2">Before Optimization vs After Optimization</div>
        { renderOptimizationContent()}
      </div>
  
      {/* Modal for Node Details */}
      {selectedNode && (
        <Modal
          title={<div className="modal-title">Node Information</div>}
          visible={isModalVisible}
          onOk={handleCloseModal}
          onCancel={handleCloseModal}
          footer={[
            <Button key="back" onClick={handleCloseModal} style={{ fontSize: '16px' }}>
              Back
            </Button>
          ]}
        >
          <div className="modal-content">
            <div className="info-row">
              <span className="info-label">Operator:</span> <span className="info-value">{selectedNode.operator}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Target Columns:</span> <span className="info-value">{selectedNode.targetColumns}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Target Steps:</span> <span className="info-value">{selectedNode.targetSteps}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Details:</span> <span className="info-value">{selectedNode.details}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Related Code Lines:</span> <span className="info-value">{selectedNode.relatedCodeLines.join(', ')}</span>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default FlowChart;

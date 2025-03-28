import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import MyResultTable from "./MyResultTable";
import ApplyButton from "../utilsCompoents/ApplyButton";
import "./DataLineage.css";
import { Image, Empty } from "antd";
import { Network } from "vis-network"; // 直接从 vis-network 导入
import "vis-network/styles/vis-network.css";
import SourceDataComponent from "./SourceDataComponent";

interface NodeData {
  id: string;
  type: string;
  dataname: string;
  targetData: string;
  operator: string;
  code: string;
}

interface EdgeData {
  from: string;
  to: string;
  label: string;
}

interface LineageData {
  LineageData: NodeData[];
  EdgeData: EdgeData[];
};

interface ResultDisplayProps {
  id: string;
  code_result :any[];
}

const DataLineage: React.FC<ResultDisplayProps> = ({ id, code_result }) => {
  const [showFilters, setShowFilters] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [lineageData, setLineageData] = useState<LineageData | null>(null);

  const [returnTrigger, setReturnTrigger] = useState(false);

  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null); 
  const [showDetail, setShowDetail] = useState<boolean>(false); 
  const networkRef = useRef<HTMLDivElement | null>(null); 
  const networkInstanceRef = useRef<Network | null>(null);

  const [isFullScreen, setIsFullScreen] = useState(false);
  
  useEffect(() => {
    if (lineageData && networkRef.current) {
      // 构造节点和边
      const nodes = lineageData.LineageData.map((data) => ({
        id: data.id,
        label: data.dataname,
        title: `Operator: ${data.operator}\n Code: ${data.code}`, // 鼠标悬浮时显示操作和代码
        color: { background: "#97C2FC", border: "#2B7CE9" }, // 默认颜色
        size: 15, 
      }));

      // 设置不同的颜色，区分起始节点和最后节点
      const edgeFromSet = new Set(lineageData.EdgeData.map((edge) => edge.from)); // 出度
      const edgeToSet = new Set(lineageData.EdgeData.map((edge) => edge.to)); // 入度

      lineageData.LineageData.forEach((node) => {
        // 判断是否为起始节点（没有入度）
        if (!edgeToSet.has(node.id)) {
          const index = nodes.findIndex((n) => n.id === node.id);
          if (index !== -1) {
            nodes[index].color = { background: "#FFDD00", border: "#FFBB00" }; // 起始节点颜色
          }
        }
        // 判断是否为最后节点（没有出度）
        if (!edgeFromSet.has(node.id)) {
          const index = nodes.findIndex((n) => n.id === node.id);
          if (index !== -1) {
            nodes[index].color = { background: "#00FF00", border: "#00BB00" }; // 最后节点颜色
          }
        }
      });

      const edges = lineageData.EdgeData.map((edge, index) => ({
        id: `${edge.from}-${edge.to}-${index}`, // 为每条边生成唯一的ID
        from: edge.from,
        to: edge.to,
        label: edge.label,
        font: { size: 12, color: "#343434" },
        width: 1,
      }));

      const data = { nodes, edges };

      const options = {
        autoResize: true,
        nodes: {
          shape: "box",
          size: 20,
          font: { size: 16 },
          borderWidth: 2,
        },
        edges: {
          width: 2,
          arrows: { to: { enabled: true, scaleFactor: 0.5 } },
          color: { color: "#848484", highlight: "#FF0000" },
          label: "", // 这里使用一个空字符串来避免不兼容的类型
          font: {
            size: 12,
            color: "#343434", // 标签文字颜色
          },
        },
        interaction: {
          hover: true,
          dragNodes: true, // 启用节点拖动
        },
        physics: {
          enabled: true, // 启用物理引擎让图形更动态
          forceAtlas2Based: {
            gravitationalConstant: -26,
            centralGravity: 0.015,
            springLength: 230,
            springConstant: 0.08,
          },
        },
        layout: {
          hierarchical: {
            direction: "UD", // "UD" 表示上到下（Up to Down），"DU" 为下到上（Down to Up）
            levelSeparation: 100, // 每一层的间隔
            nodeSpacing: 50, // 节点间距
            sortMethod: "directed", // 按照边的方向排列节点
          },
        },
      };

      const networkInstance = new Network(networkRef.current, data, options);
      networkInstanceRef.current = networkInstance; 

      networkInstance.on("click", (params) => {
        const clickedNode = lineageData.LineageData.find((node) => node.id === params.nodes[0]);
        if (clickedNode && !edgeToSet.has(clickedNode.id)) {
          setSelectedNode(clickedNode);
          setShowDetail(true); 
        }
      });
    }
  
  }, [lineageData]);
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsFullScreen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);


  const handleReturnClick = () => {
    setReturnTrigger(true); 
    setLineageData(null); 
    setShowDetail(false);
    setSelectedColumn(null); 

  };

  // 处理列点击事件
  const handleColumnClick = async (columnName: string) => {
    setSelectedColumn(columnName);
    const lineage = await fetchLineageData(columnName);
    setLineageData(lineage);
  };

  // 向后端请求溯源数据
  const fetchLineageData = async (columnName: string) => {
    try {
      const response = await axios.post("http://127.0.0.1:8080/api/Report/lineageData", {
        QueryId: id,
        columnName: columnName,
      });
      return response.data.data; // 该数据应包含节点和边的信息
    } catch (error) {
      console.error("Failed to fetch lineage data:", error);
      return null;
    }
  };

  return (
    <div className="DataLineage-container">

          <div className="DataLineage-content">
            <div className="DataLineage-left-container">
              <div className="DataLineage-header">
                  <ApplyButton tooltip="Filter" onClick={() => setShowFilters(!showFilters)} className="allpy-button-Result-DataLineage" />
                  <div className="DataLineage-title1">Query Result</div>
              </div>


              <MyResultTable code_result={code_result} showFilters={showFilters} onColumnClick={handleColumnClick} />
            </div>
            <div className="DataLineage-middle-container">
                <div className="DataLineage-header">
                  <div className="DataLineage-title">Data Lineage</div>
                  <ApplyButton tooltip="Return" onClick={handleReturnClick} className="allpy-button-Result-DataLineage" />
                </div>

                { !lineageData? (
                  <div className="empty-lineage-container">
                    <div className="empty-lineage-message">
                      <p>Please select a column to view lineage.</p>
                      <div className="empty-lineage-icon">
                        <img src="/locate.png" alt="Placeholder Chart" style={{ width: "50px", height: "50px" }} />
                      </div>
                    </div>
                  </div>                 
                ) : (
                  <div
                    ref={networkRef}
                    className="DataLineageGraph-container"
                    style={{
                      height: isFullScreen ? "100vh" : "444px", 
                      width: isFullScreen ? "100vw" : "100%", 
                      position: isFullScreen ? "fixed" : "relative", 
                      top: 0,
                      backgroundColor: 'rgba(251, 251, 251, 0.95)',
                      left: 0,
                      zIndex: isFullScreen ? 1000 : "auto", 
                    }}
                />
                )}
       
            </div>

            <div className="DataLineage-right-container">

              <div className="DataLineage-header">
                  <div className="DataLineage-title">Source Data </div>
                  <ApplyButton tooltip="Return" onClick={handleReturnClick} className="allpy-button-Result-DataLineage" />
                </div>

              {selectedNode ? (
                <SourceDataComponent
                      showFilters={showFilters}
                      dataName={selectedNode.dataname}
                      dataType={selectedNode.type}
                      id={id}
                    />
              ): (
                <div className="empty-lineage-container">
                  <div className="empty-lineage-message">
                    <p>Please select a column to view lineage.</p>
                    <div className="empty-lineage-icon">
                      <img src="/locate.png" alt="Placeholder Chart" style={{ width: "50px", height: "50px" }} />
                    </div>
                  </div>
                </div>
              )}

            </div>  

          </div>
 

    </div>
  );
};

export default DataLineage;
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';
import "./DatabaseSchemaGraph.css"
import ManageDataMenuComponent from './ManageDataMenuComponent';
import { createPortal } from 'react-dom';

// 假设这是从后端接口得到的数据类型
type SourceData = {
  id: number;
  name: string;
  nodeType: string;
  dataType: string;
  fks: string;
};

type ColumnData = {
  id: number;
  name: string;
  nodeType: string;
  dataType: string;
  source: number;
  sourceName: string;
};

type DataLinks = {
  id: number;
  source : number;
  target: number;
  condition: string;
};


const drag = function(simulation: any) {
  return function(selection: d3.Selection<SVGCircleElement, any, SVGGElement, unknown>) {
    selection.call(
      d3.drag<SVGCircleElement, any>()
        .on("start", function(event, d) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", function(event, d) {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", function(event, d) {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );
  };
};


// 节点颜色函数
function colorNode(d: any) {
  switch (d.group) {
    case 'Data Type':
      switch (d.dataType){
        case 'json':
          return '#fc8e80';
        case 'graph':
          return '#e7f738';
        default:
          return '#4fa0ec'
      }
    
    case 'Column Type': 
      switch (d.dataType){
        case 'LONG_TEXT':
          return '#beaaff';
        case 'IMAGE':
          return '#ade8ff';
        default:
          return '#03c04f';
      }
    
    default: return 'gray';
  }
}

const DatabaseSchemaGraph: React.FC = () => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [links, setLinks] = useState<any[]>([]);

  const [tooltipInfo, setTooltipInfo] = useState({type: '', label: '', group: '', dataType: '', x: 0, y: 0, fks: ''});
  const [showTooltip, setShowTooltip] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);

  const svgRef = useRef<SVGSVGElement>(null);

  const fullScreenSvgRef = useRef<SVGSVGElement>(null);

  const defaultSelectedNode = {
    id: 'default',
    label: 'Please Select a node',
    group: 'None',
    dataType: 'N/A',
    sourceName: 'N/A'
  };

  const [selectedNode, setSelectedNode] = useState<any>(defaultSelectedNode);
  const [dataSourceList, setDataSourceList] = useState([]);
  const [selectedDataSource, setSelectedDataSource] = useState('dlbench');
  const [searchQuery, setSearchQuery] = useState('');
  const [showManageMenu, setShowManageMenu] = useState(false);

  useEffect(() => {
    const fetchDataSources = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8080/api/Report/read_datasource');
        const data = await response.json();
        setDataSourceList(data.data.response);  // 假设返回的数据是一个数组
      } catch (error) {
        console.error('Error fetching data sources:', error);
      }
    };
    fetchDataSources();
  }, []);

  const filteredDataSources = dataSourceList.filter((dataSource: string) =>
    dataSource.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 选择数据源
  const handleDataSourceChange = (event: any) => {
    setSelectedDataSource(event.target.value);
  };

  // 打开管理数据菜单
  const handleManageData = () => {
    setShowManageMenu(!showManageMenu);
  };


  useEffect(() => {
    // 获取后端数据并设置节点和链接
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8080/api/Report/findData`, {
          params: { datasource: selectedDataSource} 
        });
        if (response.data.code === 0) {
          const sourceData: SourceData[] = response.data.data.tables;
          const columnData: ColumnData[] = response.data.data.columns;
          const LinkData: DataLinks[] = response.data.data.dataLinks;
          
          // 创建节点
          const nodes = sourceData.map(sd => ({
            id: sd.id,
            label: sd.name,
            group: sd.nodeType,
            dataType: sd.dataType,
            sourceName: sd.name,
            fks: sd.fks
          })).concat(columnData.map(cd => ({
            id: cd.id,
            label: cd.name,
            group: cd.nodeType,
            source: cd.source,
            dataType: cd.dataType,
            sourceName: cd.sourceName,
            fks: "None"
          })));

          // 创建链接
          const links = columnData.map(cd => ({
            source: cd.source,
            target: cd.id,
            type: "column_link",
          })).concat(LinkData.map(t => ({
            source: t.source,
            target: t.target,
            type: "table_link",
          })));

          setNodes(nodes);
          setLinks(links);
        }
      } catch (error) {
        console.error("Error fetching data: ", error);
      }
    };

    fetchData();
  }, [selectedDataSource]);

  const drawGraph = (svgElement: SVGSVGElement | null, width: number, height: number) => {
    if (nodes.length && links.length && svgElement) {
      const svg = d3.select(svgElement);
      svg.selectAll('*').remove();

      // 创建力导向图
      const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink<any, any>(links).id(d => d.id).distance(75))
        .force("charge", d3.forceManyBody().strength(-65))
        .force("center", d3.forceCenter(width / 2, height / 2))
     //   .force("collide", d3.forceCollide(10));
      
      const link = svg.append("g")
        .selectAll("path")
        .data(links)
        .enter()
        .append("path")
        .attr("stroke", d => {
          let color = '#005b96';
          
          // 检查边的类型
          if (d.type === "column_link") {
            color = '#ffab00';
          } else if (d.type === "table_link") {
            const sourceNode = nodes.find(node => node.id === d.source);
            const targetNode = nodes.find(node => node.id === d.target);
            
            if (sourceNode && targetNode) {
              if (sourceNode.dataType == 'json') {
                color = '#e9a08b';
              } 
            }
            
          }
          
          return color;
        })
        .attr("marker-end", "url(#arrow)")
        .style("fill", "none");

      // 添加箭头标记
      svg.append("defs").append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 8) // 调整箭头位置
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("class", "arrowhead")
        .attr("fill", "#999"); 

      // 绘制节点
      const node = svg.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .selectAll("circle")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("r", d => {
          // 根据节点的类型设置节点的半径
          if (d.group === 'Data Type') {
            return 8; // 设置较大的半径
          } else {
            return 6; // 设置默认较小的半径
          }
        })
        .attr("fill", colorNode)
        .call(drag(simulation))
        .on('click', (event, d) => { // 注意参数的顺序
          setSelectedNode(d); // 使用第二个参数 d 来获取节点数据
          // 这里可以替换为更新状态或展示详细信息的逻辑
          alert(`Node ${d.label} clicked!`);
        });

      // 绘制节点标签
      const label = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(nodes)
        .enter()
        .append("text")
        .attr("class", "label")
        .text(d => d.label);

        simulation.on("tick", () => {
          // 添加边界限制，确保节点在SVG容器内
      
          // 更新连线位置，使用贝塞尔曲线
          link.attr("d", d => {
            const dx = d.target.x - d.source.x;
            const dy = d.target.y - d.source.y;
            const dr = Math.sqrt(dx * dx + dy * dy);
        
            // 创建一个曲线路径，dr 为曲线的半径，可以通过调整这个值来改变曲线的弯曲程度
            return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
          });
        
          
          node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        
          // 更新标签位置
          label
            .attr("x", d => d.x + 5) // 小偏移，防止标签与节点重叠
            .attr("y", d => d.y);
        });
  

        node.on('mouseover', function(event, d) {
          const [mouseX, mouseY] = d3.pointer(event);
          // 直接使用事件坐标，加上适当的偏移以定位悬浮窗
          setTooltipInfo({
            type: 'node',
            label: d.label,
            group: d.group,
            dataType: d.dataType,

            x: isFullScreen ? (mouseX - 800) : (event.offsetX - 105),
            y: isFullScreen ? (mouseY - 600) : (event.offsetX - 105),
            fks: d.fks
          });
          setShowTooltip(true);
        })
        .on('mouseout', () => {
          setShowTooltip(false);
        });
   }
  }

  useEffect(() => {
    if (isFullScreen && fullScreenSvgRef.current) {
      drawGraph(fullScreenSvgRef.current, window.innerWidth, window.innerHeight);
    }
    if (svgRef) {
      drawGraph(svgRef.current, 600, 400);
    }
  }, [isFullScreen, nodes, links, showManageMenu]);


    // 监听键盘 ESC 退出全屏
    useEffect(() => {
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') setIsFullScreen(false);
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    return (
        <div className="data-lake-container">
            <div className="DataLineage-header">
                <div className="DataLineage-title" style={{ marginLeft: '150px' }}>Data Lake</div>
                <select
                  className="data-lake-dropdown"
                  value={selectedDataSource}
                  onChange={handleDataSourceChange}
                >
                  <option value="dlbench">dlbench</option>
                  {filteredDataSources.map((dataSource, index) => (
                    <option key={index} value={dataSource}>{dataSource}</option>
                  ))}
                </select>
            </div>

          <div className="data-lake-visualization" >
              <svg ref={svgRef} width="100%" height="100%"></svg>
          </div>

          <div className="ManageDataMenu-visualization">
            <ManageDataMenuComponent datasource={selectedDataSource} />
          </div>
          
      {isFullScreen &&
        createPortal(
          <div 
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(215, 211, 211, 0.95)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <svg ref={fullScreenSvgRef} width={window.innerWidth} height={window.innerHeight} />
          </div>,
          document.body
        )}
  
      {showTooltip && (
        <div
          className={`tooltip ${showTooltip ? 'show' : ''}`}
          style={{ top: tooltipInfo.y, left: tooltipInfo.x, zIndex: 9999}}
        >
        {tooltipInfo.type === 'node' ? (
            <>
              <div >
                <span className="tooltip-title">Name:</span>
                <span className="tooltip-content">{tooltipInfo.label}</span>
              </div>
              <div style={{marginTop: "10px"}}>
                <span className="tooltip-title">Node Type:</span>
                <span className="tooltip-content">{tooltipInfo.group}</span>
              </div>
              <div style={{marginTop: "10px"}}>
                <span className="tooltip-title">Data Type:</span>
                <span className="tooltip-content">{tooltipInfo.dataType}</span>
              </div>
              <div style={{marginTop: "10px"}}>
                <span className="tooltip-title">FKs condition:</span>
                <span className="tooltip-content">{tooltipInfo.fks}</span>
              </div>
            </> ) : (
              <>
              
              
              </>
            )
          }
        </div>
      )}
    </div>
  );

};

export default DatabaseSchemaGraph;

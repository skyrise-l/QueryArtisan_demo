import React, { useEffect, useState, useRef } from 'react';
import * as d3 from 'd3';
import { createPortal } from 'react-dom';

// ===============【1. 数据接口定义】===============
interface BackendNode {
  id: number;
  label: string;
  attributes: { [key: string]: any };
}

interface BackendEdge {
  from: number;
  to: number;
  relation: string;
}

interface GraphData {
  nodes: BackendNode[];
  edges: BackendEdge[];
}

interface GraphRendererProps {
  graphData: GraphData;
}

// ===============【2. 组件定义】===============
const D3GraphRenderer: React.FC<GraphRendererProps> = ({ graphData }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const fullScreenSvgRef = useRef<SVGSVGElement>(null);

  const [displayedNodes, setDisplayedNodes] = useState<BackendNode[]>([]);
  const [displayedEdges, setDisplayedEdges] = useState<BackendEdge[]>([]);
  
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedAttribute, setSelectedAttribute] = useState<string>('');
  const [selectedNodeID, setSelectedNodeId] = useState<string>('');

  const [attributeOptions, setAttributeOptions] = useState<string[]>([]);

  const [graphDataState, setGraphDataState] = useState<GraphData>(graphData);
  const [colorMap, setColorMap] = useState<{ [relation: string]: string }>({});

  const [isFullScreen, setIsFullScreen] = useState(false);


  const [tooltipInfo, setTooltipInfo] = useState<{
    type: 'node' | 'edge' | null;
    label?: string;
    attributes?: { [key: string]: any }; // 仅节点使用
    relation?: string; // 仅边使用
    x: number;
    y: number;
  } | null>(null);

  const [showTooltip, setShowTooltip] = useState(false);

  const MAX_SEARCH_RESULTS = 1; 

  // ===============【3. 辅助函数】===============
  // 过滤无效边：保留后端数据中确实存在的节点之间的边
  const filterValidEdges = (data: GraphData): GraphData => {
    const validEdges = data.edges.filter((edge) => {
      const fromNode = data.nodes.find((node) => node.id === edge.from);
      const toNode = data.nodes.find((node) => node.id === edge.to);
      return fromNode && toNode;
    });
    return { ...data, edges: validEdges };
  };

  // 为不同的 relation 生成不同的颜色
  const generateUniqueColorMap = (edges: BackendEdge[]): { [relation: string]: string } => {
    const colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d'];
    const map: { [relation: string]: string } = {};
    edges.forEach((edge, index) => {
      if (!map[edge.relation]) {
        map[edge.relation] = colors[index % colors.length];
      }
    });
    return map;
  };

  // BFS 展开图（深度为 depth）
  const expandGraph = (data: GraphData, startNodes: BackendNode[], depth: number) => {
    const nodeMap = new Map<number, BackendNode>(data.nodes.map((n) => [n.id, n]));
    const queue: BackendNode[] = [...startNodes];
    const visited = new Set<number>(startNodes.map((n) => n.id));
    let level = 0;

    while (queue.length > 0 && level < depth) {
      const nextQueue: BackendNode[] = [];

      for (const node of queue) {
        // 找到所有与当前节点相连的边，并获取对端节点
        const neighbors = data.edges
          .filter((e) => e.from === node.id || e.to === node.id)
          .map((e) => (e.from === node.id ? nodeMap.get(e.to) : nodeMap.get(e.from)))
          .filter((n) => n && !visited.has(n.id));

  
        for (const neighbor of neighbors) {
          if (neighbor) {
            visited.add(neighbor.id);
            nextQueue.push(neighbor);
          }
        }
      }

      queue.length = 0;
      queue.push(...nextQueue);
      level++;
    }

    // 返回 BFS 扩展后所有访问到的节点
    const result: BackendNode[] = [];
    visited.forEach((id) => {
      const n = nodeMap.get(id);
      if (n) result.push(n);
    });
    return result;
  };

    // ===============【6. 用 D3.js 进行力导向图渲染】===============
    const drawGraph = (svgElement: SVGSVGElement, width: number, height: number, distance: number) => {
      if (!svgElement) return;
  
      const svg = d3.select(svgElement);
      svg.selectAll('*').remove();
  
      // 2) 将我们的数据转换为 d3-friendly 的数据
      // d3 需要的节点结构：{ id: number/string, ... }
      const d3Nodes = displayedNodes.map((node) => ({
        ...node,
        // d3 一般识别 id 字段，也可以用 name 等
        // 这里保留 node 原有数据
      }));
      
      // d3 需要的边结构：{ source: 节点id, target: 节点id, ...}
      const d3Edges = displayedEdges.map((edge) => ({
        source: edge.from,
        target: edge.to,
        label: edge.relation,
        color: colorMap[edge.relation] || '#999',
      }));
  
      // 3) 创建力导向图
      const simulation = d3.forceSimulation(d3Nodes as d3.SimulationNodeDatum[])
        .force('link', d3.forceLink(d3Edges).id((d: any) => d.id).distance(distance))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2));
  
      // 4) 添加连线
      const link = svg.append('g')
        .attr('stroke', '#999')
        .selectAll('line')
        .data(d3Edges)
        .enter()
        .append('line')
        .attr('stroke-width', 2)
        .attr('stroke', (d) => d.color);
  
      // 5) 添加节点（圆）
      const node = svg.append('g')
        .selectAll('circle')
        .data(d3Nodes)
        .enter()
        .append('circle')
        .attr('r', 20)
        .attr('fill', '#81cee6')
        .call(
          d3.drag<SVGCircleElement, any>()
            .on('start', (event, d: any) => {
              if (!event.active) simulation.alphaTarget(0.3).restart();
              d.startX = event.x;
              d.startY = event.y;
              d.fx = d.x;
              d.fy = d.y;
            })
            .on('drag', (event, d: any) => {
              d.fx = event.x;
              d.fy = event.y;
            })
            .on('end', (event, d: any) => {
              if (!event.active) simulation.alphaTarget(0);
        
              // 计算鼠标拖拽的移动距离
              const dx = event.x - d.startX;
              const dy = event.y - d.startY;
              const distance = Math.sqrt(dx * dx + dy * dy);
        
              // 只有在拖拽距离很小的时候，才触发点击
              if (distance < 5) {
                handleNodeClick(d);
              }
        
              d.fx = null;
              d.fy = null;
            })
        );
  
      // 6) 节点文本
      const label = svg.append('g')
        .selectAll('text')
        .data(d3Nodes)
        .enter()
        .append('text')
        .text((d: any) => d.label)
        .attr('font-size', '12px')
        .attr('text-anchor', 'middle')
        .attr('dy', '.3em')
        .attr('fill', '#000');
        
  
      // 7) 力导向图每次迭代时更新圆与线的位置
      simulation.on('tick', () => {
        link
          .attr('x1', (d: any) => d.source.x)
          .attr('y1', (d: any) => d.source.y)
          .attr('x2', (d: any) => d.target.x)
          .attr('y2', (d: any) => d.target.y);
  
        node
          .attr('cx', (d: any) => d.x)
          .attr('cy', (d: any) => d.y);
  
        label
          .attr('x', (d: any) => d.x)
          .attr('y', (d: any) => d.y);
      });
  
      node.on('mouseover', function(event, d) {
        const [mouseX, mouseY] = d3.pointer(event);
        setTooltipInfo({
          type: 'node',
          label: d.label,
          attributes: d.attributes, 
          x: isFullScreen ? mouseX + 15 -600 : (800 + mouseX + 15),
          y: isFullScreen ? mouseY + 15 -100 : ( mouseY + 15),
        });
        setShowTooltip(true);
      })
      .on('mouseout', () => {
        setShowTooltip(false);
      });
  
      link.on('mouseover', function(event, d) {
        const [mouseX, mouseY] = d3.pointer(event);
      
        setTooltipInfo({
          type: 'edge',
          label: d.label, // 关系类型
          x: isFullScreen ? mouseX + 15 : (800 + mouseX + 15),
          y: isFullScreen ? mouseY + 15 : (mouseY + 15),
        });
      
        setShowTooltip(true);
      })
      .on('mouseout', () => {
        setShowTooltip(false);
      });
  
    };

  const handleNodeClick = (d: any) => {
    // 1. 找到点击的节点
    const matchingNodes = graphDataState.nodes.filter(
      (node) => node.id === d.id
    );
  

    console.log(matchingNodes);
    // 2. 扩展 BFS（只添加新节点）
    const expandedNodes = expandGraph(graphDataState, matchingNodes, 1)
       .filter((newNode) => !displayedNodes.some((n) => n.id === newNode.id));
  
    // 3. 筛选边（包括原有 + 新的）
    const expandedEdges = graphDataState.edges.filter(
      (edge) =>
        (displayedNodes.some((n) => n.id === edge.from) || 
         expandedNodes.some((n) => n.id === edge.from)) &&
        (displayedNodes.some((n) => n.id === edge.to) || 
         expandedNodes.some((n) => n.id === edge.to))
    );

    console.log(expandedNodes);
  
    // 4. 更新状态（避免重复）
    setDisplayedNodes([...displayedNodes, ...expandedNodes]);
    setDisplayedEdges([...displayedEdges, ...expandedEdges]);
  };

  // ===============【4. 数据初始化】===============
  //   1) 过滤无效边
  //   2) 生成关系-颜色映射
  //   3) 默认选中最小 ID 节点作为搜索条件
  useEffect(() => {
    if (!graphData.nodes || graphData.nodes.length === 0) return;
    
    // 过滤无效边
    const filtered = filterValidEdges(graphData);
    setGraphDataState(filtered);

    // 生成颜色映射
    const newColorMap = generateUniqueColorMap(filtered.edges);
    setColorMap(newColorMap);

    const allAttributes = new Set<string>();
    graphData.nodes.forEach(node => {
      Object.keys(node.attributes).forEach(attr => allAttributes.add(attr));
    });

    // 更新选择框选项
    setAttributeOptions(Array.from(allAttributes));

    // 默认搜索条件：最小 ID 节点
    const initialNode = filtered.nodes.reduce((prev, curr) => (prev.id < curr.id ? prev : curr));
    setSearchTerm(String(initialNode.id));
    setSelectedNodeId(String(initialNode.id));

  }, [graphData]);

  const handleSearch = ()  => {
    if (!searchTerm || !graphDataState.nodes) return;

    // 1) 找到匹配节点
    let matchingNodes: BackendNode[] = [];

    if (!selectedAttribute) {
      // 按 ID 搜索
      matchingNodes = graphDataState.nodes.filter(
        (node) => String(node.id) === searchTerm
      );
    } else {
      // 按属性值搜索
      matchingNodes = graphDataState.nodes
        .filter((node) =>
          node.attributes[selectedAttribute] &&
          String(node.attributes[selectedAttribute]) === searchTerm
        )
        .slice(0, MAX_SEARCH_RESULTS);
    }

    if (matchingNodes.length === 0) {
      setDisplayedNodes([]);
      setDisplayedEdges([]);
      return;
    }

    // 2) BFS 展开节点
    const expandedNodes = expandGraph(graphDataState, matchingNodes, 1);
    
    // 3) 筛选相应的边
    const expandedEdges = graphDataState.edges.filter(
      (edge) =>
        expandedNodes.some((n) => n.id === edge.from) &&
        expandedNodes.some((n) => n.id === edge.to)
    );

    setDisplayedNodes(expandedNodes);
    setDisplayedEdges(expandedEdges);
  }

  // ===============【5. 根据搜索展开图】===============
  useEffect(() => {
    handleSearch()
  }, [graphDataState]);


  useEffect(() => {
    if (svgRef.current) {
      drawGraph(svgRef.current, 450, 360, 150);
    }
  }, [displayedNodes, displayedEdges]);


  const handleSearchInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

    // 在全屏模式下重绘图形
    useEffect(() => {
      if (isFullScreen && fullScreenSvgRef.current) {
        drawGraph(fullScreenSvgRef.current, window.innerWidth, window.innerHeight, 220);
      }
    }, [isFullScreen]);
  
    // 监听键盘 ESC 退出全屏
    useEffect(() => {
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') setIsFullScreen(false);
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);
  

  // ===============【7. 简易搜索和属性选择 UI】===============
  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部固定搜索栏 */}
      <div
        style={{
          flexShrink: 0,
          padding: '10px',
          background: '#fafafa',
          borderBottom: '1px solid #ccc',
          position: 'sticky',
          top: 0,
          zIndex: 10
        }}
      >
        {/* 顶部搜索行（单行） */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* 属性选择框 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <label>Attribute:</label>
            <select
              style={{ padding: '4px', height: '36px' }}
              value={selectedAttribute}
              onChange={(e) => setSelectedAttribute(e.target.value)}
            >
              <option value="">ID</option>
              {attributeOptions.map(attr => (
                <option key={attr} value={attr}>
                  {attr}
                </option>
              ))}
            </select>
          </div>
  
          {/* Key 输入框 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <label>Key:</label>
            <input
              style={{ padding: '4px', height: '24px' }}
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={handleSearchInputKeyDown}
              placeholder="INPUT AND ENTER"
            />
          </div>
        </div>
      </div>

      {/* 绘图区域（可滚动） */}
      <div style={{ flexGrow: 1, overflow: 'auto' }}>
        <svg ref={svgRef} width={800} height={600} onClick={() => setIsFullScreen(true)} />
      </div>

      {showTooltip && tooltipInfo && (  // 确保 tooltipInfo 不是 null
        <div
          className={`tooltip ${showTooltip ? 'show' : ''}`}

          style={{ 
            position: 'absolute',  // 关键点，绝对定位
            top: tooltipInfo.y, 
            left: tooltipInfo.x,
            border: '1px solid black',
            padding: '8px',
            borderRadius: '5px',
            boxShadow: '0px 0px 5px rgba(0,0,0,0.2)',
            pointerEvents: 'none',
            zIndex: 9999,
          }}
        >
          {tooltipInfo.type === 'node' ? (
            <>
              {/* 遍历所有属性，动态渲染 */}
              {tooltipInfo.attributes && Object.entries(tooltipInfo.attributes).map(([key, value]) => (
                <div key={key} style={{ marginTop: "10px" }}>
                  <span className="new-tooltip-title">{key}:</span>
                  <span className="new-tooltip-content">{String(value) || "N/A"}</span>
                </div>
              ))}
            </>
          ) : (
            <>
              <div>
                <span className="new-tooltip-title">Edge:</span>
                <span className="new-tooltip-content">{tooltipInfo.label}</span>
              </div>
            </>
          )}
        </div>
      )}


      {isFullScreen &&
        createPortal(
          <div 
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(145, 145, 145, 0.95)',
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

    </div>
  );
};


export default D3GraphRenderer;

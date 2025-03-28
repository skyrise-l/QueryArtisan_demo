import React, { useEffect, useState } from "react";
import axios from "axios";
import MyResultTable from "../ReportPage/MyResultTable";
import "./SourceDataComponent2.css";
import GraphRenderer from "../ReportPage/GraphRenderer";

interface SourceDataComponentProps {
  dataName: string;
  dataType: string;
  id: string;
  showFilters: boolean;
}

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

const SourceDataComponent2: React.FC<SourceDataComponentProps> = ({
  id,
  dataType,
  dataName,
  showFilters,
}) => {
  const [data, setData] = useState<any[]>([]); // 存储获取到的 JSON 数组
  const [filteredData, setFilteredData] = useState<any[]>([]); // 存储过滤后的 JSON 数据
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1); // 当前页数
  const [itemsPerPage] = useState<number>(1); // 每页展示一行数据
  const [filterText, setFilterText] = useState<string>(""); // 过滤文本

  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] })

  // 获取数据的函数
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("http://127.0.0.1:8080/api/Report/getSourceData", {
        tableName: dataName,
      });
      if (dataType === "graph") {
        setGraphData(response.data.data || { nodes: [], edges: [] });
        setData([]); // 清空 JSON 数据，防止冲突
        setFilteredData([]);
      } else {
        setData(response.data.data || []);
        setFilteredData(response.data.data || []);
        setGraphData({ nodes: [], edges: [] }); // 清空 Graph 数据
      }
    } catch (err) {
      setError("Data load error, please try again");
    } finally {
      setLoading(false);
    }
  };

  // 过滤数据
  const filterData = (filterText: string) => {
    const filtered = data.filter((item) =>
      JSON.stringify(item).toLowerCase().includes(filterText.toLowerCase())
    );
    setFilteredData(filtered);
  };

  // 分页：获取当前页的数据
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredData.slice(indexOfFirstItem, indexOfLastItem);

  // 切换页数
  const handlePageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let page = parseInt(e.target.value, 10);
    if (!isNaN(page) && page > 0 && page <= Math.ceil(filteredData.length / itemsPerPage)) {
      setCurrentPage(page);
    }
  };

  // 监听过滤文本变化
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilterText(e.target.value);
    filterData(e.target.value);
    setCurrentPage(1); // 重置为第一页
  };

  // 在组件挂载后获取数据
  useEffect(() => {
    fetchData();
  }, [id, dataName]);

  // 渲染 JSON 数据
  const renderJsonData = () => {
    if (!data || data.length === 0) {
      return <div>No data</div>;
    }

    return (
        <div className="SourceDataComponent-json-container">
          <div className="SourceDataComponent-controls">
            <input
              type="text"
              placeholder="Filter JSON"
              value={filterText}
              onChange={handleFilterChange}
              className="SourceDataComponent-search-input"
            />
            <div className="SourceDataComponent-pagination">
              <span>Page:</span>
              <input
                type="number"
                value={currentPage}
                onChange={handlePageChange}
                min="1"
                max={Math.ceil(filteredData.length / itemsPerPage)}
                className="SourceDataComponent-page-input"
              />
            </div>
          </div>
          {currentItems.map((item, index) => (
            <div key={index} className="SourceDataComponent-json-item">
              <div className="SourceDataComponent-json-content">
                <pre>{JSON.stringify(item, null, 2)}</pre>
              </div>
            </div>
          ))}
        </div>
      );
    };

    const handleColumnClick = (columnName: string) => {
    };

    // 渲染表格数据
    const renderTableData = () => {
        if (!data || data.length === 0) {
          return <div>No data</div>;
        }
      
        return (
            <MyResultTable code_result={data} showFilters={showFilters} onColumnClick={handleColumnClick}  Height="340px"/>
        );
    };



    const renderData = () => {
        switch (dataType) {
            case "table":
                return renderTableData();
            case "json":
                return renderJsonData();
            case "graph":
                return  <GraphRenderer graphData={graphData} />
            default:
                return <div>error data type</div>;
        }
    };

  // 渲染加载和错误信息
  if (loading) {
    return (
      <div className="loading-container">
        <div className="SourceDataComponent-loading-spinner" />
        <p style={{ marginLeft: '100px', marginTop: '20px', color: '#555', fontSize: '32px' }}> Loading data, please wait...</p>
      </div>
    );
  }

  if (error) {
    return <div>{error}</div>;
  }

  return <div className="SourceDataComponent-container2">{renderData()}</div>;
};

export default SourceDataComponent2;

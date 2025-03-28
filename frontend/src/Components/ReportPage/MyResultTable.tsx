import React, { useMemo, useState } from "react";
import "./MyResultTable.css";

interface MyResultTableProps {
  code_result: any[];
  showFilters: boolean;
  onColumnClick: (columnName: string) => void; 
  Height?: string;
}

const MyResultTable: React.FC<MyResultTableProps> = ({ code_result, showFilters, onColumnClick, Height }) => {
  const columns = useMemo(() => (code_result.length > 0 ? Object.keys(code_result[0]) : []), [code_result]);

  // 过滤状态
  const [filters, setFilters] = useState<{ [key: string]: string }>({});

  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 8; // 每页固定显示10条数据
  const totalPages = Math.ceil(code_result.length / rowsPerPage);

  // 处理筛选
  const handleFilterChange = (col: string, value: string) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      [col]: value,
    }));
  };

  // 计算筛选后的数据
  const filteredData = useMemo(() => {
    return code_result.filter((row) =>
      columns.every((col) =>
        filters[col] ? String(row[col]).toLowerCase().includes(filters[col].toLowerCase()) : true
      )
    );
  }, [code_result, filters, columns]);

  // 计算分页数据
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * rowsPerPage;
    return filteredData.slice(start, start + rowsPerPage);
  }, [filteredData, currentPage, rowsPerPage]);

  // 直接跳转到某一页
  const handlePageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let page = parseInt(e.target.value, 10);
    if (!isNaN(page) && page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="MyResultTable-wrapper" style={{ height: Height }} >
      {code_result.length === 0 ? (
        <p className="no-data-message">Loading data...</p>
      ) : (
        <>
          <div className="MyResultTable-scroll">
            <table className="MyResultTable-table">
              <thead>
                <tr>
                  {columns.map((col) => (
                    <th
                      key={col}
                      className="MyResultTable-title-column"
                      onClick={() => onColumnClick(col)} // 点击表头触发回调
                    >
                      {col}
                    </th>
                  ))}
                </tr>
                {showFilters && (
                  <tr>
                    {columns.map((col) => (
                      <th key={col}>
                        <input
                          type="text"
                          className="MyResultTable-filter-input"
                          value={filters[col] || ""}
                          onChange={(e) => handleFilterChange(col, e.target.value)}
                          placeholder="Filter..."
                        />
                      </th>
                    ))}
                  </tr>
                )}
              </thead>
              <tbody>
                {paginatedData.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {columns.map((col) => (
                      <td
                      key={col}
                      className="MyResultTable-title-cell"
                      onClick={() => onColumnClick(col)} // 点击单元格触发回调
                      >
                      {row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 分页控制 - 固定位置 */}
          <div className="MyResultTable-pagination">
            <button onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))} disabled={currentPage === 1}>
              Previous
            </button>
            <span>
              Page{" "}
              <input
                type="number"
                className="MyResultTable-page-input"
                value={currentPage}
                onChange={handlePageChange}
                min="1"
                max={totalPages}
              />{" "}
              of {totalPages}
            </span>
            <button onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default MyResultTable;

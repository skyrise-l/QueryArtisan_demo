// Navbar.tsx
import React from 'react';
import './Navbar.css';  // 引入CSS文件

// 为了让 Navbar 能够接收并使用 selectedContent 和 setSelectedContent，
// 我们定义一个类型或接口:
interface NavbarProps {
  selectedContent: string;
  setSelectedContent: React.Dispatch<React.SetStateAction<string>>;
}

const Navbar: React.FC<NavbarProps> = ({ selectedContent, setSelectedContent }) => {
  return (
    <div className="top-navbar">
      {/* Logo 和站点名称 */}
      <div className="navbar-left">
        <img className="navbar-logo" src="/think.png" alt="Logo" />
        <div className="site-title">QueryArtisan</div>
      </div>

      {/* 原先 LeftSidebar 中的内容移动到这里 */}
      <div className="navbar-right">
        <ul className="navbar-menu">
          <li
            className={selectedContent === 'QueryChat' ? 'selected' : ''}
            onClick={() => setSelectedContent('QueryChat')}
          >
            <img src="/query2.png" alt="Query Icon" className="sidebar-icon" />
            Query Chat
          </li>
          <li
            className={selectedContent === 'Process' ? 'selected' : ''}
            onClick={() => setSelectedContent('Process')}
          >
            <img src="/process.png" alt="Process Icon" className="sidebar-icon" />
            Query Process
          </li>
          <li
            className={selectedContent === 'Report' ? 'selected' : ''}
            onClick={() => setSelectedContent('Report')}
          >
            <img src="/result.png" alt="Result Icon" className="sidebar-icon" />
            Final Report
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Navbar;

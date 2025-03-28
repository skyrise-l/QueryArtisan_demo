import "./AnalyzeResult.css";
import React, { useState, useEffect } from "react";
import ApplyButton from "../utilsCompoents/ApplyButton";
import { Image, Button, Carousel, Empty } from "antd";


interface AnalyzeResultProps {
  id: string;
  codeResult: string;
  LLMResult: string;
  images: string[];
}

const AnalyzeResult: React.FC<AnalyzeResultProps> = ({ id, codeResult, LLMResult, images }) => {

  const [currentImageIndex, setCurrentImageIndex] = useState(0); 

  const formatLLMReport = (text: string) => {
    if (!text) return "<p>No report available.</p>";
  
    // 去除开头多余的换行
    text = text.replace(/^\s+/, "");
  
    // 按换行符拆分文本为数组
    const lines = text.split("\n").filter(line => line.trim() !== "");
  
    // 处理文本格式
    const formattedText = lines
      .map((line, index) => {
        // 标题加粗
        line = line.replace(/(Chart \d+:|Summary|Analysis Summary)/g, "<strong>$1</strong>");
  
        // 自动加粗或高亮“冒号前的内容”
        line = line.replace(/([^:]+):/g, '<strong class="highlight">$1</strong>:');
  
        return `<p class="${index % 2 === 0 ? "even-row" : "odd-row"}">${line}</p>`;
      })
      .join(""); // 组合成HTML
  
    return formattedText;
  };

  const nextImage = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex(
      (prevIndex) => (prevIndex - 1 + images.length) % images.length
    );
  };


  return (
    <div className="DataLineage-container">

        <div className="DataLineage-content">
            <div className="DataLineage-left-container">
              <div className="DataLineage-header">
                  <div className="DataLineage-title2">LLM Report</div>
              </div>
              <div className="llm-report-container">
                <div 
                  className="llm-report-content"
                  dangerouslySetInnerHTML={{ __html: formatLLMReport(LLMResult) }}
                />
              </div>
            </div>


        <div className="DataLineage-middle-container">
            <div className="DataLineage-header">
              <ApplyButton tooltip="Next" onClick={nextImage} className="allpy-button-Pre-Next" />
              <div className="DataLineage-title2">Visualized results</div>
              <ApplyButton tooltip="Pre" onClick={prevImage} className="allpy-button-Pre-Next" />
            </div>
            {images.length === 0 ? (
                <Empty description="No images" className="no-image-placeholder" />
              ) : (
                <div className="image-carousel">
                  <div className="image-slide">
                    <Image src={`data:image/jpeg;base64,${images[currentImageIndex]}`} alt={`Visualization ${currentImageIndex + 1}`} />
                  </div>
                </div>
              )}
        </div>

        <div className="DataLineage-right-container">

        <div className="DataLineage-header">
            <div className="DataLineage-title2">Terminal output</div>
          </div>
          <div className="terminal-style">
            <div className="terminal-content">
              {codeResult.length === 0 ? (
                <p className="loading-message">Fetching code execution results...</p>
              ) : (
                codeResult.split("\n").map((line, index) => (
                  <div key={index} className="terminal-line">
                    <div className="terminal-prefix">➜</div>
                    <div className="terminal-text">{line}</div>
                  </div>
                ))
              )}
            </div>

          </div>  
      </div>

      </div>
    </div>

  );
};

export default AnalyzeResult;

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './CustomSearch.css';

interface CustomSearchProps {
  placeholder: string;
  onSearch: (searchText: string) => void;
  isLoading?: boolean;
  NewsearchText: string;
}

const CustomSearch: React.FC<CustomSearchProps> = ({
  placeholder,
  onSearch,
  isLoading = false,
  NewsearchText
}) => {
  const [searchText, setSearchText] = useState<string>('');
  const [showSuggestions, setShowSuggestions] = useState<boolean>(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSearchText(NewsearchText);
  }, [NewsearchText]);

  // 点击页面其他地方时，若不在容器内则关闭建议框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // 如果 wrapperRef 绑定的节点存在，且点击目标不在该节点内部，则关闭
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // 使用防抖来处理用户输入
  useEffect(() => {
    const debounceTimer = setTimeout(async () => {
      if (searchText.length > 2) {
        setShowSuggestions(true);

        try {
          const response = await axios.post(
            'http://127.0.0.1:8080/api/Home/GetQuerySuggestions?query=' +
              encodeURIComponent(searchText)
          );
          setSuggestions(response.data.data);
        } catch (error) {
          console.error('Error fetching suggestions', error);
        }
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 500);

    return () => clearTimeout(debounceTimer);
  }, [searchText]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value);
  };

  const handleSearch = () => {
    onSearch(searchText);
    setSearchText('');
    setShowSuggestions(false);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchText(suggestion);
    setShowSuggestions(false);
    onSearch(suggestion);
  };

  // 输入框聚焦时，如果已有足够输入文本，则显示建议
  const handleFocus = () => {
    if (searchText.length > 2) {
      setShowSuggestions(true);
    }
  };

  return (
    <div className="search-wrapper" ref={wrapperRef}>
      <div className="custom-search-container">
        <input
          ref={inputRef}
          type="text"
          placeholder={isLoading ? 'Searching... please wait' : placeholder}
          value={searchText}
          onChange={handleInputChange}
          className="custom-search-input"
          disabled={isLoading}
          onFocus={handleFocus}
        />
        <button onClick={handleSearch} className="custom-search-button" disabled={isLoading}>
          Query
        </button>
      </div>

      {showSuggestions && !isLoading && (
        <div className="suggestions-container">
          {suggestions.length > 0 ? (
            suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="suggestion-item"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </div>
            ))
          ) : (
            <div className="suggestion-item">No suggestions available</div>
          )}
        </div>
      )}
    </div>
  );
};

export default CustomSearch;

import React, { useState } from "react";
import VideoUploadForm from "./components/VideoUploadForm";
import ComputerCards from "./components/TvCards";
import { Menu } from "antd";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState(localStorage.getItem("activeTab") || "upload");

  const handleClick = (e) => {
    setActiveTab(e.key);
    localStorage.setItem("activeTab", e.key);
  };

  const menuItems = [
    { key: "upload", label: "Загрузка видео" },
    { key: "computers", label: "Список устройств" },
  ];

  return (
    <div>
      <Menu onClick={handleClick} selectedKeys={[activeTab]} mode="horizontal" items={menuItems} className="mainMenu"/>
      {activeTab === "upload" && <VideoUploadForm />}
      {activeTab === "computers" && <ComputerCards />}
    </div>
  );
}

export default App;

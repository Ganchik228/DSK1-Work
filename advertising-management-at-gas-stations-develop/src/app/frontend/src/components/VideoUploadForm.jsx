import React, { useState, useEffect } from "react";
import { Card, Button, Upload, message, Pagination, notification } from "antd";
import { UploadOutlined, SyncOutlined, DeleteOutlined } from "@ant-design/icons";
import { red } from "@ant-design/colors";
import "./VideoUploadForm.css";

function VideoUploadForm() {
  const API_URL = import.meta.env.VITE_API_URL;
  const [files, setFiles] = useState([]);
  const [uploadedVideos, setUploadedVideos] = useState([]);
  const [hoveredVideo, setHoveredVideo] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [isUploading, setIsUploading] = useState(() => {
    return localStorage.getItem('isUploading') === 'true';
  });
  const pageSize = 5;
  
  const paginatedVideos = uploadedVideos.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const fetchVideos = async () => {
    try {
      const res = await fetch(`${API_URL}/videos`);
      const data = await res.json();
      setUploadedVideos(data.videos);
    } catch (error) {
      console.error("Ошибка получения видео:", error);
    }
  };

  useEffect(() => { 
    fetchVideos(); 
  }, [API_URL]);

  useEffect(() => {
    localStorage.setItem('isUploading', isUploading);
  }, [isUploading]);

  const handleFileChange = ({ fileList }) => {
    const validFiles = fileList.filter(file => {
      const isVideo = file.type?.startsWith("video/");
      const isSizeValid = file.size / 1024 / 1024 < 500;
      return isVideo && isSizeValid;
    });
    setFiles(validFiles);
  };

  const handleRemoveFile = (file) => {
    setFiles(files.filter(f => f.uid !== file.uid));
  };

  const beforeUpload = (file) => {
    const isVideo = file.type.startsWith("video/");
    const isLt500M = file.size / 1024 / 1024 < 500;
    if (!isVideo) message.error("Только видео файлы!");
    if (!isLt500M) message.error("Максимальный размер 500MB!");
    return isVideo && isLt500M;
  };

  const handleSubmit = async () => {
    if (!files.length) {
      message.error("Выберите файлы для загрузки");
      return;
    }
    setIsUploading(true);
    setFiles([]);

    const key = `upload-${Date.now()}`;
    notification.info({
      key,
      message: 'Загрузка видео',
      description: 'Видео загружаются, пожалуйста, ожидайте...',
      icon: <SyncOutlined spin />,
      duration: 0,
    });
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append("files", file.originFileObj || file);
    });

    try {
      const response = await fetch(`${API_URL}/videos`, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      
      const info = result.results 
        ? (
          <div>
            {result.results.map((r, index) => (
              <div key={index}>{r.filename}: {r.status}</div>
            ))}
          </div>
        ) 
        : result.message;
        
      notification.success({
        key,
        message: 'Загрузка завершена',
        description: info,
        duration: 5,
      });
    } catch (error) {
      notification.error({
        key,
        message: 'Ошибка загрузки',
        description: error.message,
        duration: 5,
      });
    } finally {
      setIsUploading(false);
      fetchVideos();
    }
  };

  const handleDeleteCommonVideo = async (video) => {
    try {
      const formData = new FormData();
      formData.append("filenames", video);
      const response = await fetch(`${API_URL}/videos/common`, {
        method: "DELETE",
        body: formData,
      });
      if (response.ok) {
        message.success(`Видео ${video} удалено`);
        fetchVideos();
      } else {
        const err = await response.json();
        message.error(`Ошибка удаления ${video}: ${err.message || JSON.stringify(err)}`);
      }
    } catch (error) {
      message.error(`Ошибка удаления ${video}: ${error.message}`);
    }
  };

  return (
    <div className="vf-container">
      <Card className="vf-upload-card" title="Загрузка видео">
        <Upload
          multiple
          beforeUpload={beforeUpload}
          onChange={handleFileChange}
          fileList={files}
          onRemove={handleRemoveFile}
          accept="video/*"
          maxCount={10}
          action={null}
          customRequest={({ onSuccess }) => onSuccess("ok")}
          disabled={isUploading}
        >
          <Button 
            icon={<UploadOutlined />} 
            className="vf-upload-btn"
            disabled={isUploading}
          >
            Выберите файлы (Max: 10)
          </Button>
        </Upload>
        <Button 
          type="primary" 
          onClick={handleSubmit} 
          className="vf-submit-btn" 
          disabled={!files.length || isUploading}
        >
          {isUploading ? "Загрузка..." : "Загрузить"}
        </Button>
      </Card>
      
      <Card className="vf-videos-card" title="Загруженные видео">
        <div className="vf-videos-list">
          {paginatedVideos.map((video) => (
            <div 
              key={video} 
              className="vf-video-item"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                position: "relative",
                border: "1px solid #ddd",
                marginBottom: "4px",
                padding: "2px", 
                background: "#fafafa"
              }}
            >
              <span 
                className="vf-video-title"
                onMouseEnter={() => setHoveredVideo(video)}
                onMouseLeave={() => setHoveredVideo(null)}
              >
                {video}
              </span>
              <Button 
                type="text" 
                icon={<DeleteOutlined style={{ color: red.primary }} />} 
                onClick={() => handleDeleteCommonVideo(video)}
              />
              {hoveredVideo === video && (
                <div className="vf-preview-popup" style={{ left: "100%", top: "50%", transform: "translate(10px, -50%)" }}>
                  <img src={`${API_URL}/videos/preview/${video}`} alt={video} />
                </div>
              )}
            </div>
          ))}
        </div>
        <Pagination
          current={currentPage}
          pageSize={pageSize}
          total={uploadedVideos.length}
          onChange={setCurrentPage}
          style={{ textAlign: "center", margin: "10px 0" }}
        />
      </Card>
    </div>
  );
}

export default VideoUploadForm;
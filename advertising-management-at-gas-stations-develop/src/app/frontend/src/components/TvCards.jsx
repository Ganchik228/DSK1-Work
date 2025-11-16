import React, { useEffect, useState } from "react";
import { Card, Button, message, Select, Progress, Modal, Checkbox, Collapse, Popconfirm, List } from "antd";
import { DeleteOutlined, ReloadOutlined, SyncOutlined, PlusOutlined, LoginOutlined, LogoutOutlined, EditOutlined } from '@ant-design/icons';
import CategoryMenu from "./CategoryMenu";
import AuthModal from "./AuthModal";
import EditTvModal from "./EditTvModal";
import "./TvCards.css";

const { Meta } = Card;

function TvCards() {
  const API_URL = import.meta.env.VITE_API_URL;
  const [tvs, setTvs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [syncingTvId, setSyncingTvId] = useState(null);
  const [currentPages, setCurrentPages] = useState({});
  const [filterCat, setFilterCat] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [tvCurrentVideo, setTvCurrentVideo] = useState({});
  const [reorderModalVisible, setReorderModalVisible] = useState(false);
  const [currentTvForReorder, setCurrentTvForReorder] = useState(null);
  const [reorderVideos, setReorderVideos] = useState([]);
  const [isSavingReorder, setIsSavingReorder] = useState(false);
  const [deletionModalVisible, setDeletionModalVisible] = useState(false);
  const [deletionCurrentTv, setDeletionCurrentTv] = useState(null);
  const [deletionSelectedVideos, setDeletionSelectedVideos] = useState({});
  const [restartingTvId, setRestartingTvId] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [availableVideos, setAvailableVideos] = useState([]);
  const [selectedVideos, setSelectedVideos] = useState([]);
  const [currentTvForAdd, setCurrentTvForAdd] = useState(null);
  const [isDeploying, setIsDeploying] = useState(false);
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken') || null);
  const [isAuthModalVisible, setIsAuthModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [currentTvForEdit, setCurrentTvForEdit] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  const handleLogin = async (credentials) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(credentials.username)}&password=${encodeURIComponent(credentials.password)}`
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('authToken', data.access_token);
        setAuthToken(data.access_token);
        setIsAuthModalVisible(false);
        message.success("Успешная авторизация");
        return true;
      } else {
        const error = await response.json();
        message.error("Ошибка авторизации: " + error.detail);
        return false;
      }
    } catch (error) {
      console.error("Ошибка при авторизации", error);
      message.error("Ошибка при авторизации");
      return false;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setAuthToken(null);
    message.success("Вы вышли из системы");
  };
  
  const handleEditSave = async (values) => {
    if (!authToken || !currentTvForEdit) return;
    
    setIsEditing(true);
    try {
      const updateRequests = [];
      
      if (values.machine_name !== currentTvForEdit.name) {
        updateRequests.push(
          fetch(`${API_URL}/admin/tvs/${currentTvForEdit.id}/name/${encodeURIComponent(values.machine_name)}`, {
            method: "PATCH",
            headers: { "Authorization": `Bearer ${authToken}` }
          })
        );
      }
      
      if (values.ip_address !== currentTvForEdit.address) {
        updateRequests.push(
          fetch(`${API_URL}/admin/tvs/${currentTvForEdit.id}/ip/${encodeURIComponent(values.ip_address)}`, {
            method: "PATCH",
            headers: { "Authorization": `Bearer ${authToken}` }
          })
        );
      }
      
      if (values.username !== currentTvForEdit.user_name) {
        updateRequests.push(
          fetch(`${API_URL}/admin/tvs/${currentTvForEdit.id}/username/${encodeURIComponent(values.username)}`, {
            method: "PATCH",
            headers: { "Authorization": `Bearer ${authToken}` }
          })
        );
      }
      
      if (values.password) {
        updateRequests.push(
          fetch(`${API_URL}/admin/tvs/${currentTvForEdit.id}/password/${encodeURIComponent(values.password)}`, {
            method: "PATCH",
            headers: { "Authorization": `Bearer ${authToken}` }
          })
        );
      }
      
      if (values.status !== undefined) {
        const statusValue = values.status ? "true" : "false";
        updateRequests.push(
          fetch(`${API_URL}/admin/tvs/${currentTvForEdit.id}/status/${statusValue}`, {
            method: "PATCH",
            headers: { "Authorization": `Bearer ${authToken}` }
          })
        );
      }
      
      if (updateRequests.length > 0) {
        const responses = await Promise.all(updateRequests);
        
        for (const response of responses) {
          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Ошибка при обновлении");
          }
        }
        
        message.success("Данные устройства успешно обновлены");
        fetchData(filterCat);
      } else {
        message.info("Нет изменений для сохранения");
      }
      
      setIsEditModalVisible(false);
      setCurrentTvForEdit(null);
    } catch (error) {
      console.error("Ошибка при обновлении устройства", error);
      message.error(`Ошибка при обновлении: ${error.message}`);
    } finally {
      setIsEditing(false);
    }
  };
  
  const handleAdminDelete = async (tvId) => {
    if (!authToken) return;
    
    try {
      const response = await fetch(`${API_URL}/admin/tvs/${tvId}/delete`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${authToken}`
        }
      });
      
      if (response.ok) {
        message.success("TV успешно удалена");
        fetchData(filterCat);
      } else {
        const error = await response.json();
        message.error("Ошибка удаления: " + error.detail);
      }
    } catch (error) {
      console.error("Ошибка при удалении TV", error);
      message.error("Ошибка при удалении TV");
    }
  };

  const fetchData = async (category = "all") => {
    setIsLoading(true);
    try {
      let url = `${API_URL}/tvs`;
      if (category !== "all") url += `?category=${category}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setTvs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Ошибка загрузки списка устройств", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error("Ошибка загрузки категорий", error);
    }
  };

  useEffect(() => { 
    fetchData(); 
    fetchCategories(); 
    const handleCategoriesUpdated = () => fetchCategories();
    window.addEventListener("categories-updated", handleCategoriesUpdated);
    return () => window.removeEventListener("categories-updated", handleCategoriesUpdated);
  }, []);

  useEffect(() => {
    const eventSources = {};
    tvs.forEach(tv => {
      if (tv.status === "false" || tv.status?.toLowerCase() === "processing") return;
      const eventSource = new EventSource(`${API_URL}/sse/tv_status/${tv.id}`);
      eventSource.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          setTvCurrentVideo(prev => ({ ...prev, [tv.id]: data }));
        } catch (err) {
          console.error("Ошибка парсинга SSE", err);
        }
      };
      eventSources[tv.id] = eventSource;
    });
    return () => {
      Object.values(eventSources).forEach(es => es.close());
    };
  }, [tvs]);

  useEffect(() => {
    const eventSource = new EventSource(`${API_URL}/sse/tvs_db_status`);
    eventSource.onmessage = (e) => {
      try {
        const statusData = JSON.parse(e.data);
        setTvs(prevTvs =>
          prevTvs.map(tv => {
            const newData = statusData.find(item => item.id === tv.id);
            return newData ? { ...tv, status: newData.status } : tv;
          })
        );
      } catch (err) {
        console.error("Ошибка парсинга SSE статусов из БД", err);
      }
    };
    return () => {
      eventSource.close();
    };
  }, [API_URL]);

  const handleFilterChange = (key) => {
    setFilterCat(key);
    fetchData(key);
  };

  const handleSync = async (tvId) => {
    setSyncingTvId(tvId);
    message.loading("Синхронизация началась...", 0);
    try {
      const response = await fetch(`${API_URL}/tvs/${tvId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      if (response.ok) {
        const result = await response.json();
        message.destroy();
        message.success(result.message);
      } else {
        const error = await response.json();
        message.destroy();
        message.error("Ошибка синхронизации: " + error.message);
      }
      fetchData();
    } catch (error) {
      console.error("Ошибка при синхронизации", error);
      message.destroy();
      message.error("Ошибка при синхронизации TV");
    } finally {
      setSyncingTvId(null);
    }
  };

  const handleRestart = async (tvId) => {
    if (restartingTvId) return;
    setRestartingTvId(tvId);
    message.loading("Перезапуск начался...", 0);
    try {
      const response = await fetch(`${API_URL}/tvs/${tvId}/restart`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (response.ok) {
        const result = await response.json();
        message.destroy();
        message.success(result.message);
      } else {
        const error = await response.json();
        message.destroy();
        message.error("Ошибка перезапуска: " + error.message);
      }
      fetchData();
    } catch (error) {
      console.error("Ошибка при перезапуске", error);
      message.destroy();
      message.error("Ошибка при перезапуске машины");
    } finally {
      setRestartingTvId(null);
    }
  };

  const handleDeleteSelected = async (tvId) => {
    const videosToDelete = Object.entries(deletionSelectedVideos)
      .filter(([_, selected]) => selected)
      .map(([video]) => video);
    if (videosToDelete.length === 0) {
      message.warning("Выберите ролики для удаления");
      return;
    }
    setIsDeleting(true);
    try {
      const payload = {
        tv_id: tvId,
        filenames: videosToDelete
      };
      const response = await fetch(`${API_URL}/videos`, {
        method: "DELETE",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        setTvs(prevTvs =>
          prevTvs.map(tv =>
            tv.id === tvId ? { ...tv, videos: tv.videos.filter(video => !videosToDelete.includes(video)) } : tv
          )
        );
        setDeletionModalVisible(false);
        setDeletionCurrentTv(null);
        message.success("Ролики успешно удалены");
        fetchData(filterCat);
      } else {
        message.error("Ошибка при удалении роликов");
      }
    } catch (error) {
      console.error("Ошибка при удалении роликов", error);
      message.error("Ошибка при удалении роликов");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCategoryChange = async (tvId, value) => {
    try {
      const payload = { category_id: value === "none" ? null : Number(value) };
      const response = await fetch(`${API_URL}/tvs/${tvId}/category`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        message.success("Категория обновлена");
        fetchData(filterCat);
      } else {
        const error = await response.json();
        message.error("Ошибка при обновлении: " + error.message);
      }
    } catch (error) {
      message.error("Ошибка при обновлении категории");
    }
  };

  const openReorderModal = (tv) => {
    setCurrentTvForReorder(tv);
    setReorderVideos([...tv.videos]);
    setReorderModalVisible(true);
  };

  const handleMoveUp = (index) => {
    if (index === 0) return;
    const updated = [...reorderVideos];
    [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
    setReorderVideos(updated);
  };

  const handleMoveDown = (index) => {
    if (index === reorderVideos.length - 1) return;
    const updated = [...reorderVideos];
    [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
    setReorderVideos(updated);
  };

  const handleSaveReorder = async () => {
    setIsSavingReorder(true);
    try {
      const response = await fetch(`${API_URL}/tvs/${currentTvForReorder.id}/videos`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videos: reorderVideos })
      });
      if (response.ok) {
        message.success("Порядок роликов обновлен");
        fetchData(filterCat);
      } else {
        const error = await response.json();
        message.error("Ошибка обновления порядка: " + error.message);
      }
    } catch (error) {
      message.error("Ошибка обновления порядка роликов");
    } finally {
      setIsSavingReorder(false);
      setReorderModalVisible(false);
      setCurrentTvForReorder(null);
      setReorderVideos([]);
    }
  };

  const handleCancelReorder = () => {
    setReorderModalVisible(false);
    setCurrentTvForReorder(null);
    setReorderVideos([]);
  };

  const openDeletionModal = (tv) => {
    if (!tv.videos || tv.videos.length === 0) {
      message.warning("Нет роликов для удаления");
      return;
    }
    setDeletionCurrentTv(tv);
    const initSelection = {};
    tv.videos.forEach(video => initSelection[video] = false);
    setDeletionSelectedVideos(initSelection);
    setDeletionModalVisible(true);
  };

  const toggleDeletionVideo = (video) => {
    setDeletionSelectedVideos(prev => ({
      ...prev,
      [video]: !prev[video]
    }));
  };

  const renderVideoList = (tv) => {
    const currentPage = currentPages[tv.id] || 1;
    const start = (currentPage - 1) * 10;
    const currentVideos = (tv.videos || []).slice(start, start + 10);
    return (
      <div style={{ width: "419.667px" }}>
        {currentVideos.map((video) => (
          <div 
            key={video}
            style={{ 
              display: "flex", 
              alignItems: "center", 
              padding: "4px", 
              border: "1px solid #ddd", 
              marginBottom: "4px", 
              background: "#fafafa" 
            }}
          >
            <span>{video}</span>
          </div>
        ))}
      </div>
    );
  };

  const fetchAvailableVideos = async (tv) => {
    try {
      const res = await fetch(`${API_URL}/videos`);
      const data = await res.json();
      const currentVideos = tv.videos || [];
      setAvailableVideos(data.videos.filter(video => !currentVideos.includes(video)));
    } catch (error) {
      console.error("Ошибка получения списка видео", error);
    }
  };

  const openAddModal = (tv) => {
    setCurrentTvForAdd(tv);
    fetchAvailableVideos(tv);
    setSelectedVideos([]);
    setAddModalVisible(true);
  };

  const handleAddSubmit = async () => {
    if (!selectedVideos.length) {
      message.warning("Выберите ролики для отправки");
      return;
    }
    
    setIsDeploying(true);
    const payload = {
      targets: [currentTvForAdd.id],
      videos: selectedVideos
    };
    
    try {
      const response = await fetch(`${API_URL}/deployments`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        message.success("Видео успешно отправлены на устройство");
        fetchData(filterCat);
        setAddModalVisible(false);
        setCurrentTvForAdd(null);
      } else {
        const err = await response.json();
        message.error("Ошибка: " + err.detail);
      }
    } catch (error) {
      message.error("Ошибка при отправке видео");
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "row", minHeight: "100vh" }}>
      <div style={{ width: "250px", padding: "10px", borderRight: "1px solid #f0f0f0", backgroundColor: "#fafafa" }}>
        <CategoryMenu onFilterChange={handleFilterChange} />
      </div>
      
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ position: "absolute", right: "10px", top: "10px", zIndex: 1000 }}>
          {authToken ? (
            <Button 
              type="primary" 
              icon={<LogoutOutlined />} 
              onClick={handleLogout}
            >
              Выйти
            </Button>
          ) : (
            <Button 
              type="primary" 
              icon={<LoginOutlined />} 
              onClick={() => setIsAuthModalVisible(true)}
            >
              Админ
            </Button>
          )}
        </div>
        <div style={{ flex: 1, padding: "10px" }}>
          {isLoading ? (
            <p>Загрузка данных...</p>
          ) : tvs.length === 0 ? (
            <p>Здесь ничего нет...</p>
          ) : (
            <div className="tv-cards-container">
              {tvs.map((tv) => (
                <div key={tv.id} className={`tv-card-wrapper ${!tv.status ? 'disabled' : ''}`} style={{ position: 'relative' }}>
                  {tv.status?.toLowerCase() === "processing" && (
                    <div className="processing-overlay" style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      backgroundColor: 'rgba(0,0,0,0.5)',
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 10,
                      fontSize: '1.2rem'
                    }}>
                      Устройство в обработке
                    </div>
                  )}
                  <Card
                    title={tv.name}
                    extra={
                      <div>
                        <Popconfirm
                          title="Вы уверены, что хотите синхронизировать это устройство?"
                          onConfirm={() => handleSync(tv.id)}
                          okText="Да"
                          cancelText="Нет"
                          disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                        >
                          <Button 
                            type="primary" 
                            icon={<SyncOutlined />} 
                            loading={syncingTvId === tv.id} 
                            style={{ margin: "0 8px" }}
                            disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                          >
                            Синхронизация
                          </Button>
                        </Popconfirm>
                        
                        <Popconfirm
                          title="Вы уверены, что хотите перезапустить это устройство?"
                          onConfirm={() => handleRestart(tv.id)}
                          okText="Да"
                          cancelText="Нет"
                          disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                        >
                          <Button 
                            danger
                            type="primary"
                            icon={<ReloadOutlined />} 
                            disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                            loading={restartingTvId === tv.id}
                          />
                        </Popconfirm>
                      </div>
                    }
                  >
                    <Meta description={`Видео: ${tv.videos ? tv.videos.length : 0} | Категория: ${tv.category || "Не назначена"}`} />

                    <div style={{ marginTop: 8 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span>
                            {tv.status === "false" 
                              ? <div style={{ color: "red", fontWeight: "bold" }}>Устройство сейчас недоступно</div>
                              : (tvCurrentVideo[tv.id]?.title || "Нет данных")}
                          </span>
                          {tv.status !== "false" && tvCurrentVideo[tv.id]?.position !== undefined && (
                            <Progress 
                              percent={Math.floor(tvCurrentVideo[tv.id].position * 100)} 
                              size="small" 
                              style={{ width: 100 }}
                            />
                          )}
                        </div>
                    </div>
                    <div style={{ margin: "10px 0" }}>
                      <Select 
                        style={{ width: 200 }}
                        placeholder="Выбрать категорию"
                        value={tv.category ? categories.find(c => c.name === tv.category)?.id : "none"}
                        onChange={(value) => handleCategoryChange(tv.id, value)}
                        disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                      >
                        <Select.Option value="none">...</Select.Option>
                        {categories.map(cat => (
                          <Select.Option key={cat.id} value={cat.id}>{cat.name}</Select.Option>
                        ))}
                      </Select>
                    </div>
                    
                    <div style={{ position: "relative", marginTop: "10px" }}>
                      <div style={{ marginRight: "150px" }}>
                        <Collapse 
                          defaultActiveKey={[]} 
                          ghost 
                          items={[
                            { 
                              key: '1', 
                              label: <div style={{ width: "100%", paddingRight: "150px" }}>Ролики</div>, 
                              children: renderVideoList(tv) 
                            }
                          ]}
                        />
                      </div>
                      <div style={{ position: "absolute", top: 0, right: 0, display: "flex", gap: "8px", alignItems: "center" }}>
                        <Button 
                          type="primary"
                          onClick={() => openReorderModal(tv)}
                          disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                        >
                          Изменить порядок
                        </Button>
                        <Button 
                          type="primary" 
                          icon={<PlusOutlined />} 
                          onClick={() => openAddModal(tv)}
                          disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                        />
                        
                        {authToken && (
                          <div style={{ display: "flex", gap: "8px" }}>
                            <Button 
                              type="primary" 
                              icon={<EditOutlined />}
                              onClick={() => {
                                setCurrentTvForEdit(tv);
                                setIsEditModalVisible(true);
                              }}
                              disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                            />
                            <Button 
                              type="primary" 
                              danger 
                              icon={<DeleteOutlined />} 
                              onClick={() => openDeletionModal(tv)}
                              disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                              style={{ background: "#ff4d4f", borderColor: "#ff4d4f" }}
                            />
                            <Popconfirm
                              title="Вы уверены, что хотите удалить это устройство?"
                              onConfirm={() => handleAdminDelete(tv.id)}
                              okText="Да"
                              cancelText="Нет"
                            >
                              <Button 
                                type="primary" 
                                danger 
                                icon={<DeleteOutlined />}
                                style={{ background: "#d9363e", borderColor: "#d9363e" }}
                              />
                            </Popconfirm>
                          </div>
                        )}
                        
                        {!authToken && (
                          <Button 
                            type="primary" 
                            danger 
                            icon={<DeleteOutlined />} 
                            onClick={() => openDeletionModal(tv)}
                            disabled={tv.status === "false" || tv.status?.toLowerCase() === "processing"}
                          />
                        )}
                      </div>
                    </div>
                  </Card>
                </div>
              ))}
            </div>
          )}
        </div>
      <Modal
        title="Выберите ролики для удаления"
        open={deletionModalVisible}
        onCancel={() => { setDeletionModalVisible(false); setDeletionCurrentTv(null); }}
        footer={[
          <Button key="cancel" onClick={() => { setDeletionModalVisible(false); setDeletionCurrentTv(null); }}>
            Отмена
          </Button>,
          <Button 
            key="delete" 
            type="primary" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteSelected(deletionCurrentTv.id)}
            loading={isDeleting}
          >
            Удалить выбранные
          </Button>
        ]}
      >
        <div>
          {deletionCurrentTv && deletionCurrentTv.videos.map(video => (
            <div 
              key={video}
              style={{ 
                display: "flex", 
                alignItems: "center", 
                padding: "4px", 
                border: "1px solid #ddd", 
                background: "#fafafa", 
                marginBottom: "4px" 
              }}
            >
              <Checkbox
                checked={deletionSelectedVideos[video] || false}
                onChange={() => toggleDeletionVideo(video)}
              />
              <span style={{ marginLeft: 8 }}>{video}</span>
            </div>
          ))}
        </div>
      </Modal>
      <Modal
        title="Изменить порядок видео"
        open={reorderModalVisible}
        onCancel={handleCancelReorder}
        footer={[
          <Button key="cancel" onClick={handleCancelReorder}>Отмена</Button>,
          <Button 
            key="save" 
            type="primary" 
            onClick={handleSaveReorder}
            disabled={
              isSavingReorder ||
              (!currentTvForReorder ||
              JSON.stringify(currentTvForReorder.videos) === JSON.stringify(reorderVideos))
            }
          >
            {isSavingReorder ? "Сохранение..." : "Сохранить"}
          </Button>
        ]}
      >
        {reorderVideos.map((video, index) => (
          <div key={video} style={{ display: "flex", alignItems: "center", marginBottom: "4px", padding: "4px", background: "#fafafa", border: "1px solid #ddd" }}>
            <span style={{ flex: 1 }}>{video}</span>
            <Button size="small" onClick={() => handleMoveUp(index)} disabled={index === 0}>↑</Button>
            <Button size="small" onClick={() => handleMoveDown(index)} disabled={index === reorderVideos.length - 1}>↓</Button>
          </div>
        ))}
      </Modal>
      <Modal
        title="Выберите ролики для добавления"
        open={addModalVisible}
        onCancel={() => setAddModalVisible(false)}
        onOk={handleAddSubmit}
        okText={isDeploying ? "Отправка..." : "Отправить"}
        cancelText="Отмена"
        okButtonProps={{ 
          disabled: isDeploying || !selectedVideos.length 
        }}
      >
        {availableVideos.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            Все доступные ролики уже загружены на это устройство
          </div>
        ) : (
          <List
            dataSource={availableVideos}
            renderItem={(video) => (
              <List.Item>
                <Checkbox
                  checked={selectedVideos.includes(video)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedVideos([...selectedVideos, video]);
                    } else {
                      setSelectedVideos(selectedVideos.filter((v) => v !== video));
                    }
                  }}
                  disabled={isDeploying}
                >
                  {video}
                </Checkbox>
              </List.Item>
            )}
          />
        )}
      </Modal>
      
      <AuthModal
        visible={isAuthModalVisible}
        onCancel={() => setIsAuthModalVisible(false)}
        onLogin={handleLogin}
      />
      
      <EditTvModal
        visible={isEditModalVisible}
        onCancel={() => {
          setIsEditModalVisible(false);
          setCurrentTvForEdit(null);
        }}
        onSave={handleEditSave}
        tvData={currentTvForEdit}
        loading={isEditing}
      />
      </div>
    </div>
  );
}

export default TvCards;

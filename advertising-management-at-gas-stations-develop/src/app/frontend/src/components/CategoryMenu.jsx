import React, { useState, useEffect, useRef } from "react";
import { Menu, Input, Button, message, Modal } from "antd";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";

function CategoryMenu({ onFilterChange }) {
  const API_URL = import.meta.env.VITE_API_URL;
  const [selectedKey, setSelectedKey] = useState("all");
  const [hoveredId, setHoveredId] = useState(null);
  const [categories, setCategories] = useState([]);
  const [newCat, setNewCat] = useState("");
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [categoryToDeleteId, setCategoryToDeleteId] = useState(null);
  const [isAddingCategory, setIsAddingCategory] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [startX, setStartX] = useState(0);
  const [startWidth, setStartWidth] = useState(200);
  const menuRef = useRef(null);

  const handleMouseDown = (e) => {
    setIsResizing(true);
    setStartX(e.clientX);
    setStartWidth(menuRef.current.offsetWidth);
    document.body.style.userSelect = 'none';
  };

  const handleMouseMove = (e) => {
    if (!isResizing) return;
    const newWidth = startWidth + (e.clientX - startX);
    const clampedWidth = Math.max(150, Math.min(newWidth, 400));
    menuRef.current.style.width = `${clampedWidth}px`;
  };

  const handleMouseUp = () => {
    setIsResizing(false);
    document.body.style.userSelect = '';
  };

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error("Ошибка загрузки категорий", error);
    }
  };

  useEffect(() => { fetchCategories(); }, []);

  const handleAdd = async () => {
    if (!newCat.trim()) return;
    setIsAddingCategory(true);
    try {
      const response = await fetch(`${API_URL}/categories`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newCat })
      });
      if (response.ok) {
        message.success("Категория добавлена");
        setNewCat("");
        setIsModalVisible(false);
        fetchCategories();
      } else {
        const errorData = await response.json();
        message.error(`Ошибка при добавлении: ${errorData.detail}`);
      }
    } catch (error) {
      message.error(`Ошибка при добавлении: ${error.message}`);
    } finally {
      setIsAddingCategory(false);
    }
  };

  const confirmDeleteCategory = (catId, e) => {
    e.stopPropagation();
    setCategoryToDeleteId(catId);
    setDeleteModalVisible(true);
  };

  const handleDeleteCategoryConfirmed = async () => {
    try {
      const response = await fetch(`${API_URL}/categories/${categoryToDeleteId}`, {
        method: "DELETE"
      });
      if (response.ok) {
        message.success("Категория удалена");
        if (selectedKey === String(categoryToDeleteId)) setSelectedKey("all");
        fetchCategories();
      } else {
        message.error("Ошибка при удалении категории");
      }
    } catch (error) {
      message.error("Ошибка при удалении категории");
    } finally {
      setDeleteModalVisible(false);
      setCategoryToDeleteId(null);
    }
  };

  const menuItems = [
    { key: "all", label: "Все устройства" },
    { key: "unassigned", label: "Без категории" },
    ...categories.map(cat => ({
      key: String(cat.id),
      label: (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {cat.name}
          </span>
          <DeleteOutlined
            onClick={(e) => confirmDeleteCategory(cat.id, e)}
            onMouseEnter={() => setHoveredId(cat.id)}
            onMouseLeave={() => setHoveredId(null)}
            style={{
              color: hoveredId === cat.id ? "#d32f2f" : "#ff4d4f",
              transform: hoveredId === cat.id ? "scale(1.2)" : "scale(1)",
              transition: "transform 0.2s ease, color 0.2s ease",
              cursor: "pointer"
            }}
          />
        </div>
      )
    }))
  ];

  const handleClick = ({ key }) => {
    setSelectedKey(key);
    onFilterChange(key);
    fetchCategories();
  };

  return (
    <div ref={menuRef}
    style={{ width: 200, minWidth: 150, maxWidth: 400, padding: "10px", borderRight: "1px solid #f0f0f0", position: "relative", overflow: "hidden" }}>
      <Menu
        onClick={handleClick}
        selectedKeys={[selectedKey]}
        mode="inline"
        items={menuItems}
      />
      <div
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          bottom: 0,
          width: '6px',
          cursor: 'col-resize',
          backgroundColor: isResizing ? '#1890ff' : 'transparent',
          zIndex: 1000,
          transition: 'background-color 0.2s'
        }}
        onMouseDown={handleMouseDown}
      />
      <div style={{ marginTop: 10 }}>
        <Button onClick={() => setIsModalVisible(true)} block>
          <PlusOutlined />
        </Button>
        <Modal
          open={isModalVisible}
          title="Новая категория"
          onOk={handleAdd}
          onCancel={() => setIsModalVisible(false)}
          okText="Добавить"
          cancelText="Отмена"
          confirmLoading={isAddingCategory}
        >
          <Input 
            placeholder="Название категории (до 16 символов)" 
            value={newCat} 
            onChange={e => setNewCat(e.target.value)}
            maxLength={16}
          />
        </Modal>
        <Modal
          open={deleteModalVisible}
          title="Подтверждение удаления"
          onOk={handleDeleteCategoryConfirmed}
          onCancel={() => setDeleteModalVisible(false)}
          okText="Удалить"
          cancelText="Отмена"
        >
          <p>Вы уверены, что хотите удалить эту категорию?</p>
        </Modal>
      </div>
    </div>
  );
}

export default CategoryMenu;

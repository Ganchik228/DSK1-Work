import React, { useState, useEffect } from "react";
import { Modal, Form, Input, Button, message, Checkbox } from "antd";

const EditTvModal = ({ 
  visible, 
  onCancel, 
  onSave, 
  tvData,
  loading 
}) => {
  const API_URL = import.meta.env.VITE_API_URL;
  const [form] = Form.useForm();
  const [tvDetails, setTvDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    const fetchTvDetails = async () => {
      if (!tvData || !visible) return;
      
      setLoadingDetails(true);
      try {
        const response = await fetch(`${API_URL}/admin/tvs/${tvData.id}/data`, {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setTvDetails(data);
          form.setFieldsValue({
            ip_address: data.address || "",
            machine_name: data.machine_name || "",
            password: "",
            username: data.user_name || "",
            status: data.status === "true"
          });
        } else {
          const error = await response.json();
          message.error("Ошибка загрузки данных: " + error.detail);
        }
      } catch (error) {
        console.error("Ошибка при загрузке данных устройства", error);
        message.error("Ошибка при загрузке данных устройства");
      } finally {
        setLoadingDetails(false);
      }
    };
    
    fetchTvDetails();
  }, [tvData, visible, API_URL, form]);

  useEffect(() => {
    if (!visible) {
      setTvDetails(null);
    }
  }, [visible]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      onSave(values);
    } catch (error) {
      console.error("Ошибка валидации формы", error);
    }
  };

  return (
    <Modal
      title="Редактирование устройства"
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Отмена
        </Button>,
        <Button 
          key="save" 
          type="primary" 
          onClick={handleSubmit}
          loading={loading || loadingDetails}
        >
          Сохранить
        </Button>
      ]}
      width={600}
    >
      {loadingDetails ? (
        <p>Загрузка данных устройства...</p>
      ) : (
        <Form form={form} layout="vertical">
          <Form.Item
            name="machine_name"
            label="Название устройства"
            rules={[{ required: true, message: 'Введите название устройства' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="ip_address"
            label="IP-адрес"
            rules={[{ required: true, message: 'Введите IP-адрес' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="username"
            label="Имя пользователя"
            rules={[{ required: true, message: 'Введите имя пользователя' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="password"
            label="Пароль"
          >
            <Input.Password placeholder="Оставьте пустым, чтобы не менять" />
          </Form.Item>
          
          <Form.Item
            name="status"
            label="Статус"
            valuePropName="checked"
          >
            <Checkbox>Устройство активно</Checkbox>
          </Form.Item>
        </Form>
      )}
    </Modal>
  );
};

export default EditTvModal;

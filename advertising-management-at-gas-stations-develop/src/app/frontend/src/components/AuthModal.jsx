import React, { useState } from "react";
import { Modal, Form, Input, Button, message } from "antd";

const AuthModal = ({ visible, onCancel, onLogin }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await onLogin(values);
      form.resetFields();
    } catch (error) {
      message.error("Ошибка авторизации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="Авторизация"
      open={visible}
      onCancel={onCancel}
      footer={null}
    >
      <Form
        form={form}
        onFinish={handleSubmit}
        layout="vertical"
      >
        <Form.Item
          label="Логин"
          name="username"
          rules={[{ required: true, message: 'Введите логин' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="Пароль"
          name="password"
          rules={[{ required: true, message: 'Введите пароль' }]}
        >
          <Input.Password />
        </Form.Item>
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit"
            loading={loading}
          >
            Войти
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default AuthModal;

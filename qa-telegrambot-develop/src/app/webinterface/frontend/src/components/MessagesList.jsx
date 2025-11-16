import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config.js';

const MessagesList = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/message/all`);
      if (!response.ok) {
        throw new Error('Ошибка загрузки сообщений');
      }
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedMessages = [...messages].sort((a, b) => {
    let aValue, bValue;

    switch (sortField) {
      case 'phone_number':
        aValue = a.phone_number;
        bValue = b.phone_number;
        break;
      case 'request':
        aValue = a.request;
        bValue = b.request;
        break;
      case 'response':
        aValue = a.response;
        bValue = b.response;
        break;
      case 'date':
        aValue = new Date(a.date);
        bValue = new Date(b.date);
        break;
      default:
        return 0;
    }

    if (aValue < bValue) {
      return sortDirection === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortDirection === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const handleCheckboxChange = async (messageId, currentChecked) => {
    try {
      const response = await fetch(`${API_BASE_URL}/message/status/${messageId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка изменения статуса');
      }

      setMessages(prevMessages =>
        prevMessages.map(msg =>
          msg.id === messageId
            ? { ...msg, checked: !currentChecked }
            : msg
        )
      );
    } catch (err) {
      console.error('Ошибка при изменении статуса:', err);
      alert('Не удалось изменить статус сообщения');
    }
  };

  const getSortIcon = (field) => {
    if (sortField !== field) return '↕️';
    return sortDirection === 'asc' ? '⬆️' : '⬇️';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Загрузка сообщений...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Ошибка</h2>
        </div>
        <div className="error-message">
          {error}
          <button className="btn btn-primary" onClick={fetchMessages} style={{ marginLeft: '10px' }}>
            Повторить
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="panel">
        <div className="panel-header">
          <h1 className="panel-title">Все сообщения ({messages.length})</h1>
          <div style={{ display: 'flex', gap: '10px' }}>
            <Link to="/contexts" className="btn btn-primary">
              Управление темами
            </Link>
            <button className="btn btn-primary" onClick={fetchMessages}>
              Обновить
            </button>
          </div>
        </div>

        {messages.length === 0 ? (
          <div className="no-messages">
            Сообщения не найдены
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th 
                  className="sortable-header" 
                  onClick={() => handleSort('phone_number')}
                  title="Сортировать по номеру телефона"
                >
                  Номер телефона {getSortIcon('phone_number')}
                </th>
                <th 
                  className="sortable-header" 
                  onClick={() => handleSort('request')}
                  title="Сортировать по запросу"
                >
                  Запрос {getSortIcon('request')}
                </th>
                <th 
                  className="sortable-header" 
                  onClick={() => handleSort('response')}
                  title="Сортировать по ответу"
                >
                  Ответ {getSortIcon('response')}
                </th>
                <th 
                  className="sortable-header" 
                  onClick={() => handleSort('date')}
                  title="Сортировать по дате"
                >
                  Дата {getSortIcon('date')}
                </th>
                <th>
                  Проверено
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedMessages.map((message) => (
                <tr key={message.id} className={message.checked ? 'checked-row' : ''}>
                  <td className="phone-cell">
                    {message.phone_number || 'Не указан'}
                  </td>
                  <td className="message-cell request-cell">
                    <div className="message-content">
                      {message.request}
                    </div>
                  </td>
                  <td className="message-cell response-cell">
                    <div className="message-content">
                      {message.response}
                    </div>
                  </td>
                  <td className="date-cell">
                    {formatDate(message.date)}
                  </td>
                  <td>
                    <input
                      type="checkbox"
                      checked={message.checked || false}
                      onChange={() => handleCheckboxChange(message.id, message.checked)}
                      className="message-checkbox"
                      title={message.checked ? 'Отметить как непроверенное' : 'Отметить как проверенное'}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default MessagesList;

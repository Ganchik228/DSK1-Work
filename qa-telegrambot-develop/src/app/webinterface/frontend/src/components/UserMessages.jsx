import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { API_BASE_URL } from '../config'

export default function UserMessages() {
  const { id: userId } = useParams()
  const [messages, setMessages] = useState([])
  const [messageIndex, setMessageIndex] = useState(0)
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/user/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error('Ошибка запроса пользователя')
        return res.json()
      })
      .then(data => {
        if (data.status === 'success') {
          setUserInfo({id: data.user.id, name: data.user.name})
        } else {
          setUserInfo({id: userId, name: 'Неизвестный пользователь'})
        }
      })
      .catch(() => {
        setUserInfo({id: userId, name: 'Ошибка загрузки'})
      })

    fetch(`${API_BASE_URL}/message/user/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error('Ошибка запроса сообщений')
        return res.json()
      })
      .then(data => {
        setMessages(data.messages || [])
        setMessageIndex(0)
      })
      .catch(() => {
        setMessages([])
      })
  }, [userId])

  const handlePrevMessage = () => {
    if (messageIndex > 0) {
      setMessageIndex(messageIndex - 1)
    }
  }

  const handleNextMessage = () => {
    if (messageIndex < messages.length - 1) {
      setMessageIndex(messageIndex + 1)
    }
  }

  return (
    <div className="container">
      <Link to="/" className="back-link">← Назад к списку пользователей</Link>
      
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">
            Сообщения пользователя: {userInfo?.name || 'Загрузка...'} (ID: {userId})
          </h2>
        </div>

        {messages.length > 0 ? (
          <>
            <div className="message-navigation">
              <button 
                onClick={handlePrevMessage} 
                disabled={messageIndex === 0}
                className="btn"
              >
                Назад
              </button>
              <span className="message-counter">
                Сообщение {messageIndex + 1} из {messages.length}
              </span>
              <button 
                onClick={handleNextMessage} 
                disabled={messageIndex === messages.length - 1}
                className="btn"
              >
                Вперед
              </button>
            </div>

            <div className="message-card">
              <div className="message-meta">Отправлено:</div>
              <div className="message-content">
                {messages[messageIndex]?.request}
              </div>
              
              <div className="message-meta" style={{marginTop: '15px'}}>Получено:</div>
              <div className="message-content">
                {messages[messageIndex]?.response}
              </div>
            </div>
          </>
        ) : (
          <p>Нет сообщений для отображения</p>
        )}
      </div>
    </div>
  )
}

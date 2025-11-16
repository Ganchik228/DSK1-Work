import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { API_BASE_URL } from '../config'

export default function ContextsList() {
  const [contexts, setContexts] = useState([])
  const [newContext, setNewContext] = useState({name: '', data: ''})

  useEffect(() => {
    fetch(`${API_BASE_URL}/context/all`)
      .then(res => res.json())
      .then(data => setContexts(data.contexts))
  }, [])

  const handleAddContext = () => {
    fetch(`${API_BASE_URL}/context/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: newContext.name,
        data: newContext.data
      })
    })
    .then(async res => {
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Ошибка сервера')
      }
      return data
    })
    .then(data => {
      setContexts([...contexts, data.context])
      setNewContext({name: '', data: ''})
    })
    .catch(error => {
      console.error('Error:', error)
      alert(error.message)
    })
  }

  return (
    <div className="container">
      <Link to="/" className="back-link">← Назад к списку пользователей</Link>
      
      <div className="panel">
        <div className="panel-header">
          <h1 className="panel-title">Темы</h1>
        </div>

        <div className="form-panel">
          <h3>Добавить новую тему</h3>
          <div className="form-group">
            <input
              className="form-input"
              value={newContext.name}
              onChange={e => setNewContext({...newContext, name: e.target.value})}
              placeholder="Название темы"
            />
          </div>
          <div className="form-group">
            <textarea
              className="form-textarea"
              value={newContext.data}
              onChange={e => setNewContext({...newContext, data: e.target.value})}
              placeholder="Содержание"
              rows="5"
            />
          </div>
          <button 
            onClick={handleAddContext}
            className="btn btn-primary"
            disabled={!newContext.name || !newContext.data}
          >
            Создать тему
          </button>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {contexts.map(context => (
              <tr key={context.id}>
                <td>{context.id}</td>
                <td>{context.name}</td>
                <td>
                  <Link 
                    to={`/contexts/${context.id}`}
                    className="nav-link"
                  >
                    Редактировать
                  </Link>
                  <button
                    onClick={() => {
                      if (window.confirm('Вы уверены, что хотите удалить тему?')) {
                        fetch(`${API_BASE_URL}/context/${context.id}`, {
                          method: 'DELETE'
                        })
                        .then(res => res.json())
                        .then(data => {
                          if (data.status === 'success') {
                            setContexts(contexts.filter(c => c.id !== context.id))
                          }
                        })
                      }
                    }}
                    className="btn btn-danger"
                    style={{marginLeft: '10px'}}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { API_BASE_URL } from '../config'

export default function EditContext() {
  const { id } = useParams()
  const [context, setContext] = useState({name: '', data: ''})

  useEffect(() => {
    fetch(`${API_BASE_URL}/context/${id}`)
      .then(res => res.json())
      .then(data => setContext(data.context_data))
  }, [id])

  const handleUpdate = () => {
    fetch(`${API_BASE_URL}/context/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        id: id,
        name: context.contextName,
        data: context.contextData
      })
    })
    .then(res => res.json())
    .then(data => {
      alert('Контекст обновлен')
    })
  }

  return (
    <div className="container">
      <Link to="/contexts" className="back-link">← Назад к списку тем</Link>
      
      <div className="panel">
        <div className="panel-header">
          <h1 className="panel-title">Редактирование темы</h1>
        </div>

        <div className="form-panel">
          <div className="form-group">
            <label>Название темы</label>
            <input
              className="form-input"
              value={context.contextName || ''}
              onChange={e => setContext({...context, contextName: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>Содержание темы</label>
            <textarea
              className="form-textarea"
              value={context.contextData || ''}
              onChange={e => setContext({...context, contextData: e.target.value})}
              rows="10"
            />
          </div>
          <button 
            onClick={handleUpdate}
            className="btn btn-primary"
          >
            Сохранить изменения
          </button>
        </div>
      </div>
    </div>
  )
}

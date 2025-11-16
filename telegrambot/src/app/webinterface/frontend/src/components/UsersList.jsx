import { useEffect, useState } from 'react'
import '../App.css'
import { apiGet } from '../utils/apiClient'
import { handleApiError } from '../utils/errorHandler'

function UsersList() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setError('')
        const response = await apiGet('/users')
        const data = await response.json()
        setUsers(data)
      } catch (error) {
        handleApiError(error)
        setError('Не удалось загрузить список пользователей')
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [])

  if (loading) return <div className="panel">Загрузка пользователей...</div>
  
  if (error) {
    return (
      <div className="panel">
        <div style={{ color: 'red', textAlign: 'center' }}>
          {error}
          <br />
          <button 
            className="btn btn-primary" 
            onClick={() => window.location.reload()}
            style={{ marginTop: '10px' }}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Пользователи</h2>
      </div>
      
      <table className="table">
        <thead>
          <tr>
            <th>Chat ID</th>
            <th>Имя</th>
            <th>Телефон</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.chat_id}</td>
              <td>{user.name}</td>
              <td>{user.phone}</td>
              <td>
                <a href={`/users/${user.id}/reviews`} className="link">
                  Просмотреть отзывы
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default UsersList

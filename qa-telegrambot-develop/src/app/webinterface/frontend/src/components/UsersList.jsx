import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { API_BASE_URL } from '../config'

export default function UsersList() {
  const [users, setUsers] = useState([])

  useEffect(() => {
    fetch(`${API_BASE_URL}/user/all`)
      .then(res => res.json())
      .then(data => setUsers(data.users))
  }, [])

  return (
    <div className="container">
      <div className="panel">
        <div className="panel-header">
          <h1 className="panel-title">Пользователи</h1>
          <Link to="/contexts" className="btn btn-primary">
            Управление темами
          </Link>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>
                  <Link 
                    to={`/users/${user.id}/messages`} 
                    className="nav-link"
                  >
                    Просмотреть сообщения
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

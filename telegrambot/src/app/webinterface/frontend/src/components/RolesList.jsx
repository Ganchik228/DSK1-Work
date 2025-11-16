import { useEffect, useState } from 'react'
import '../App.css'
import { apiGet, apiPost, apiDelete } from '../utils/apiClient'

function RolesList() {
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)
  const [newRoleName, setNewRoleName] = useState('')

  useEffect(() => {
    fetchRoles()
  }, [])

  const fetchRoles = async () => {
    try {
      const response = await apiGet('/roles')
      const data = await response.json()
      setRoles(data)
    } catch (error) {
      console.error('Error fetching roles:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddRole = async () => {
    if (!newRoleName.trim()) return

    try {
      const response = await apiPost('/roles', { name: newRoleName })
      
      if (response.ok) {
        setNewRoleName('')
        fetchRoles()
      }
    } catch (error) {
      console.error('Error adding role:', error)
    }
  }

  const handleDeleteRole = async (id) => {
    try {
      const response = await apiDelete(`/roles/${id}`)
      
      if (response.ok) {
        fetchRoles()
      }
    } catch (error) {
      console.error('Error deleting role:', error)
    }
  }

  if (loading) return <div className="panel">Загрузка ролей...</div>

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Управление ролями</h2>
      </div>

      <div className="form-panel">
        <div className="form-group">
          <input
            type="text"
            className="form-input"
            value={newRoleName}
            onChange={(e) => setNewRoleName(e.target.value)}
            placeholder="Название новой роли"
          />
        </div>
        <button className="btn btn-primary" onClick={handleAddRole}>
          Добавить роль
        </button>
      </div>
      
      <table className="table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {roles.map(role => (
            <tr key={role.id}>
              <td>{role.name}</td>
              <td>
                <button 
                  className="btn btn-primary"
                  onClick={() => handleDeleteRole(role.id)}
                >
                  Удалить
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RolesList

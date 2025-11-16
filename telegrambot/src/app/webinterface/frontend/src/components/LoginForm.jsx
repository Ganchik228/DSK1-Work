import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../App.css'
import { API_BASE_URL } from '../config'


function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!username || !password) {
      setError('Введите логин и пароль')
      return
    }

    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    try {
      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      })

      if (!response.ok) {
        const data = await response.json()
        setError(data.detail || 'Ошибка входа')
        return
      }

      const data = await response.json()
      const token = data.access_token
      localStorage.setItem('access_token', token)

      onLogin()
      navigate('/reviews')
    } catch (e) {
      setError('Ошибка сети')
    }
  }

  return (
    <div className="panel" style={{ maxWidth: 400, margin: '60px auto' }}>
      <h2 className="panel-title" style={{ textAlign: 'center' }}>Вход</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            className="form-input"
            type="text"
            placeholder="Логин"
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoFocus
          />
        </div>
        <div className="form-group">
          <input
            className="form-input"
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </div>
        {error && <div style={{ color: 'red', marginBottom: 10 }}>{error}</div>}
        <button className="btn btn-primary" type="submit" style={{ width: '100%' }}>
          Войти
        </button>
      </form>
    </div>
  )
}

export default LoginForm

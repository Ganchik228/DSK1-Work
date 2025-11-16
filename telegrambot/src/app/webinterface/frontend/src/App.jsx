import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'
import { apiGet } from './utils/apiClient'

import UsersList from './components/UsersList'
import ReviewsList from './components/ReviewsList'
import RolesList from './components/RolesList'
import LoginForm from './components/LoginForm'
import PrivateRoute from './components/PrivateRoute'

function AppWrapper() {
  const [isAuth, setIsAuth] = useState(() => {
    return !!localStorage.getItem('access_token')
  })

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    setIsAuth(!!token)
    
    // Проверим валидность токена при запуске
    if (token) {
      checkTokenValidity()
    }
  }, [])

  const checkTokenValidity = async () => {
    try {
      // Попробуем сделать запрос к защищенному эндпоинту
      await apiGet('/roles')
    } catch (error) {
      // Если токен недействителен, apiClient автоматически перенаправит на /login
      setIsAuth(false)
    }
  }

  const handleLogin = () => setIsAuth(true)

  return (
    <Router>
      <App isAuth={isAuth} setIsAuth={setIsAuth} onLogin={handleLogin} />
    </Router>
  )
}

function App({ isAuth, setIsAuth, onLogin }) {
  const navigate = useNavigate()

  // Слушаем изменения в localStorage для автоматического обновления состояния
  useEffect(() => {
    const handleStorageChange = () => {
      const token = localStorage.getItem('access_token')
      setIsAuth(!!token)
      
      // Если токен удален, перенаправляем на логин
      if (!token && window.location.pathname !== '/login') {
        navigate('/login')
      }
    }

    // Слушаем события изменения localStorage
    window.addEventListener('storage', handleStorageChange)
    
    // Также проверяем при каждом фокусе на окно
    window.addEventListener('focus', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('focus', handleStorageChange)
    }
  }, [navigate, setIsAuth])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsAuth(false)
    navigate('/login')
  }

  return (
    <div className="app-container">
      {isAuth && (
        <nav className="navigation">
          <div className="nav-links">
            <a href="/reviews" className="nav-link">Отзывы</a>
            <a href="/roles" className="nav-link">Роли</a>
          </div>
          <button onClick={handleLogout} className="btn btn-secondary logout-btn">Выйти</button>
        </nav>
      )}

      <Routes>
        <Route path="/login" element={<LoginForm onLogin={onLogin} />} />

        <Route path="/reviews" element={
          <PrivateRoute>
            <ReviewsList />
          </PrivateRoute>
        } />
        <Route path="/roles" element={
          <PrivateRoute>
            <RolesList />
          </PrivateRoute>
        } />
        <Route path="/users" element={
          <PrivateRoute>
            <UsersList />
          </PrivateRoute>
        } />

        <Route path="*" element={
          isAuth ? <Navigate to="/reviews" /> : <Navigate to="/login" />
        } />
      </Routes>
    </div>
  )
}

export default AppWrapper

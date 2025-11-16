import { Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { validateToken } from '../utils/apiClient'

function PrivateRoute({ children }) {
  const [isValidating, setIsValidating] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        setIsAuthenticated(false)
        setIsValidating(false)
        return
      }
      
      try {
        const isValid = await validateToken()
        setIsAuthenticated(isValid)
      } catch (error) {
        setIsAuthenticated(false)
      } finally {
        setIsValidating(false)
      }
    }
    
    checkAuth()
  }, [])
  
  if (isValidating) {
    return <div className="panel">Проверка авторизации...</div>
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default PrivateRoute

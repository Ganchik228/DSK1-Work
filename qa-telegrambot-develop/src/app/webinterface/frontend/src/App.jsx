import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import MessagesList from './components/MessagesList'
import ContextsList from './components/ContextsList'
import EditContext from './components/EditContext'
import UserMessages from './components/UserMessages'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MessagesList />} />
        <Route path="/contexts" element={<ContextsList />} />
        <Route path="/contexts/:id" element={<EditContext />} />
        <Route path="/users/:id/messages" element={<UserMessages />} />
      </Routes>
    </Router>
  )
}

export default App

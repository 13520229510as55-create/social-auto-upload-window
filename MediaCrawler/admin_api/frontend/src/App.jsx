import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import MainLayout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ConfigPage from './pages/Config'
import TasksPage from './pages/Tasks'
import DataPage from './pages/Data'
import LoginPage from './pages/Login'

const { Content } = Layout

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="config/:platform?" element={<ConfigPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="data/:platform?" element={<DataPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App


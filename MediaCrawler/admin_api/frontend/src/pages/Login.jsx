import React from 'react'
import { Card } from 'antd'
import { useNavigate } from 'react-router-dom'

const LoginPage = () => {
  const navigate = useNavigate()

  // 简化登录页面，实际可以添加登录表单
  React.useEffect(() => {
    // 如果已登录，跳转到首页
    // 这里可以检查token等
    setTimeout(() => {
      navigate('/dashboard')
    }, 1000)
  }, [navigate])

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400, textAlign: 'center' }}>
        <h2>MediaCrawler 管理后台</h2>
        <p>正在跳转...</p>
      </Card>
    </div>
  )
}

export default LoginPage


import React from 'react'
import { Layout, Menu, Avatar } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  SettingOutlined,
  DatabaseOutlined,
  PlayCircleOutlined
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout

const MainLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '总览',
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: '配置管理',
    },
    {
      key: '/tasks',
      icon: <PlayCircleOutlined />,
      label: '任务管理',
    },
    {
      key: '/data',
      icon: <DatabaseOutlined />,
      label: '数据列表',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  const selectedKey = location.pathname.startsWith('/config') ? '/config' :
    location.pathname.startsWith('/data') ? '/data' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#001529', 
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ color: '#fff', fontSize: '20px', fontWeight: 'bold' }}>
          MediaCrawler 管理后台
        </div>
        <Avatar style={{ backgroundColor: '#1890ff' }}>Admin</Avatar>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              background: '#fff',
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default MainLayout


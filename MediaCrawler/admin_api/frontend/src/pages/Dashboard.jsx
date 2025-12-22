import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag } from 'antd'
import { 
  DatabaseOutlined, 
  PlayCircleOutlined, 
  CheckCircleOutlined,
  ClockCircleOutlined 
} from '@ant-design/icons'
import api from '../utils/api'

const Dashboard = () => {
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    // 每30秒刷新一次
    const interval = setInterval(loadStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await api.get('/dashboard/stats')
      setStats(data)
    } catch (error) {
      console.error('加载统计数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const platformNames = {
    xhs: '小红书',
    dy: '抖音',
    ks: '快手',
    bili: 'B站',
    wb: '微博',
    tieba: '百度贴吧',
    zhihu: '知乎',
    juejin: '掘金',
    medium: 'Medium'
  }

  const platformStats = Object.values(stats.stats || {}).map(stat => ({
    key: stat.name,
    platform: platformNames[stat.name] || stat.name,
    dataCount: stat.data_count,
    lastCrawlTime: stat.last_crawl_time || '暂无'
  }))

  const columns = [
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
    },
    {
      title: '数据量',
      dataIndex: 'dataCount',
      key: 'dataCount',
      render: (count) => <Tag color="blue">{count}</Tag>
    },
    {
      title: '最后爬取时间',
      dataIndex: 'lastCrawlTime',
      key: 'lastCrawlTime',
    },
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>总览</h2>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.total_tasks || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中任务"
              value={stats.running_tasks || 0}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成任务"
              value={(stats.total_tasks || 0) - (stats.running_tasks || 0)}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平台数量"
              value={Object.keys(stats.stats || {}).length}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="平台数据统计" loading={loading}>
        <Table
          columns={columns}
          dataSource={platformStats}
          pagination={false}
        />
      </Card>
    </div>
  )
}

export default Dashboard


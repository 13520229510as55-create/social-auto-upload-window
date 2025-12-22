import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Tag, Space, message, Input, Select, Avatar, List, Tooltip, Switch } from 'antd'
import { ReloadOutlined, LinkOutlined, HistoryOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

const { Option } = Select

/**
 * 公众号数据列表组件
 * 显示公众号订阅源列表和文章列表
 */
const WechatDataList = () => {
  const [feeds, setFeeds] = useState([])
  const [articles, setArticles] = useState([])
  const [selectedFeedId, setSelectedFeedId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [gettingHistory, setGettingHistory] = useState(false)
  const [historyProgress, setHistoryProgress] = useState({ id: '', page: 1 })
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })

  useEffect(() => {
    loadFeeds()
  }, [])

  useEffect(() => {
    if (selectedFeedId !== null) {
      loadArticles()
    }
  }, [selectedFeedId, pagination.current, pagination.pageSize])

  // 轮询获取历史文章进度
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const progress = await api.get('/wechat/feeds/history/progress')
        setHistoryProgress(progress)
      } catch (error) {
        // 忽略错误
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const loadFeeds = async () => {
    try {
      setLoading(true)
      const data = await api.get('/wechat/feeds')
      setFeeds(data.feeds || [])
    } catch (error) {
      message.error('加载订阅源列表失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadArticles = async () => {
    try {
      setLoading(true)
      const params = {
        mp_id: selectedFeedId || undefined,
        limit: pagination.pageSize,
        offset: (pagination.current - 1) * pagination.pageSize
      }
      const data = await api.get('/wechat/articles', { params })
      setArticles(data.articles || [])
      setPagination(prev => ({ ...prev, total: data.total || 0 }))
    } catch (error) {
      message.error('加载文章列表失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRefreshFeed = async (feedId) => {
    try {
      setRefreshing(true)
      await api.post(`/wechat/feeds/${feedId}/refresh`)
      message.success('刷新成功')
      await loadFeeds()
      if (feedId === selectedFeedId) {
        await loadArticles()
      }
    } catch (error) {
      message.error('刷新失败: ' + error.message)
    } finally {
      setRefreshing(false)
    }
  }

  const handleUpdateFeedStatus = async (feedId, status) => {
    try {
      await api.put(`/wechat/feeds/${feedId}/status`, { status })
      message.success('状态更新成功')
      await loadFeeds()
    } catch (error) {
      message.error('更新状态失败: ' + error.message)
    }
  }

  const handleDeleteFeed = async (feedId) => {
    if (!window.confirm('确定要删除这个订阅源吗？已获取的文章不会被删除。')) {
      return
    }
    try {
      await api.delete(`/wechat/feeds/${feedId}`)
      message.success('删除成功')
      if (feedId === selectedFeedId) {
        setSelectedFeedId(null)
        setArticles([])
      }
      await loadFeeds()
    } catch (error) {
      message.error('删除失败: ' + error.message)
    }
  }

  const handleGetHistoryArticles = async (feedId) => {
    try {
      setGettingHistory(true)
      if (historyProgress.id === feedId) {
        // 停止获取
        await api.post(`/wechat/feeds/${feedId}/history`)
        message.info('已停止获取历史文章')
      } else {
        // 开始获取
        await api.post(`/wechat/feeds/${feedId}/history`)
        message.success('开始获取历史文章，请耐心等待')
      }
    } catch (error) {
      message.error('操作失败: ' + error.message)
    } finally {
      setGettingHistory(false)
    }
  }

  const handleRefreshAll = async () => {
    try {
      setRefreshing(true)
      const feeds = await api.get('/wechat/feeds')
      for (const feed of feeds.feeds || []) {
        if (feed.status === 1) {
          try {
            await api.post(`/wechat/feeds/${feed.id}/refresh`)
          } catch (error) {
            console.error(`刷新 ${feed.mp_name} 失败:`, error)
          }
        }
      }
      message.success('批量刷新完成')
      await loadFeeds()
      if (selectedFeedId) {
        await loadArticles()
      }
    } catch (error) {
      message.error('批量刷新失败: ' + error.message)
    } finally {
      setRefreshing(false)
    }
  }

  const feedColumns = [
    {
      title: '公众号',
      key: 'mp_name',
      render: (_, record) => (
        <Space>
          <Avatar src={record.mp_cover} size="small" />
          <span>{record.mp_name}</span>
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusMap = {
          0: { color: 'red', text: '失效' },
          1: { color: 'green', text: '启用' },
          2: { color: 'default', text: '禁用' }
        }
        const info = statusMap[status] || statusMap[0]
        return <Tag color={info.color}>{info.text}</Tag>
      }
    },
    {
      title: '最后同步',
      dataIndex: 'sync_time',
      key: 'sync_time',
      width: 180,
      render: (time) => time ? dayjs(time * 1000).format('YYYY-MM-DD HH:mm:ss') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 300,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            type="link"
            onClick={() => setSelectedFeedId(record.id)}
          >
            查看文章
          </Button>
          <Button
            size="small"
            icon={<ReloadOutlined />}
            loading={refreshing && selectedFeedId === record.id}
            onClick={() => handleRefreshFeed(record.id)}
          >
            刷新
          </Button>
          {record.has_history === 1 && (
            <Tooltip
              title={
                historyProgress.id === record.id
                  ? `正在获取第${historyProgress.page}页...`
                  : '历史文章需要分批次拉取，请耐心等候'
              }
            >
              <Button
                size="small"
                icon={<HistoryOutlined />}
                loading={gettingHistory && historyProgress.id === record.id}
                onClick={() => handleGetHistoryArticles(record.id)}
              >
                {historyProgress.id === record.id ? '停止获取' : '获取历史'}
              </Button>
            </Tooltip>
          )}
          <Switch
            size="small"
            checked={record.status === 1}
            onChange={(checked) => handleUpdateFeedStatus(record.id, checked ? 1 : 2)}
            checkedChildren="启用"
            unCheckedChildren="禁用"
          />
          <Button
            size="small"
            danger
            type="link"
            onClick={() => handleDeleteFeed(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ]

  const articleColumns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text, record) => (
        <a
          href={`https://mp.weixin.qq.com/s/${record.id}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          {text}
        </a>
      )
    },
    {
      title: '发布时间',
      dataIndex: 'publish_time',
      key: 'publish_time',
      width: 180,
      render: (time) => dayjs(time * 1000).format('YYYY-MM-DD HH:mm:ss')
    }
  ]

  return (
    <div style={{ display: 'flex', gap: 16 }}>
      <Card
        title="公众号订阅源"
        style={{ width: 400, flexShrink: 0 }}
        extra={
          <Space>
            <Button size="small" onClick={loadFeeds}>
              刷新列表
            </Button>
            <Button 
              size="small" 
              icon={<ReloadOutlined />}
              onClick={handleRefreshAll}
              loading={refreshing}
            >
              刷新全部
            </Button>
          </Space>
        }
      >
        <Table
          columns={feedColumns}
          dataSource={feeds}
          rowKey="id"
          loading={loading}
          pagination={false}
          size="small"
          onRow={(record) => ({
            onClick: () => setSelectedFeedId(record.id),
            style: {
              cursor: 'pointer',
              backgroundColor: selectedFeedId === record.id ? '#e6f7ff' : 'transparent'
            }
          })}
        />
      </Card>

      <Card
        title={selectedFeedId ? `文章列表 (${feeds.find(f => f.id === selectedFeedId)?.mp_name || ''})` : '文章列表'}
        style={{ flex: 1 }}
        extra={
          selectedFeedId && (
            <Space>
              <Button
                size="small"
                icon={<ReloadOutlined />}
                loading={refreshing}
                onClick={() => handleRefreshFeed(selectedFeedId)}
              >
                刷新文章
              </Button>
              {feeds.find(f => f.id === selectedFeedId)?.has_history === 1 && (
                <Tooltip
                  title={
                    historyProgress.id === selectedFeedId
                      ? `正在获取第${historyProgress.page}页...`
                      : '获取历史文章'
                  }
                >
                  <Button
                    size="small"
                    icon={<HistoryOutlined />}
                    loading={gettingHistory && historyProgress.id === selectedFeedId}
                    onClick={() => handleGetHistoryArticles(selectedFeedId)}
                  >
                    {historyProgress.id === selectedFeedId ? '停止获取' : '获取历史'}
                  </Button>
                </Tooltip>
              )}
            </Space>
          )
        }
      >
        {selectedFeedId ? (
          <Table
            columns={articleColumns}
            dataSource={articles}
            rowKey="id"
            loading={loading}
            pagination={{
              ...pagination,
              showTotal: (total) => `共 ${total} 条文章`,
              showSizeChanger: true,
              showQuickJumper: true,
              onChange: (page, pageSize) => {
                setPagination(prev => ({ ...prev, current: page, pageSize }))
              }
            }}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            请选择一个公众号查看文章列表
          </div>
        )}
      </Card>
    </div>
  )
}

export default WechatDataList


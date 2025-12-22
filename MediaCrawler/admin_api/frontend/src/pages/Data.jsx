import React, { useEffect, useState } from 'react'
import { Card, Table, Tabs, Tag, Input, Button, Space, message, Modal, List, Avatar, Spin, Select } from 'antd'
import { SearchOutlined, ReloadOutlined, CommentOutlined } from '@ant-design/icons'
import { useParams } from 'react-router-dom'
import api from '../utils/api'
import WechatDataList from '../components/WechatDataList'

const { Option } = Select

const { TabPane } = Tabs

const DataPage = () => {
  const { platform } = useParams()
  const [currentPlatform, setCurrentPlatform] = useState(platform || 'xhs')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [filterCrawlerType, setFilterCrawlerType] = useState('')
  const [filterKeyword, setFilterKeyword] = useState('')
  const [filterNoteType, setFilterNoteType] = useState('')
  const [filterOptions, setFilterOptions] = useState({ keywords: [], crawler_types: [] })
  const [sortInfo, setSortInfo] = useState({ field: '', order: '' })
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })
  const [commentsModalVisible, setCommentsModalVisible] = useState(false)
  const [currentNoteId, setCurrentNoteId] = useState(null)
  const [comments, setComments] = useState([])
  const [commentsLoading, setCommentsLoading] = useState(false)
  const [commentsPagination, setCommentsPagination] = useState({
    current: 1,
    pageSize: 50,
    total: 0
  })

  const platformNames = {
    xhs: '小红书',
    dy: '抖音',
    ks: '快手',
    bili: 'B站',
    wb: '微博',
    tieba: '百度贴吧',
    zhihu: '知乎',
    juejin: '掘金',
    medium: 'Medium',
    wechat: '公众号'
  }

  useEffect(() => {
    // 当平台切换时重置搜索和分页（公众号不需要）
    if (currentPlatform !== 'wechat') {
      setSearchText('')
      setFilterCrawlerType('')
      setFilterKeyword('')
      setFilterNoteType('')
      setSortInfo({ field: '', order: '' })
      setPagination({ current: 1, pageSize: 20, total: 0 })
      // 加载筛选选项（小红书和快手）
      if (currentPlatform === 'xhs' || currentPlatform === 'ks') {
        loadFilterOptions()
      }
    }
  }, [currentPlatform])

  useEffect(() => {
    if (currentPlatform !== 'wechat') {
      loadData()
    }
  }, [currentPlatform, pagination.current, pagination.pageSize, filterCrawlerType, filterKeyword, filterNoteType, sortInfo.field, sortInfo.order])

  const loadFilterOptions = async () => {
    try {
      const result = await api.get(`/data/${currentPlatform}/filter-options`)
      setFilterOptions(result)
    } catch (error) {
      console.error('加载筛选选项失败:', error)
    }
  }

  const loadData = async (showMessage = false) => {
    try {
      setLoading(true)
      const params = {
        page: pagination.current,
        page_size: pagination.pageSize,
        keyword: searchText
      }
      // 小红书和快手添加筛选参数
      if (currentPlatform === 'xhs' || currentPlatform === 'ks') {
        if (filterCrawlerType) {
          params.crawler_type = filterCrawlerType
        }
        if (filterKeyword) {
          params.source_keyword = filterKeyword
        }
        if (filterNoteType) {
          params.note_type = filterNoteType
        }
        if (sortInfo.field && sortInfo.order) {
          params.sort_field = sortInfo.field
          params.sort_order = sortInfo.order
        }
      }
      const result = await api.get(`/data/${currentPlatform}`, { params })
      setData(result.data || [])
      setPagination(prev => ({
        ...prev,
        total: result.total || 0
      }))
      if (showMessage) {
        message.success('数据刷新成功')
      }
    } catch (error) {
      console.error('加载数据失败:', error)
      message.error('加载数据失败: ' + (error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    loadData(true)
  }

  const loadComments = async (noteId, page = 1) => {
    try {
      setCommentsLoading(true)
      const result = await api.get(`/data/${currentPlatform}/comments/${noteId}`, {
        params: {
          page: page,
          page_size: commentsPagination.pageSize
        }
      })
      setComments(result.comments || [])
      setCommentsPagination(prev => ({
        ...prev,
        current: page,
        total: result.total || 0
      }))
    } catch (error) {
      console.error('加载评论失败:', error)
      message.error('加载评论失败: ' + (error.message || '未知错误'))
    } finally {
      setCommentsLoading(false)
    }
  }

  const handleViewComments = (noteId) => {
    setCurrentNoteId(noteId)
    setCommentsModalVisible(true)
    setCommentsPagination({ current: 1, pageSize: 50, total: 0 })
    loadComments(noteId, 1)
  }

  const handleCommentsModalClose = () => {
    setCommentsModalVisible(false)
    setCurrentNoteId(null)
    setComments([])
  }

  const handleCommentsTableChange = (page) => {
    if (currentNoteId) {
      loadComments(currentNoteId, page)
    }
  }

  const handleTableChange = (newPagination, filters, sorter) => {
    // 处理分页
    setPagination({
      ...pagination,
      current: newPagination.current,
      pageSize: newPagination.pageSize
    })
    
    // 处理排序
    if (sorter && sorter.field) {
      const order = sorter.order === 'ascend' ? 'asc' : sorter.order === 'descend' ? 'desc' : ''
      setSortInfo({
        field: order ? sorter.field : '',
        order: order
      })
    } else {
      setSortInfo({ field: '', order: '' })
    }
  }

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 300,
      render: (text, record) => (
        <a href={record.note_url} target="_blank" rel="noopener noreferrer">
          {text || '-'}
        </a>
      )
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: '发布时间',
      dataIndex: 'publish_time',
      key: 'publish_time',
      width: 180,
    },
    {
      title: '点赞数',
      dataIndex: 'liked_count',
      key: 'liked_count',
      width: 100,
      sorter: true,
      sortOrder: sortInfo.field === 'liked_count' && (sortInfo.order === 'asc' ? 'ascend' : sortInfo.order === 'desc' ? 'descend' : null),
      render: (count) => count ? <Tag color="red">{count}</Tag> : '-'
    },
    {
      title: '评论数',
      dataIndex: 'comment_count',
      key: 'comment_count',
      width: 100,
      sorter: true,
      sortOrder: sortInfo.field === 'comment_count' && (sortInfo.order === 'asc' ? 'ascend' : sortInfo.order === 'desc' ? 'descend' : null),
      render: (count) => count ? <Tag color="blue">{count}</Tag> : '-'
    },
    {
      title: '收藏数',
      dataIndex: 'collected_count',
      key: 'collected_count',
      width: 100,
      sorter: true,
      sortOrder: sortInfo.field === 'collected_count' && (sortInfo.order === 'asc' ? 'ascend' : sortInfo.order === 'desc' ? 'descend' : null),
      render: (count) => count ? <Tag color="green">{count}</Tag> : '-'
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 80,
      render: (type) => type === 'video' ? <Tag color="purple">视频</Tag> : <Tag>图文</Tag>
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<CommentOutlined />} 
          onClick={() => handleViewComments(record.id)}
        >
          查看评论
        </Button>
      )
    },
  ]

  const tabItems = [
    ...Object.keys(platformNames).filter(key => key !== 'wechat').map(key => ({
      key,
      label: platformNames[key],
      children: (
      <Card>
        <Space style={{ marginBottom: 16 }} wrap>
          {/* 小红书和快手显示筛选选项 */}
          {(key === 'xhs' || key === 'ks') && (
            <>
              <Select
                placeholder="爬取类型"
                value={filterCrawlerType || undefined}
                onChange={(value) => {
                  setFilterCrawlerType(value || '')
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
                allowClear
                style={{ width: 150 }}
              >
                <Option value="search">关键词搜索</Option>
                <Option value="detail">指定帖子详情</Option>
                <Option value="creator">创作者主页</Option>
              </Select>
              <Select
                placeholder="关键词"
                value={filterKeyword || undefined}
                onChange={(value) => {
                  setFilterKeyword(value || '')
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.children ?? '').toLowerCase().includes(input.toLowerCase())
                }
                style={{ width: 150 }}
              >
                {filterOptions.keywords.map(kw => (
                  <Option key={kw} value={kw}>{kw}</Option>
                ))}
              </Select>
              <Select
                placeholder="内容类型"
                value={filterNoteType || undefined}
                onChange={(value) => {
                  setFilterNoteType(value || '')
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
                allowClear
                style={{ width: 120 }}
              >
                <Option value="图文">图文</Option>
                <Option value="视频">视频</Option>
                <Option value="文章">文章</Option>
              </Select>
            </>
          )}
          <Input
            placeholder="搜索标题或作者"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onPressEnter={loadData}
            style={{ width: 300 }}
          />
          <Button type="primary" icon={<SearchOutlined />} onClick={() => {
            setPagination(prev => ({ ...prev, current: 1 }))
            setTimeout(() => loadData(), 0)
          }}>
            搜索
          </Button>
          <Button onClick={() => {
            setSearchText('')
            if (key === 'xhs' || key === 'ks') {
              setFilterCrawlerType('')
              setFilterKeyword('')
              setFilterNoteType('')
              setSortInfo({ field: '', order: '' })
            }
            setPagination(prev => ({ ...prev, current: 1 }))
            setTimeout(() => loadData(), 0)
          }}>
            重置
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            刷新
          </Button>
        </Space>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showTotal: (total) => `共 ${total} 条数据`,
            showSizeChanger: true,
            showQuickJumper: true
          }}
          onChange={handleTableChange}
        />
        <Modal
          title={`评论列表 (共 ${commentsPagination.total} 条)`}
          open={commentsModalVisible}
          onCancel={handleCommentsModalClose}
          footer={null}
          width={800}
        >
          <Spin spinning={commentsLoading}>
            <List
              dataSource={comments}
              pagination={{
                current: commentsPagination.current,
                pageSize: commentsPagination.pageSize,
                total: commentsPagination.total,
                onChange: handleCommentsTableChange,
                showSizeChanger: false,
                showTotal: (total) => `共 ${total} 条评论`
              }}
              renderItem={(comment) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar src={comment.avatar}>{comment.author?.[0] || '?'}</Avatar>}
                    title={
                      <Space>
                        <span>{comment.author || '匿名用户'}</span>
                        {comment.ip_location && <Tag>{comment.ip_location}</Tag>}
                        {comment.like_count > 0 && <Tag color="red">👍 {comment.like_count}</Tag>}
                        {comment.sub_comment_count > 0 && <Tag color="blue">回复 {comment.sub_comment_count}</Tag>}
                      </Space>
                    }
                    description={
                      <div>
                        <div style={{ marginBottom: 8 }}>{comment.content || '-'}</div>
                        <div style={{ fontSize: 12, color: '#999' }}>{comment.create_time || '-'}</div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Spin>
        </Modal>
      </Card>
    )
  })),
    {
      key: 'wechat',
      label: platformNames.wechat,
      children: <WechatDataList />
    }
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>数据列表</h2>
      <Tabs
        activeKey={currentPlatform}
        onChange={setCurrentPlatform}
        items={tabItems}
      />
    </div>
  )
}

export default DataPage


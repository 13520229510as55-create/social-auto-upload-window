import React, { useEffect, useState } from 'react'
import { Card, Table, Button, Tag, Space, message, Modal, Form, Select, Switch, Input } from 'antd'
import { PlayCircleOutlined, StopOutlined, ReloadOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

const { Option } = Select
const { TextArea } = Input

const TasksPage = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [startModalVisible, setStartModalVisible] = useState(false)
  const [form] = Form.useForm()

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
    loadTasks()
    // 每5秒刷新一次
    const interval = setInterval(loadTasks, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadTasks = async () => {
    try {
      const data = await api.get('/tasks')
      setTasks(data.tasks || [])
    } catch (error) {
      console.error('加载任务列表失败:', error)
    }
  }

  const handleStartTask = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)

      // 如果是公众号任务，使用不同的处理逻辑
      if (values.platform === 'wechat') {
        const wxsLinks = values.wxs_links ? values.wxs_links.split('\n').filter(link => link.trim()) : []
        if (wxsLinks.length === 0) {
          message.error('请至少输入一个公众号分享链接')
          setLoading(false)
          return
        }

        // 处理每个公众号链接
        for (const wxsLink of wxsLinks) {
          try {
            // 获取公众号信息
            const mpInfoResult = await api.post('/wechat/mp/info', { wxs_link: wxsLink.trim() })
            if (mpInfoResult.mp_info && mpInfoResult.mp_info.length > 0) {
              const mpInfo = mpInfoResult.mp_info[0]
              
              // 添加订阅源
              await api.post('/wechat/feeds', {
                feed_id: mpInfo.id,
                mp_name: mpInfo.name,
                mp_cover: mpInfo.cover,
                mp_intro: mpInfo.intro,
                update_time: mpInfo.updateTime,
                status: 1
              })

              // 刷新文章
              await api.post(`/wechat/feeds/${mpInfo.id}/refresh`)
              
              message.success(`公众号 ${mpInfo.name} 添加成功`)
            } else {
              message.error('获取公众号信息失败，请检查链接是否正确')
            }
          } catch (error) {
            message.error(`处理链接失败: ${error.message}`)
          }
        }

        setStartModalVisible(false)
        form.resetFields()
        return
      }

      // 处理关键词：如果是数组则转换为逗号分隔的字符串，如果是字符串则直接使用
      let keywords = values.keywords || ''
      if (Array.isArray(keywords)) {
        keywords = keywords.join(',')
      }

      const taskRequest = {
        platform: values.platform,
        config: {
          platform: values.platform,
          keywords: keywords,
          // 根据用户的选择设置登录类型
          // 如果用户选择强制重新登录，则使用qrcode，否则让后端自动检测cookie
          login_type: values.force_relogin ? 'qrcode' : 'auto', // 'auto'表示自动检测cookie
          crawler_type: values.crawler_type || 'search',
          start_page: 1,
          max_notes_count: values.max_notes_count || 15,
          enable_get_comments: values.enable_get_comments !== false,
          max_comments_count: values.max_comments_count || 10,
          enable_get_medias: false,
          headless: values.headless === undefined ? false : values.headless, // 默认为false（有头模式）
          save_data_option: 'json',
          // 添加强制重新登录标志
          force_relogin: values.force_relogin || false
        }
      }

      await api.post('/tasks/start', taskRequest)
      message.success('任务已启动')
      setStartModalVisible(false)
      form.resetFields()
      loadTasks()
    } catch (error) {
      message.error('启动任务失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStopTask = async (taskId) => {
    try {
      await api.delete(`/tasks/${taskId}`)
      message.success('任务已停止')
      loadTasks()
    } catch (error) {
      message.error('停止任务失败: ' + error.message)
    }
  }

  const getStatusTag = (status) => {
    const statusMap = {
      running: { color: 'processing', text: '运行中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
      cancelled: { color: 'default', text: '已取消' },
      pending: { color: 'warning', text: '等待中' }
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const columns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      ellipsis: true,
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform) => platformNames[platform] || platform
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusTag(status)
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress) => `${progress || 0}%`
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          {record.status === 'running' && (
            <Button
              size="small"
              danger
              icon={<StopOutlined />}
              onClick={() => handleStopTask(record.task_id)}
            >
              停止
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>任务管理</h2>
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={() => setStartModalVisible(true)}
        >
          启动新任务
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="task_id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showTotal: (total) => `共 ${total} 条任务`
          }}
        />
      </Card>

      <Modal
        title="启动新任务"
        open={startModalVisible}
        onOk={handleStartTask}
        onCancel={() => {
          setStartModalVisible(false)
          form.resetFields()
        }}
        confirmLoading={loading}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="平台"
            name="platform"
            rules={[{ required: true, message: '请选择平台' }]}
          >
            <Select 
              placeholder="请选择平台"
              onChange={(value) => {
                // 切换平台时重置表单
                form.setFieldsValue({
                  crawler_type: value === 'wechat' ? undefined : 'search',
                  keywords: undefined,
                  wxs_links: undefined
                })
              }}
            >
              <Option value="xhs">小红书</Option>
              <Option value="dy">抖音</Option>
              <Option value="ks">快手</Option>
              <Option value="bili">B站</Option>
              <Option value="wb">微博</Option>
              <Option value="tieba">百度贴吧</Option>
              <Option value="zhihu">知乎</Option>
              <Option value="juejin">掘金</Option>
              <Option value="medium">Medium</Option>
              <Option value="wechat">公众号</Option>
            </Select>
          </Form.Item>

          {Form.useWatch('platform', form) === 'wechat' ? (
            <Form.Item
              label="公众号分享链接"
              name="wxs_links"
              rules={[{ required: true, message: '请输入公众号分享链接' }]}
              tooltip="输入公众号文章分享链接，一行一条，例如：https://mp.weixin.qq.com/s/xxxxxx"
            >
              <TextArea
                rows={4}
                placeholder="请输入公众号文章分享链接，一行一条，例如：&#10;https://mp.weixin.qq.com/s/xxxxxx&#10;https://mp.weixin.qq.com/s/yyyyyy"
              />
            </Form.Item>
          ) : (
            <>
              <Form.Item
                label="爬取类型"
                name="crawler_type"
                rules={[{ required: true, message: '请选择爬取类型' }]}
              >
                <Select>
                  <Option value="search">关键词搜索</Option>
                  <Option value="detail">指定帖子详情</Option>
                  <Option value="creator">创作者主页</Option>
                </Select>
              </Form.Item>
            </>
          )}

          {Form.useWatch('platform', form) !== 'wechat' && (
            <>
              <Form.Item
                label="关键词（搜索模式，多个用逗号分隔）"
                name="keywords"
                tooltip="输入关键词，多个关键词用逗号分隔，例如：deepseek,AI,编程"
              >
                <Select 
                  mode="tags" 
                  placeholder="输入关键词，按回车添加多个，或直接输入逗号分隔的字符串"
                  tokenSeparators={[',']}
                />
              </Form.Item>

              <Form.Item
                label="最大爬取数量"
                name="max_notes_count"
                initialValue={15}
              >
                <Select>
                  <Option value={10}>10</Option>
                  <Option value={15}>15</Option>
                  <Option value={20}>20</Option>
                  <Option value={50}>50</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="无头模式（不显示浏览器窗口）"
                name="headless"
                initialValue={false}
                tooltip="启用后将不显示浏览器窗口，适合后台运行。建议关闭无头模式以避免被平台检测"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                label="是否爬取评论"
                name="enable_get_comments"
                initialValue={true}
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>

              <Form.Item
                label="最大评论数量"
                name="max_comments_count"
                initialValue={10}
              >
                <Select>
                  <Option value={5}>5</Option>
                  <Option value={10}>10</Option>
                  <Option value={20}>20</Option>
                  <Option value={50}>50</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="强制重新登录"
                name="force_relogin"
                initialValue={false}
                tooltip="勾选后将忽略已保存的cookie，强制使用二维码重新登录。适用于cookie过期或账号权限问题的情况"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default TasksPage


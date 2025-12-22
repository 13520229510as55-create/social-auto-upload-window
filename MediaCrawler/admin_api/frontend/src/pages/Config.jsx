import React, { useEffect, useState } from 'react'
import { 
  Card, 
  Form, 
  Input, 
  Select, 
  Switch, 
  InputNumber, 
  Button, 
  Tabs, 
  message,
  Space,
  Tag
} from 'antd'
import { SaveOutlined, LoginOutlined, DeleteOutlined } from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../utils/api'
import QRCodeLogin from '../components/QRCodeLogin'
import WechatAccountManager from '../components/WechatAccountManager'

const { Option } = Select
const { TextArea } = Input

const ConfigPage = () => {
  const { platform } = useParams()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [platforms, setPlatforms] = useState([])
  const [currentPlatform, setCurrentPlatform] = useState(platform || 'xhs')
  const [loading, setLoading] = useState(false)
  const [hasCookie, setHasCookie] = useState(false)

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

  useEffect(() => {
    loadPlatforms()
  }, [])

  useEffect(() => {
    if (currentPlatform && currentPlatform !== 'wechat') {
      loadConfig(currentPlatform)
      checkCookie(currentPlatform)
      navigate(`/config/${currentPlatform}`, { replace: true })
    } else if (currentPlatform === 'wechat') {
      navigate(`/config/wechat`, { replace: true })
    }
  }, [currentPlatform])

  const loadPlatforms = async () => {
    try {
      const data = await api.get('/platforms')
      setPlatforms(data.platforms)
    } catch (error) {
      message.error('加载平台列表失败')
    }
  }

  const loadConfig = async (plat) => {
    try {
      setLoading(true)
      const data = await api.get(`/config/${plat}`)
      form.setFieldsValue(data)
    } catch (error) {
      message.error('加载配置失败')
    } finally {
      setLoading(false)
    }
  }

  const checkCookie = async (plat) => {
    try {
      const data = await api.get(`/login/cookie/${plat}`)
      setHasCookie(data.has_cookie)
    } catch (error) {
      setHasCookie(false)
    }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)
      
      const configData = {
        platform: currentPlatform,
        keywords: values.keywords || '',
        login_type: values.login_type || 'qrcode',
        crawler_type: values.crawler_type || 'search',
        start_page: values.start_page || 1,
        max_notes_count: values.max_notes_count || 15,
        enable_get_comments: values.enable_get_comments !== false,
        max_comments_count: values.max_comments_count || 10,
        enable_get_medias: values.enable_get_medias || false,
        headless: values.headless || false,
        save_data_option: values.save_data_option || 'json',
        specified_urls: values.specified_urls ? values.specified_urls.split('\n').filter(Boolean) : [],
        creator_ids: values.creator_ids ? values.creator_ids.split('\n').filter(Boolean) : [],
        platform_specific: {}
      }

      await api.post(`/config/${currentPlatform}`, configData)
      message.success('配置保存成功')
    } catch (error) {
      message.error('保存配置失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handlePlatformChange = (value) => {
    setCurrentPlatform(value)
  }

  const handleLoginSuccess = () => {
    setHasCookie(true)
    message.success('登录成功，Cookie已保存')
  }

  const handleDeleteCookie = async () => {
    try {
      const response = await api.delete(`/login/cookie/${currentPlatform}`)
      if (response.success) {
        setHasCookie(false)
        message.success('Cookie已清除')
      } else {
        message.warning(response.message || '清除失败')
      }
    } catch (error) {
      message.error('清除Cookie失败: ' + (error.message || '未知错误'))
    }
  }

  // 添加公众号 Tab
  const allTabItems = [
    ...platforms.map(p => ({
      key: p.value,
      label: p.label,
      children: (
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          login_type: 'qrcode',
          crawler_type: 'search',
          start_page: 1,
          max_notes_count: 15,
          enable_get_comments: true,
          max_comments_count: 10,
          enable_get_medias: false,
          headless: false,
          save_data_option: 'json'
        }}
      >
        <Card 
          title="登录状态" 
          extra={
            <Space>
              {hasCookie ? (
                <>
                  <Tag color="green">已登录</Tag>
                  <Button 
                    type="default" 
                    danger
                    icon={<DeleteOutlined />}
                    onClick={handleDeleteCookie}
                    size="small"
                  >
                    清除Cookie
                  </Button>
                </>
              ) : (
                <Tag color="red">未登录</Tag>
              )}
              <QRCodeLogin 
                platform={currentPlatform} 
                onSuccess={handleLoginSuccess}
              />
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Form.Item label="登录方式" name="login_type">
            <Select>
              <Option value="qrcode">二维码登录</Option>
              <Option value="cookie">Cookie登录</Option>
              <Option value="phone">手机号登录</Option>
            </Select>
          </Form.Item>
        </Card>

        <Card title="基础配置">
          <Form.Item label="爬取类型" name="crawler_type">
            <Select>
              <Option value="search">关键词搜索</Option>
              <Option value="detail">指定帖子详情</Option>
              <Option value="creator">创作者主页</Option>
            </Select>
          </Form.Item>

          <Form.Item label="关键词（搜索模式）" name="keywords">
            <Input placeholder="多个关键词用英文逗号分隔" />
          </Form.Item>

          <Form.Item label="起始页数" name="start_page">
            <InputNumber min={1} />
          </Form.Item>

          <Form.Item label="最大爬取数量" name="max_notes_count">
            <InputNumber min={1} />
          </Form.Item>

          <Form.Item label="数据保存格式" name="save_data_option">
            <Select>
              <Option value="json">JSON</Option>
              <Option value="csv">CSV</Option>
              <Option value="excel">Excel</Option>
              <Option value="db">数据库</Option>
              <Option value="sqlite">SQLite</Option>
            </Select>
          </Form.Item>
        </Card>

        <Card title="评论配置">
          <Form.Item label="是否爬取评论" name="enable_get_comments" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item label="单帖子最大评论数" name="max_comments_count">
            <InputNumber min={0} />
          </Form.Item>
        </Card>

        <Card title="其他配置">
          <Form.Item label="是否爬取媒体文件" name="enable_get_medias" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item label="无头模式" name="headless" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Card>

        {currentPlatform === 'xhs' && (
          <Card title="小红书特定配置">
            <Form.Item label="指定笔记URL列表（每行一个）" name="specified_urls">
              <TextArea rows={4} placeholder="请输入完整的笔记URL，每行一个" />
            </Form.Item>

            <Form.Item label="指定创作者ID列表（每行一个）" name="creator_ids">
              <TextArea rows={4} placeholder="请输入完整的创作者URL，每行一个" />
            </Form.Item>
          </Card>
        )}

        <Card>
          <Button 
            type="primary" 
            icon={<SaveOutlined />} 
            onClick={handleSave}
            loading={loading}
            size="large"
          >
            保存配置
          </Button>
        </Card>
      </Form>
    )
  })),
    {
      key: 'wechat',
      label: '公众号',
      children: <WechatAccountManager />
    }
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>配置管理</h2>
      <Tabs
        activeKey={currentPlatform}
        onChange={handlePlatformChange}
        items={allTabItems}
      />
    </div>
  )
}

export default ConfigPage


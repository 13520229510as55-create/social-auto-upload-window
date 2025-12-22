import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Table, 
  Button, 
  Tag, 
  Space, 
  message, 
  Modal, 
  Spin,
  Select,
  QRCode
} from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../utils/api'

const { Option } = Select

/**
 * 微信读书账号管理组件
 * 功能：添加账号、查看账号列表、更新账号状态、删除账号
 */
const WechatAccountManager = () => {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [loginModalVisible, setLoginModalVisible] = useState(false)
  const [qrcodeUrl, setQrcodeUrl] = useState('')
  const [loginUuid, setLoginUuid] = useState('')
  const [countdown, setCountdown] = useState(0)

  const statusMap = {
    0: { color: 'red', text: '失效' },
    1: { color: 'green', text: '启用' },
    2: { color: 'default', text: '禁用' }
  }

  useEffect(() => {
    loadAccounts()
  }, [])

  useEffect(() => {
    if (loginModalVisible && loginUuid) {
      // 开始倒计时
      setCountdown(60)
      // 开始轮询登录结果
      const interval = setInterval(async () => {
        try {
          const result = await api.get(`/wechat/login/result/${loginUuid}`)
          if (result.vid && result.token) {
            // 登录成功，添加账号
            await addAccount({
              account_id: String(result.vid),
              name: result.username || `用户${result.vid}`,
              token: result.token,
              status: 1
            })
            message.success('账号添加成功')
            setLoginModalVisible(false)
            setQrcodeUrl('')
            setLoginUuid('')
            loadAccounts()
          } else if (result.message) {
            // 有错误消息
            if (result.message.includes('过期') || result.message.includes('expired')) {
              message.warning('二维码已过期，请重新获取')
              setLoginModalVisible(false)
            }
          }
        } catch (error) {
          console.error('检查登录状态失败:', error)
        }
      }, 2000)

      // 倒计时
      const countdownInterval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(countdownInterval)
            return 0
          }
          return prev - 1
        })
      }, 1000)

      return () => {
        clearInterval(interval)
        clearInterval(countdownInterval)
      }
    }
  }, [loginModalVisible, loginUuid])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      const data = await api.get('/wechat/accounts')
      setAccounts(data.accounts || [])
    } catch (error) {
      message.error('加载账号列表失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateLoginUrl = async () => {
    try {
      setLoginModalVisible(true)
      const result = await api.post('/wechat/login/create-url')
      setQrcodeUrl(result.scanUrl)
      setLoginUuid(result.uuid)
    } catch (error) {
      message.error('获取登录二维码失败: ' + error.message)
      setLoginModalVisible(false)
    }
  }

  const addAccount = async (accountData) => {
    try {
      await api.post('/wechat/accounts', accountData)
      await loadAccounts()
    } catch (error) {
      message.error('添加账号失败: ' + error.message)
      throw error
    }
  }

  const updateAccountStatus = async (accountId, status) => {
    try {
      await api.put(`/wechat/accounts/${accountId}/status`, { status })
      message.success('状态更新成功')
      await loadAccounts()
    } catch (error) {
      message.error('更新状态失败: ' + error.message)
    }
  }

  const deleteAccount = async (accountId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个账号吗？',
      onOk: async () => {
        try {
          await api.delete(`/wechat/accounts/${accountId}`)
          message.success('删除成功')
          await loadAccounts()
        } catch (error) {
          message.error('删除失败: ' + error.message)
        }
      }
    })
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100
    },
    {
      title: '用户名',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '状态',
      key: 'status',
      width: 120,
      render: (_, record) => {
        const statusInfo = statusMap[record.status] || statusMap[0]
        const isBlocked = record.is_blocked
        return (
          <Space>
            {isBlocked ? (
              <Tag color="orange">今日小黑屋</Tag>
            ) : (
              <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
            )}
          </Space>
        )
      }
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (time) => {
        if (!time) return '-'
        const date = new Date(time * 1000)
        return date.toLocaleDateString('zh-CN')
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Select
            value={record.status}
            onChange={(value) => updateAccountStatus(record.id, value)}
            size="small"
            style={{ width: 100 }}
          >
            <Option value={0}>失效</Option>
            <Option value={1}>启用</Option>
            <Option value={2}>禁用</Option>
          </Select>
          <Button
            type="link"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => deleteAccount(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontWeight: 'bold' }}>共{accounts.length}个账号</div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreateLoginUrl}
        >
          添加读书账号
        </Button>
      </div>
      <Card>
        <Table
          columns={columns}
          dataSource={accounts}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showTotal: (total) => `共 ${total} 个账号`
          }}
        />
      </Card>

      <Modal
        title="添加微信读书账号"
        open={loginModalVisible}
        onCancel={() => {
          setLoginModalVisible(false)
          setQrcodeUrl('')
          setLoginUuid('')
          setCountdown(0)
        }}
        footer={null}
        width={400}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          {qrcodeUrl ? (
            <>
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
                <QRCode
                  value={qrcodeUrl}
                  size={200}
                  errorLevel="M"
                />
              </div>
              <p style={{ marginTop: 16, color: '#666' }}>
                微信扫码登录
                {countdown > 0 && <span style={{ color: '#ff4d4f' }}> ({countdown}s)</span>}
              </p>
              <p style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
                注意：不要勾选"24小时后自动退出"
              </p>
            </>
          ) : (
            <Spin size="large" />
          )}
        </div>
      </Modal>
    </div>
  )
}

export default WechatAccountManager


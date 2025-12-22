import React, { useState, useEffect, useCallback } from 'react'
import { Modal, Button, Image, message, Spin } from 'antd'
import { LoginOutlined } from '@ant-design/icons'
import api from '../utils/api'

const QRCodeLogin = ({ platform, onSuccess }) => {
  const [visible, setVisible] = useState(false)
  const [qrcode, setQrcode] = useState('')
  const [qrcodeId, setQrcodeId] = useState('')
  const [status, setStatus] = useState('pending')
  const [loading, setLoading] = useState(false)

  const checkLoginStatus = useCallback(async () => {
    if (!qrcodeId) {
      console.log('[QRCodeLogin] checkLoginStatus: qrcodeId为空，跳过检查')
      return
    }

    // 对于知乎平台，返回的是页面截图而不是二维码，不进行状态检查
    // 用户需要手动在截图中找到二维码并扫描，所以不应该自动关闭弹窗
    if (platform === 'zhihu') {
      console.log('[QRCodeLogin] 知乎平台：跳过状态检查（使用页面截图）')
      return
    }

    try {
      console.log('[QRCodeLogin] 检查登录状态，qrcodeId:', qrcodeId)
      const data = await api.get(`/login/status/${qrcodeId}`)
      console.log('[QRCodeLogin] 登录状态响应:', data)
      setStatus(data.status)

      if (data.status === 'success') {
        message.success('登录成功！')
        setVisible(false)
        if (onSuccess) onSuccess()
      } else if (data.status === 'expired') {
        message.warning('二维码已过期，请重新获取')
        setVisible(false)
      }
    } catch (error) {
      console.error('[QRCodeLogin] 检查登录状态失败:', error)
    }
  }, [qrcodeId, onSuccess, platform])

  useEffect(() => {
    // 对于知乎平台，不进行状态轮询（因为返回的是页面截图）
    if (platform === 'zhihu') {
      console.log('[QRCodeLogin] 知乎平台：不进行状态轮询')
      return
    }

    if (visible && qrcodeId) {
      console.log('[QRCodeLogin] 开始轮询登录状态，qrcodeId:', qrcodeId)
      // 立即检查一次
      checkLoginStatus()
      // 然后每2秒检查一次
      const interval = setInterval(() => {
        checkLoginStatus()
      }, 2000)

      return () => {
        console.log('[QRCodeLogin] 停止轮询登录状态')
        clearInterval(interval)
      }
    }
  }, [visible, qrcodeId, checkLoginStatus, platform])

  const handleOpen = async () => {
    try {
      console.log('开始获取二维码，平台:', platform)
      setLoading(true)
      setVisible(true)
      
      // 添加force=true参数，允许强制重新登录（即使已有cookie）
      const data = await api.post(`/login/qrcode?platform=${platform}&force=true`)
      
      console.log('获取二维码响应:', data)
      
      if (data.has_cookie) {
        message.info('已有登录状态，无需重新登录')
        setVisible(false)
        if (onSuccess) onSuccess()
        return
      }

      if (data.error) {
        message.error(data.error || '二维码获取失败，请检查后端服务')
        setVisible(false)
        return
      }

      if (!data.qrcode_base64) {
        message.warning('二维码获取失败，请检查后端服务或安装完整依赖')
        setVisible(false)
        return
      }

      setQrcode(data.qrcode_base64)
      setQrcodeId(data.qrcode_id)
      setStatus('pending')
    } catch (error) {
      console.error('获取二维码错误:', error)
      message.error('获取二维码失败: ' + (error.message || '未知错误'))
      setVisible(false)
    } finally {
      setLoading(false)
    }
  }


  const handleCancel = () => {
    setVisible(false)
    setQrcode('')
    setQrcodeId('')
    setStatus('pending')
  }

  return (
    <>
      <Button 
        type="primary" 
        icon={<LoginOutlined />}
        onClick={handleOpen}
      >
        登录
      </Button>
      <Modal
        title="扫码登录"
        open={visible}
        onCancel={handleCancel}
        footer={null}
        width={400}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          {loading ? (
            <Spin size="large" />
          ) : qrcode ? (
            <>
              <Image
                src={qrcode.startsWith('data:image') ? qrcode : `data:image/png;base64,${qrcode}`}
                alt="登录二维码"
                style={{ maxWidth: '100%' }}
              />
              <p style={{ marginTop: 16, color: '#666' }}>
                {platform === 'zhihu' ? (
                  '请查看页面截图，找到二维码并使用手机APP扫描登录'
                ) : (
                  <>
                    {status === 'pending' && '请使用手机APP扫描二维码登录'}
                    {status === 'success' && '登录成功！'}
                    {status === 'expired' && '二维码已过期'}
                  </>
                )}
              </p>
            </>
          ) : (
            <p>正在生成二维码...</p>
          )}
        </div>
      </Modal>
    </>
  )
}

export default QRCodeLogin


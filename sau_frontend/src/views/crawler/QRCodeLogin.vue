<template>
  <div>
    <el-button 
      type="primary" 
      :icon="Key"
      @click="handleOpen"
    >
      登录
    </el-button>
    
    <el-dialog
      v-model="visible"
      title="扫码登录"
      width="400px"
      :close-on-click-modal="false"
      @close="handleCancel"
    >
      <div style="text-align: center; padding: 20px 0">
        <el-skeleton v-if="loading" :rows="5" animated />
        <div v-else-if="qrcode">
          <el-image
            :src="qrcode.startsWith('data:image') ? qrcode : `data:image/png;base64,${qrcode}`"
            alt="登录二维码"
            style="max-width: 100%"
          />
          <p style="margin-top: 16px; color: #666">
            <template v-if="platform === 'zhihu'">
              请查看页面截图，找到二维码并使用手机APP扫描登录
            </template>
            <template v-else>
              <span v-if="status === 'pending'">请使用手机APP扫描二维码登录</span>
              <span v-else-if="status === 'success'">登录成功！</span>
              <span v-else-if="status === 'expired'">二维码已过期</span>
            </template>
          </p>
        </div>
        <p v-else>正在生成二维码...</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, onBeforeUnmount } from 'vue'
import { Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import crawlerApi from '@/api/crawler'

const props = defineProps({
  platform: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['success'])

const visible = ref(false)
const qrcode = ref('')
const qrcodeId = ref('')
const status = ref('pending')
const loading = ref(false)
let checkInterval = null

const checkLoginStatus = async () => {
  if (!qrcodeId.value || !visible.value) {
    // 如果弹窗已关闭或没有qrcodeId，停止检查
    if (checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
    return
  }

  // 对于知乎平台，返回的是页面截图而不是二维码，不进行状态检查
  if (props.platform === 'zhihu') {
    return
  }

  try {
    console.log('[QRCodeLogin] 检查登录状态，qrcodeId:', qrcodeId.value)
    const data = await crawlerApi.checkLoginStatus(qrcodeId.value)
    console.log('[QRCodeLogin] 登录状态响应:', data)
    status.value = data.status

    if (data.status === 'success') {
      console.log('[QRCodeLogin] 登录成功，关闭弹窗')
      // 先清除轮询
      if (checkInterval) {
        clearInterval(checkInterval)
        checkInterval = null
      }
      ElMessage.success('登录成功！')
      visible.value = false
      emit('success')
    } else if (data.status === 'expired') {
      console.log('[QRCodeLogin] 二维码已过期')
      // 先清除轮询
      if (checkInterval) {
        clearInterval(checkInterval)
        checkInterval = null
      }
      ElMessage.warning('二维码已过期，请重新获取')
      visible.value = false
    }
  } catch (error) {
    console.error('[QRCodeLogin] 检查登录状态失败:', error)
  }
}

watch([visible, qrcodeId], ([newVisible, newQrcodeId]) => {
  // 对于知乎平台，不进行状态轮询
  if (props.platform === 'zhihu') {
    return
  }

  // 先清除之前的轮询
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }

  if (newVisible && newQrcodeId) {
    console.log('[QRCodeLogin] 开始轮询登录状态，qrcodeId:', newQrcodeId)
    // 立即检查一次
    checkLoginStatus()
    // 然后每2秒检查一次
    checkInterval = setInterval(() => {
      checkLoginStatus()
    }, 2000)
  } else {
    console.log('[QRCodeLogin] 停止轮询登录状态')
  }
}, { immediate: false })

// 监听 visible 变化，确保弹窗关闭时清除轮询
watch(visible, (newVisible) => {
  if (!newVisible) {
    console.log('[QRCodeLogin] 弹窗关闭，清除轮询')
    if (checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
    // 重置状态
    qrcode.value = ''
    qrcodeId.value = ''
    status.value = 'pending'
  }
})

onBeforeUnmount(() => {
  console.log('[QRCodeLogin] 组件卸载前，清除轮询')
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
})

onUnmounted(() => {
  console.log('[QRCodeLogin] 组件已卸载')
})

const handleOpen = async () => {
  try {
    loading.value = true
    visible.value = true
    
    // 添加force=true参数，允许强制重新登录
    const data = await crawlerApi.getQRCode(props.platform, true)
    
    if (data.has_cookie) {
      ElMessage.info('已有登录状态，无需重新登录')
      visible.value = false
      emit('success')
      return
    }

    if (data.error) {
      ElMessage.error(data.error || '二维码获取失败，请检查后端服务')
      visible.value = false
      return
    }

    if (!data.qrcode_base64) {
      ElMessage.warning('二维码获取失败，请检查后端服务或安装完整依赖')
      visible.value = false
      return
    }

    qrcode.value = data.qrcode_base64
    qrcodeId.value = data.qrcode_id
    status.value = 'pending'
  } catch (error) {
    console.error('获取二维码错误:', error)
    ElMessage.error('获取二维码失败: ' + (error.message || '未知错误'))
    visible.value = false
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  console.log('[QRCodeLogin] 用户取消登录')
  // 先清除轮询
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
  visible.value = false
  qrcode.value = ''
  qrcodeId.value = ''
  status.value = 'pending'
}
</script>


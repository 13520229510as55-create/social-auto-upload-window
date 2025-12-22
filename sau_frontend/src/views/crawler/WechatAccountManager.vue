<template>
  <div>
    <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center">
      <div style="font-weight: bold">共{{ accounts.length }}个账号</div>
      <el-button
        type="primary"
        :icon="Plus"
        @click="handleCreateLoginUrl"
      >
        添加读书账号
      </el-button>
    </div>
    
    <el-card>
      <el-table
        :data="accounts"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="name" label="用户名" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_blocked" type="warning">今日小黑屋</el-tag>
            <el-tag v-else :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-space>
              <el-select
                :model-value="row.status"
                @change="(value) => updateAccountStatus(row.id, value)"
                size="small"
                style="width: 100px"
              >
                <el-option label="失效" :value="0" />
                <el-option label="启用" :value="1" />
                <el-option label="禁用" :value="2" />
              </el-select>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="deleteAccount(row.id)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="loginModalVisible"
      title="添加微信读书账号"
      width="400px"
      @close="handleCloseLoginModal"
    >
      <div style="text-align: center; padding: 20px 0">
        <div v-if="qrcodeUrl" style="display: flex; justify-content: center; margin-bottom: 16px">
          <el-qrcode
            :value="qrcodeUrl"
            :size="200"
            :error-level="'M'"
          />
        </div>
        <p style="margin-top: 16px; color: #666">
          微信扫码登录
          <span v-if="countdown > 0" style="color: #ff4d4f"> ({{ countdown }}s)</span>
        </p>
        <p style="font-size: 12px; color: #999; margin-top: 8px">
          注意：不要勾选"24小时后自动退出"
        </p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import crawlerApi from '@/api/crawler'

const accounts = ref([])
const loading = ref(false)
const loginModalVisible = ref(false)
const qrcodeUrl = ref('')
const loginUuid = ref('')
const countdown = ref(0)

let checkInterval = null
let countdownInterval = null

const statusMap = {
  0: { type: 'danger', text: '失效' },
  1: { type: 'success', text: '启用' },
  2: { type: 'info', text: '禁用' }
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
}

const getStatusText = (status) => {
  return statusMap[status]?.text || '未知'
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadAccounts()
})

watch([loginModalVisible, loginUuid], ([newVisible, newUuid]) => {
  if (newVisible && newUuid) {
    // 开始倒计时
    countdown.value = 60
    // 开始轮询登录结果
    checkInterval = setInterval(async () => {
      try {
        const result = await crawlerApi.getWechatLoginResult(newUuid)
        if (result.vid && result.token) {
          // 登录成功，添加账号
          await addAccount({
            account_id: String(result.vid),
            name: result.username || `用户${result.vid}`,
            token: result.token,
            status: 1
          })
          ElMessage.success('账号添加成功')
          handleCloseLoginModal()
          loadAccounts()
        } else if (result.message) {
          if (result.message.includes('过期') || result.message.includes('expired')) {
            ElMessage.warning('二维码已过期，请重新获取')
            handleCloseLoginModal()
          }
        }
      } catch (error) {
        console.error('检查登录状态失败:', error)
      }
    }, 2000)

    // 倒计时
    countdownInterval = setInterval(() => {
      if (countdown.value <= 1) {
        clearInterval(countdownInterval)
        countdown.value = 0
      } else {
        countdown.value--
      }
    }, 1000)
  } else {
    if (checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
    if (countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
  }
})

onUnmounted(() => {
  if (checkInterval) clearInterval(checkInterval)
  if (countdownInterval) clearInterval(countdownInterval)
})

const loadAccounts = async () => {
  try {
    loading.value = true
    const data = await crawlerApi.getWechatAccounts()
    accounts.value = data.accounts || []
  } catch (error) {
    ElMessage.error('加载账号列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleCreateLoginUrl = async () => {
  try {
    loginModalVisible.value = true
    const result = await crawlerApi.createWechatLoginUrl()
    qrcodeUrl.value = result.scanUrl
    loginUuid.value = result.uuid
  } catch (error) {
    ElMessage.error('获取登录二维码失败: ' + error.message)
    loginModalVisible.value = false
  }
}

const addAccount = async (accountData) => {
  try {
    await crawlerApi.addWechatAccount(accountData)
    await loadAccounts()
  } catch (error) {
    ElMessage.error('添加账号失败: ' + error.message)
    throw error
  }
}

const updateAccountStatus = async (accountId, status) => {
  try {
    await crawlerApi.updateWechatAccountStatus(accountId, status)
    ElMessage.success('状态更新成功')
    await loadAccounts()
  } catch (error) {
    ElMessage.error('更新状态失败: ' + error.message)
  }
}

const deleteAccount = async (accountId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个账号吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await crawlerApi.deleteWechatAccount(accountId)
    ElMessage.success('删除成功')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const handleCloseLoginModal = () => {
  loginModalVisible.value = false
  qrcodeUrl.value = ''
  loginUuid.value = ''
  countdown.value = 0
}
</script>


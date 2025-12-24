<template>
  <div class="account-management">
    <div class="account-tabs">
      <el-tabs v-model="activeTab" class="account-tabs-nav">
        <!-- 图文Tab -->
        <el-tab-pane label="图文" name="image-text">
          <div class="account-list-container">
            <!-- 筛选选项 -->
            <div class="filter-section">
              <span class="filter-label">平台类型: </span>
              <el-radio-group v-model="selectedPlatforms.imageText" @change="handlePlatformFilterChange">
                <el-radio 
                  v-for="platform in filterOptions['image-text']" 
                  :key="platform" 
                  :label="platform"
                  class="filter-radio"
                >
                  {{ platform }}
                </el-radio>
              </el-radio-group>
            </div>
            
            <div class="search-toolbar">
              <div class="search-box">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索账号名称、平台..."
                  clearable
                  @clear="handleSearch"
                  @input="handleSearch"
                  class="search-input"
                  size="large"
                >
                  <template #prefix>
                    <el-icon class="search-icon"><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="toolbar-actions">
                <el-button 
                  type="primary" 
                  @click="handleAddAccount('image-text')" 
                  class="primary-action-btn"
                  size="large"
                >
                  <el-icon><Plus /></el-icon>
                  <span class="btn-text">添加账号</span>
                </el-button>
                <el-button 
                  @click="fetchAccounts" 
                  :loading="appStore.isAccountRefreshing" 
                  class="secondary-action-btn"
                  size="large"
                >
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span class="btn-text">{{ appStore.isAccountRefreshing ? '刷新中' : '刷新' }}</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredImageTextAccounts.length > 0" class="account-list">
              <el-table :data="filteredImageTextAccounts" style="width: 100%">
                <el-table-column label="头像" width="70" align="center">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="账号名称" min-width="200">
                  <template #default="scope">
                    <div class="account-name">
                      <span class="name-text">{{ scope.row.name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="platform" label="平台" width="120" align="center">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="light"
                      class="platform-tag"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="120" align="center">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="light"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                      class="status-tag"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="340" align="center">
                  <template #default="scope">
                    <div class="action-buttons-group">
                      <el-button size="small" @click="handleEdit(scope.row)" class="action-btn">
                        <el-icon><Edit /></el-icon>
                        编辑
                      </el-button>
                      <el-button size="small" type="primary" @click="handleDownloadCookie(scope.row)" class="action-btn">
                        <el-icon><Download /></el-icon>
                        下载
                      </el-button>
                      <el-button size="small" type="info" @click="handleUploadCookie(scope.row)" class="action-btn">
                        <el-icon><Upload /></el-icon>
                        上传
                      </el-button>
                      <el-button size="small" type="danger" @click="handleDelete(scope.row)" class="action-btn">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty :description="`暂无${selectedPlatforms.imageText || '图文'}账号数据`" />
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 文章Tab -->
        <el-tab-pane label="文章" name="article">
          <div class="account-list-container">
            <!-- 筛选选项 -->
            <div class="filter-section">
              <span class="filter-label">平台类型：</span>
              <el-radio-group v-model="selectedPlatforms.article" @change="handlePlatformFilterChange">
                <el-radio 
                  v-for="platform in filterOptions.article" 
                  :key="platform" 
                  :label="platform"
                  class="filter-radio"
                >
                  {{ platform }}
                </el-radio>
              </el-radio-group>
            </div>
            
            <div class="search-toolbar">
              <div class="search-box">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索账号名称、平台..."
                  clearable
                  @clear="handleSearch"
                  @input="handleSearch"
                  class="search-input"
                  size="large"
                >
                  <template #prefix>
                    <el-icon class="search-icon"><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="toolbar-actions">
                <el-button 
                  type="primary" 
                  @click="handleAddAccount('article')" 
                  class="primary-action-btn"
                  size="large"
                >
                  <el-icon><Plus /></el-icon>
                  <span class="btn-text">添加账号</span>
                </el-button>
                <el-button 
                  @click="fetchAccounts" 
                  :loading="appStore.isAccountRefreshing" 
                  class="secondary-action-btn"
                  size="large"
                >
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span class="btn-text">{{ appStore.isAccountRefreshing ? '刷新中' : '刷新' }}</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredArticleAccounts.length > 0" class="account-list">
              <el-table :data="filteredArticleAccounts" style="width: 100%">
                <el-table-column label="头像" width="70" align="center">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="账号名称" min-width="200">
                  <template #default="scope">
                    <div class="account-name">
                      <span class="name-text">{{ scope.row.name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="platform" label="平台" width="120" align="center">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="light"
                      class="platform-tag"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="120" align="center">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="light"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                      class="status-tag"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="340" align="center">
                  <template #default="scope">
                    <div class="action-buttons-group">
                      <el-button size="small" @click="handleEdit(scope.row)" class="action-btn">
                        <el-icon><Edit /></el-icon>
                        编辑
                      </el-button>
                      <el-button size="small" type="primary" @click="handleDownloadCookie(scope.row)" class="action-btn">
                        <el-icon><Download /></el-icon>
                        下载
                      </el-button>
                      <el-button size="small" type="info" @click="handleUploadCookie(scope.row)" class="action-btn">
                        <el-icon><Upload /></el-icon>
                        上传
                      </el-button>
                      <el-button size="small" type="danger" @click="handleDelete(scope.row)" class="action-btn">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty :description="`暂无${selectedPlatforms.article || '文章'}账号数据`" />
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 视频Tab -->
        <el-tab-pane label="视频" name="video">
          <div class="account-list-container">
            <!-- 筛选选项 -->
            <div class="filter-section">
              <span class="filter-label">平台类型：</span>
              <el-radio-group v-model="selectedPlatforms.video" @change="handlePlatformFilterChange">
                <el-radio 
                  v-for="platform in filterOptions.video" 
                  :key="platform" 
                  :label="platform"
                  class="filter-radio"
                >
                  {{ platform }}
                </el-radio>
              </el-radio-group>
            </div>
            
            <div class="search-toolbar">
              <div class="search-box">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索账号名称、平台..."
                  clearable
                  @clear="handleSearch"
                  @input="handleSearch"
                  class="search-input"
                  size="large"
                >
                  <template #prefix>
                    <el-icon class="search-icon"><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="toolbar-actions">
                <el-button 
                  type="primary" 
                  @click="handleAddAccount('video')" 
                  class="primary-action-btn"
                  size="large"
                >
                  <el-icon><Plus /></el-icon>
                  <span class="btn-text">添加账号</span>
                </el-button>
                <el-button 
                  @click="fetchAccounts" 
                  :loading="appStore.isAccountRefreshing" 
                  class="secondary-action-btn"
                  size="large"
                >
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span class="btn-text">{{ appStore.isAccountRefreshing ? '刷新中' : '刷新' }}</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredVideoAccounts.length > 0" class="account-list">
              <el-table :data="filteredVideoAccounts" style="width: 100%">
                <el-table-column label="头像" width="70" align="center">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="账号名称" min-width="200">
                  <template #default="scope">
                    <div class="account-name">
                      <span class="name-text">{{ scope.row.name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="platform" label="平台" width="120" align="center">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="light"
                      class="platform-tag"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="120" align="center">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="light"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                      class="status-tag"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="340" align="center">
                  <template #default="scope">
                    <div class="action-buttons-group">
                      <el-button size="small" @click="handleEdit(scope.row)" class="action-btn">
                        <el-icon><Edit /></el-icon>
                        编辑
                      </el-button>
                      <el-button size="small" type="primary" @click="handleDownloadCookie(scope.row)" class="action-btn">
                        <el-icon><Download /></el-icon>
                        下载
                      </el-button>
                      <el-button size="small" type="info" @click="handleUploadCookie(scope.row)" class="action-btn">
                        <el-icon><Upload /></el-icon>
                        上传
                      </el-button>
                      <el-button size="small" type="danger" @click="handleDelete(scope.row)" class="action-btn">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty :description="`暂无${selectedPlatforms.video || '视频'}账号数据`" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 添加/编辑账号对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加账号' : '编辑账号'"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="!sseConnecting"
      :show-close="!sseConnecting"
    >
      <el-form :model="accountForm" label-width="80px" :rules="rules" ref="accountFormRef">
        <el-form-item label="平台" prop="platform">
          <el-select 
            v-model="accountForm.platform" 
            placeholder="请选择平台" 
            style="width: 100%"
            :disabled="dialogType === 'edit' || sseConnecting"
          >
            <!-- 根据当前Tab显示对应的平台选项 -->
            <el-option 
              v-for="platform in getAvailablePlatforms(accountForm.contentType)" 
              :key="platform" 
              :label="platform" 
              :value="platform" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input 
            v-model="accountForm.name" 
            placeholder="请输入账号名称" 
            :disabled="sseConnecting"
          />
        </el-form-item>
        
        <!-- Facebook专用字段 -->
        <template v-if="accountForm.platform === 'Facebook'">
          <el-form-item label="账号" prop="facebookAccount">
            <el-input 
              v-model="accountForm.facebookAccount" 
              placeholder="请输入Facebook账号" 
              :disabled="sseConnecting"
            />
          </el-form-item>
          <el-form-item label="密码" prop="facebookPassword">
            <el-input 
              v-model="accountForm.facebookPassword" 
              type="password"
              placeholder="请输入Facebook密码" 
              :disabled="sseConnecting"
              show-password
            />
          </el-form-item>
          <el-form-item label="Token" prop="facebookToken">
            <el-input 
              v-model="accountForm.facebookToken" 
              placeholder="请输入Facebook Token" 
              :disabled="sseConnecting"
            />
          </el-form-item>
        </template>
        
        <!-- 二维码显示区域 -->
        <div v-if="sseConnecting" class="qrcode-container">
          <!-- 视频号登录：等待用户在本地浏览器扫码 -->
          <div v-if="qrCodeData === 'waiting' && !loginStatus" class="local-browser-wrapper">
            <el-icon><Link /></el-icon>
            <p class="local-browser-tip">已在浏览器中打开视频号登录页面</p>
            <p class="local-browser-desc">请在浏览器中扫码登录，登录成功后点击下方按钮</p>
            <el-button 
              type="primary" 
              @click="handleLocalBrowserLogin"
              :loading="localBrowserLogging"
              style="margin-top: 20px;"
            >
              {{ localBrowserLogging ? '验证中...' : '我已登录' }}
            </el-button>
          </div>
          <!-- 其他平台：显示二维码 -->
          <div v-else-if="qrCodeData && qrCodeData !== 'waiting' && !loginStatus && loginStatus !== 'timeout'" class="qrcode-wrapper">
            <p class="qrcode-tip">请使用对应平台APP扫描二维码登录</p>
            <img :src="qrCodeData" alt="登录二维码" class="qrcode-image" />
          <div v-if="accountForm.platform === '视频号' || accountForm.platform === '公众号'">
            <div v-if="qrSessionInfo.sessionId" class="qrcode-session-info">
              <div class="session-row">会话ID: {{ qrSessionInfo.sessionId.slice(0, 8) }}...</div>
              <div v-if="qrSessionInfo.sessionToken" class="session-row">Token: {{ qrSessionInfo.sessionToken.slice(0, 8) }}...</div>
              <div v-if="qrSessionInfo.generatedAt" class="session-row">
                生成时间: {{ new Date(qrSessionInfo.generatedAt * 1000).toLocaleTimeString() }}
              </div>
              <div v-if="qrSessionInfo.expiresIn" class="session-row">
                剩余有效期: {{ qrSessionInfo.remainingSeconds }} 秒
              </div>
              <div class="session-hint">请确保扫描当前二维码，避免过期/错码</div>
            </div>
          </div>
            <p v-if="accountForm.platform === '视频号' || accountForm.platform === '公众号'" class="qrcode-tip" style="margin-top: 10px; color: #909399; font-size: 12px;">
              扫码后，系统会自动检测登录状态。如果长时间无反应，请点击下方"我已扫码并确认"按钮
            </p>
            <el-button 
              v-if="accountForm.platform === '视频号' || accountForm.platform === '公众号'"
              type="primary" 
              @click="handleManualConfirmLogin"
              :loading="manualConfirming"
              style="margin-top: 15px;"
              size="small"
            >
              {{ manualConfirming ? '验证中...' : '我已扫码并确认' }}
            </el-button>
          </div>
          <!-- 超时提示 -->
          <div v-else-if="loginStatus === 'timeout'" class="timeout-wrapper">
            <el-icon><Clock /></el-icon>
            <p class="timeout-tip">登录超时</p>
            <p class="timeout-desc">如果已扫码并确认登录，请点击下方按钮手动完成登录</p>
            <el-button 
              type="primary" 
              @click="handleManualConfirmLogin"
              :loading="manualConfirming"
              style="margin-top: 15px;"
            >
              {{ manualConfirming ? '验证中...' : '我已扫码并确认登录' }}
            </el-button>
          </div>
          <div v-else-if="!qrCodeData && !loginStatus" class="loading-wrapper">
            <el-icon class="is-loading"><Refresh /></el-icon>
            <span>请求中...</span>
          </div>
          <div v-else-if="loginStatus === '200'" class="success-wrapper">
            <el-icon><CircleCheckFilled /></el-icon>
            <span>添加成功</span>
          </div>
          <div v-else-if="loginStatus === '500'" class="error-wrapper">
            <el-icon><CircleCloseFilled /></el-icon>
            <span>添加失败，请稍后再试</span>
          </div>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitAccountForm" 
            :loading="sseConnecting || addingAccountDirect" 
            :disabled="sseConnecting || addingAccountDirect"
          >
            {{ (sseConnecting || addingAccountDirect) ? '请求中' : '确认' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

// 验证定时器（用于清理）
let validationTimer = null
import { Refresh, CircleCheckFilled, CircleCloseFilled, Download, Upload, Loading, Plus, UserFilled, Edit, Delete, Search, Link, Clock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountApi } from '@/api/account'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { buildApiUrl, resolveApiBaseUrl } from '@/utils/apiConfig'

// 获取账号状态管理
const accountStore = useAccountStore()
// 获取应用状态管理
const appStore = useAppStore()

// 当前激活的标签页
const activeTab = ref('video')

// 搜索关键词
const searchKeyword = ref('')

/**
 * 平台到内容类型的映射
 */
const platformToContentType = {
  // 图文平台
  '微信': 'image-text',
  '小红书': 'image-text',
  'X': 'image-text',
  'Facebook': 'image-text',
  'Thread': 'image-text',
  'Instagram': 'image-text',
  'LinkedIn': 'image-text',
  // 文章平台
  '公众号': 'article',
  '掘金': 'article',
  '知乎': 'article',
  '百家号': 'article',
  'CSND': 'article',
  'Medium': 'article',
  // 视频平台
  '快手': 'video',
  '抖音': 'video',
  '视频号': 'video',
  '小红书': 'video' // 小红书同时支持视频
}

/**
 * 默认筛选选项
 */
const defaultFilterOptions = {
  'image-text': ['公众号', '小红书', 'X', 'FaceBook', 'Thread', 'Instagram'],
  'article': ['公众号', 'Medium', '知乎', '掘金', 'CSND', '百家号'],
  'video': ['快手', '抖音', '视频号', '小红书']
}

/**
 * 从localStorage加载筛选选项，如果没有则使用默认值
 */
const loadFilterOptions = () => {
  const stored = localStorage.getItem('accountFilterOptions')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      // 检查是否有空数组的情况，如果有则清除并重新使用默认值
      const hasEmptyArray = 
        (parsed['image-text'] && Array.isArray(parsed['image-text']) && parsed['image-text'].length === 0) ||
        (parsed['article'] && Array.isArray(parsed['article']) && parsed['article'].length === 0) ||
        (parsed['video'] && Array.isArray(parsed['video']) && parsed['video'].length === 0)
      
      if (hasEmptyArray) {
        // 如果发现空数组，清除localStorage并使用默认值
        console.log('检测到空数组，清除localStorage并使用默认筛选选项')
        localStorage.removeItem('accountFilterOptions')
        return { ...defaultFilterOptions }
      }
      
      // 合并默认选项和存储的选项，确保默认选项存在
      // 如果存储的选项为空数组或不存在，则使用默认值
      return {
        'image-text': (parsed['image-text'] && Array.isArray(parsed['image-text']) && parsed['image-text'].length > 0) 
          ? [...new Set([...defaultFilterOptions['image-text'], ...parsed['image-text']])]
          : defaultFilterOptions['image-text'],
        'article': (parsed['article'] && Array.isArray(parsed['article']) && parsed['article'].length > 0)
          ? [...new Set([...defaultFilterOptions['article'], ...parsed['article']])]
          : defaultFilterOptions['article'],
        'video': (parsed['video'] && Array.isArray(parsed['video']) && parsed['video'].length > 0)
          ? [...new Set([...defaultFilterOptions['video'], ...parsed['video']])]
          : defaultFilterOptions['video']
      }
    } catch (e) {
      console.error('加载筛选选项失败:', e)
      // 清除损坏的数据
      localStorage.removeItem('accountFilterOptions')
      return { ...defaultFilterOptions }
    }
  }
  return { ...defaultFilterOptions }
}

/**
 * 保存筛选选项到localStorage
 */
const saveFilterOptions = () => {
  try {
    localStorage.setItem('accountFilterOptions', JSON.stringify(filterOptions.value))
  } catch (e) {
    console.error('保存筛选选项失败:', e)
  }
}

// 筛选选项（支持动态添加）
const filterOptions = ref(loadFilterOptions())
console.log('filterOptions....', filterOptions.value)

// 当前选中的平台（每个Tab一个）
const selectedPlatforms = reactive({
  'image-text': filterOptions.value['image-text']?.includes('公众号') ? '公众号' : (filterOptions.value['image-text']?.[0] || ''),
  'article': filterOptions.value['article']?.includes('公众号') ? '公众号' : (filterOptions.value['article']?.[0] || ''),
  'video': filterOptions.value['video']?.[0] || ''
})

/**
 * 自动识别并添加新平台到筛选选项
 */
const autoAddPlatformsToFilters = (accounts) => {
  accounts.forEach(account => {
    const platform = account.platform
    if (platform) {
      const contentType = platformToContentType[platform]
      if (contentType && !filterOptions.value[contentType]?.includes(platform)) {
        addPlatformToFilter(platform, contentType)
      }
    }
  })
  
  // 确保每个Tab都有一个选中的平台（如果没有选中，则选择第一个可用的）
  ['image-text', 'article', 'video'].forEach(contentType => {
    if (!selectedPlatforms[contentType] && filterOptions.value[contentType]?.length > 0) {
      selectedPlatforms[contentType] = filterOptions.value[contentType][0]
    }
  })
}

// 获取账号数据（快速，不验证）
const fetchAccountsQuick = async () => {
  try {
    const res = await accountApi.getAccounts()
    if (res.code === 200 && res.data && res.data.length > 0) {
      // 后端返回的是对象格式 {id, type, filePath, userName, status}
      // 直接调用 setAccounts，它会处理对象格式
      accountStore.setAccounts(res.data);
      
      // 将所有账号的状态暂时设为"验证中"（覆盖setAccounts转换的状态）
      // 使用 nextTick 确保响应式更新
      await nextTick();
      accountStore.accounts.forEach(account => {
        account.status = '验证中';
      });
      
      // 自动识别并添加新平台到筛选选项
      const formattedAccounts = accountStore.accounts
      autoAddPlatformsToFilters(formattedAccounts)
    } else if (res.code === 200 && (!res.data || res.data.length === 0)) {
      // 数据为空，清空账号列表
      accountStore.setAccounts([]);
    }
  } catch (error) {
    console.error('快速获取账号数据失败:', error)
  }
}

// 获取账号数据（带验证）
const fetchAccounts = async () => {
  if (appStore.isAccountRefreshing) return

  appStore.setAccountRefreshing(true)

  try {
    const res = await accountApi.getValidAccounts()
    if (res.code === 200 && res.data) {
      accountStore.setAccounts(res.data)
      
      // 自动识别并添加新平台到筛选选项
      autoAddPlatformsToFilters(accountStore.accounts)
      
      ElMessage.success('账号数据获取成功')
      // 标记为已访问
      if (appStore.isFirstTimeAccountManagement) {
        appStore.setAccountManagementVisited()
      }
    } else {
      ElMessage.error('获取账号数据失败')
    }
  } catch (error) {
    console.error('获取账号数据失败:', error)
    ElMessage.error('获取账号数据失败')
  } finally {
    appStore.setAccountRefreshing(false)
  }
}

// 后台验证所有账号（优化版本，使用setTimeout避免阻塞UI）
const validateAllAccountsInBackground = async () => {
  // 清除之前的定时器（如果存在）
  if (validationTimer) {
    clearTimeout(validationTimer)
  }
  
  // 使用setTimeout将验证过程放在下一个事件循环，避免阻塞UI
  validationTimer = setTimeout(async () => {
    try {
      console.log('开始后台验证账号...')
      const res = await accountApi.getValidAccounts()
      if (res.code === 200 && res.data) {
        accountStore.setAccounts(res.data)
        console.log('账号验证完成')
      }
    } catch (error) {
      console.error('后台验证账号失败:', error)
    } finally {
      validationTimer = null
    }
  }, 0)
}

// 页面加载时获取账号数据
onMounted(() => {
  // 确保初始化时选中第一个平台
  if (!selectedPlatforms['image-text'] && filterOptions.value['image-text']?.length > 0) {
    // 优先选择公众号，如果没有则选择第一个
    selectedPlatforms['image-text'] = filterOptions.value['image-text'].includes('公众号') 
      ? '公众号' 
      : filterOptions.value['image-text'][0]
  }
  if (!selectedPlatforms['article'] && filterOptions.value['article']?.length > 0) {
    // 优先选择公众号，如果没有则选择第一个
    selectedPlatforms['article'] = filterOptions.value['article'].includes('公众号') 
      ? '公众号' 
      : filterOptions.value['article'][0]
  }
  if (!selectedPlatforms['video'] && filterOptions.value['video']?.length > 0) {
    // 优先选择第一个平台（可能是快手、抖音、视频号或小红书）
    selectedPlatforms['video'] = filterOptions.value['video'][0]
  }
  
  // 快速获取账号列表（不验证），立即显示
  fetchAccountsQuick()

  // 延迟验证，避免首屏卡顿（5秒后再验证，给用户足够时间看到内容）
  // 如果用户在这之前离开了页面，验证会被取消
  setTimeout(() => {
    validateAllAccountsInBackground()
  }, 5000) // 延迟5秒，确保首屏完全加载后再验证
})

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  const typeMap = {
    '快手': 'success',
    '抖音': 'danger',
    '视频号': 'warning',
    '小红书': 'info',
    'Facebook': 'primary'
  }
  return typeMap[platform] || 'info'
}

// 判断状态是否可点击（异常状态可点击）
const isStatusClickable = (status) => {
  return status === '异常'; // 只有异常状态可点击，验证中不可点击
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  if (status === '验证中') {
    return 'info'; // 验证中使用灰色
  } else if (status === '正常') {
    return 'success'; // 正常使用绿色
  } else {
    return 'danger'; // 无效使用红色
  }
}

// 处理状态点击事件
const handleStatusClick = (row) => {
  if (isStatusClickable(row.status)) {
    // 触发重新登录流程
    handleReLogin(row)
  }
}

/**
 * 基础过滤后的账号列表（仅搜索关键词）
 */
const baseFilteredAccounts = computed(() => {
  if (!searchKeyword.value) return accountStore.accounts
  return accountStore.accounts.filter(account =>
    account.name.includes(searchKeyword.value) || account.platform.includes(searchKeyword.value)
  )
})

/**
 * 根据内容类型和选中的平台过滤账号
 */
const getAccountsByContentType = (contentType) => {
  const selectedPlatform = selectedPlatforms[contentType]
  
  // 如果没有选中平台，但有账号，尝试显示属于该内容类型的所有账号
  if (!selectedPlatform) {
    return baseFilteredAccounts.value.filter(account => {
      const accountContentType = platformToContentType[account.platform]
      return accountContentType === contentType
    })
  }
  
  return baseFilteredAccounts.value.filter(account => {
    // 首先检查平台是否匹配
    if (account.platform !== selectedPlatform) return false
    
    // 特殊处理：小红书同时支持图文和视频
    if (account.platform === '小红书') {
      // 在视频Tab中，如果选中的是小红书，则显示小红书账号
      if (contentType === 'video' && selectedPlatform === '小红书') {
        return true
      }
      // 在图文Tab中，如果选中的是小红书，则显示小红书账号
      if (contentType === 'image-text' && selectedPlatform === '小红书') {
        return true
      }
    }
    
    // 然后检查平台是否属于当前内容类型
    const accountContentType = platformToContentType[account.platform]
    return accountContentType === contentType
  })
}

// 图文账号列表
const filteredImageTextAccounts = computed(() => {
  return getAccountsByContentType('image-text')
})

// 文章账号列表
const filteredArticleAccounts = computed(() => {
  return getAccountsByContentType('article')
})

// 视频账号列表
const filteredVideoAccounts = computed(() => {
  return getAccountsByContentType('video')
})

/**
 * 处理平台筛选变化
 */
const handlePlatformFilterChange = () => {
  // 筛选逻辑已通过计算属性实现，这里可以添加其他逻辑
}

/**
 * 获取可用的平台列表（根据内容类型）
 * @param {string} contentType - 内容类型
 * @returns {string[]} 平台列表
 */
const getAvailablePlatforms = (contentType) => {
  if (!contentType) {
    // 如果没有指定内容类型，返回所有平台
    return [
      ...defaultFilterOptions['image-text'],
      ...defaultFilterOptions['article'],
      ...defaultFilterOptions['video']
    ]
  }
  
  // 返回对应内容类型的平台列表（包括动态添加的）
  return filterOptions.value[contentType] || []
}

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已通过计算属性实现
}

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' 或 'edit'
const accountFormRef = ref(null)

// 账号表单
const accountForm = reactive({
  id: null,
  name: '',
  platform: '',
  status: '正常',
  contentType: '', // 内容类型（image-text/article/video）
  automationTool: 'playwright', // 自动化框架：'playwright'（默认）或 'selenium'
  facebookAccount: '', // Facebook账号
  facebookPassword: '', // Facebook密码
  facebookToken: '' // Facebook Token
})

// 表单验证规则
const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  name: [{ required: true, message: '请输入账号名称', trigger: 'blur' }]
}

// SSE连接状态
const sseConnecting = ref(false)
const qrCodeData = ref('')
const qrSessionInfo = reactive({
  sessionId: '',
  sessionToken: '',
  generatedAt: 0,
  expiresIn: 0,
  remainingSeconds: 0,
})
const currentAutomationTool = ref('playwright')
let qrCountdownTimer = null
let autoRefreshTimer = null
const loginStatus = ref('')
const localBrowserLogging = ref(false) // 本地浏览器登录状态
const currentLoginPlatform = ref('') // 当前登录的平台
const currentLoginName = ref('') // 当前登录的账号名
const addingAccountDirect = ref(false) // 直接添加账号的loading状态
const manualConfirming = ref(false) // 手动确认登录状态

/**
 * 添加账号
 * @param {string} contentType - 内容类型（image-text/article/video）
 */
const handleAddAccount = (contentType) => {
  dialogType.value = 'add'
  Object.assign(accountForm, {
    id: null,
    name: '',
    platform: '',
    status: '正常',
    contentType: contentType, // 保存内容类型，用于后续处理
    automationTool: 'playwright', // 默认使用 Playwright
    facebookAccount: '',
    facebookPassword: '',
    facebookToken: ''
  })
  // 重置SSE状态
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''
  dialogVisible.value = true
}

/**
 * 添加新平台到筛选选项
 * @param {string} platform - 平台名称
 * @param {string} contentType - 内容类型
 * @param {boolean} autoSelect - 是否自动选中（默认false）
 */
const addPlatformToFilter = (platform, contentType, autoSelect = false) => {
  if (!filterOptions.value[contentType]?.includes(platform)) {
    filterOptions.value[contentType].push(platform)
    saveFilterOptions()
    // 如果指定自动选中，且当前Tab是该内容类型，则选中新添加的平台
    if (autoSelect && activeTab.value === contentType) {
      selectedPlatforms[contentType] = platform
    }
  }
}

// 编辑账号
const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(accountForm, {
    id: row.id,
    name: row.name,
    platform: row.platform,
    status: row.status,
    facebookAccount: row.facebookAccount || '',
    facebookPassword: row.facebookPassword || '',
    facebookToken: row.facebookToken || ''
  })
  dialogVisible.value = true
}

// 删除账号
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除账号 ${row.name} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // 调用API删除账号
        const response = await accountApi.deleteAccount(row.id)

        if (response.code === 200) {
          // 从状态管理中删除账号
          accountStore.deleteAccount(row.id)
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        } else {
          ElMessage.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除账号失败:', error)
        ElMessage.error('删除账号失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// 下载Cookie文件
const handleDownloadCookie = (row) => {
  // 使用统一的工具函数构建 API URL
  const downloadUrl = buildApiUrl(`/downloadCookie?filePath=${encodeURIComponent(row.filePath)}`)

  // 创建一个隐藏的链接来触发下载
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = `${row.name}_cookie.json`
  link.target = '_blank'
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 上传Cookie文件
const handleUploadCookie = (row) => {
  // 创建一个隐藏的文件输入框
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.style.display = 'none'
  document.body.appendChild(input)

  input.onchange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // 检查文件类型
    if (!file.name.endsWith('.json')) {
      ElMessage.error('请选择JSON格式的Cookie文件')
      document.body.removeChild(input)
      return
    }

    try {
      // 创建FormData对象
      const formData = new FormData()
      formData.append('file', file)
      formData.append('id', row.id)
      formData.append('platform', row.platform)

      // 发送上传请求 - 使用统一的工具函数
      const uploadUrl = buildApiUrl('/uploadCookie')
      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (result.code === 200) {
        ElMessage.success('Cookie文件上传成功')
        // 刷新账号列表以显示更新
        fetchAccounts()
      } else {
        ElMessage.error(result.msg || 'Cookie文件上传失败')
      }
    } catch (error) {
      console.error('上传Cookie文件失败:', error)
      ElMessage.error('Cookie文件上传失败')
    } finally {
      document.body.removeChild(input)
    }
  }

  input.click()
}

// 处理从登录流程收到的Cookie数据
const handleSaveCookieFromLogin = async (cookieData) => {
  try {
    console.log('[前端] 收到Cookie数据，准备保存...', cookieData)
    
    // Cookie已经在后端保存到服务器了，这里只是记录日志
    // 如果需要，也可以在这里做额外的处理（比如验证、下载等）
    console.log('[前端] Cookie已由后端保存到服务器:', cookieData.filePath)
    
    // 可选：将cookie数据保存到localStorage作为备份
    try {
      const cookieBackup = {
        userName: cookieData.userName,
        filePath: cookieData.filePath,
        cookies: cookieData.cookies,
        timestamp: new Date().toISOString()
      }
      localStorage.setItem(`cookie_backup_${cookieData.userName}`, JSON.stringify(cookieBackup))
      console.log('[前端] Cookie已备份到localStorage')
    } catch (e) {
      console.warn('[前端] Cookie备份到localStorage失败:', e)
    }
  } catch (error) {
    console.error('[前端] 处理Cookie数据失败:', error)
    // 不显示错误，因为登录已经成功，cookie已经在后端保存
  }
}

// 重新登录账号
const handleReLogin = (row) => {
  // 设置表单信息
  dialogType.value = 'edit'
  Object.assign(accountForm, {
    id: row.id,
    name: row.name,
    platform: row.platform,
    status: row.status
  })

  // 重置SSE状态
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''

  // 显示对话框
  dialogVisible.value = true

  // 立即开始登录流程
  setTimeout(() => {
    connectSSE(row.platform, row.name)
  }, 300)
}

// 手动确认登录（用于视频号等需要手动确认的平台）
const handleManualConfirmLogin = async () => {
  if (!currentLoginPlatform.value || !currentLoginName.value) {
    ElMessage.error('登录信息不完整，请重新开始登录流程')
    return
  }

  manualConfirming.value = true
  try {
    // 调用后端API手动确认登录
    const platformTypeMap = {
      '小红书': 1,
      '视频号': 2,
      '公众号': 2,
      '抖音': 3,
      '快手': 4
    }
    const type = platformTypeMap[currentLoginPlatform.value] || 2

    const response = await fetch(`${resolveApiBaseUrl()}/manualConfirmLogin?type=${type}&id=${encodeURIComponent(currentLoginName.value)}`, {
      method: 'POST'
    })
    const result = await response.json()

    if (result.code === 200) {
      ElMessage.success('登录确认成功')
      loginStatus.value = '200'
      
      // 关闭SSE连接
      closeSSEConnection()
      
      // 延迟关闭对话框并刷新
      setTimeout(() => {
        dialogVisible.value = false
        sseConnecting.value = false
        fetchAccountsQuick().then(() => {
          if (accountForm.platform) {
            const contentType = platformToContentType[accountForm.platform]
            if (contentType) {
              activeTab.value = contentType
              selectedPlatforms[contentType] = accountForm.platform
            }
          }
        })
      }, 1000)
    } else {
      ElMessage.error(result.msg || '登录确认失败，请检查是否已扫码并确认')
    }
  } catch (error) {
    console.error('手动确认登录失败:', error)
    ElMessage.error('登录确认失败，请稍后重试')
  } finally {
    manualConfirming.value = false
  }
}

// 获取默认头像
const getDefaultAvatar = (name) => {
  // 使用简单的默认头像，可以基于用户名生成不同的颜色
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`
}

// SSE事件源对象
let eventSource = null

// 关闭SSE连接
const closeSSEConnection = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

// 建立SSE连接
const clearQrTimers = () => {
  if (qrCountdownTimer) {
    clearInterval(qrCountdownTimer)
    qrCountdownTimer = null
  }
  if (autoRefreshTimer) {
    clearTimeout(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

const startQrCountdown = (generatedAt, expiresIn) => {
  clearQrTimers()
  if (!generatedAt || !expiresIn) return
  const updateRemaining = () => {
    const elapsed = Math.floor(Date.now() / 1000 - generatedAt)
    const remaining = Math.max(0, expiresIn - elapsed)
    qrSessionInfo.remainingSeconds = remaining
  }
  updateRemaining()
  qrCountdownTimer = setInterval(updateRemaining, 1000)
}

const connectSSE = (platform, name, automationTool = 'playwright') => {
  // 添加调试日志
  console.log('[前端] 建立SSE连接 - 平台:', platform, '账号名称:', name, '自动化框架:', automationTool)
  console.log('[前端] 账号名称原始值:', JSON.stringify(name))
  console.log('[前端] 账号名称编码后:', encodeURIComponent(name))
  
  // 关闭可能存在的连接
  closeSSEConnection()
  clearQrTimers()

  // 设置连接状态
  sseConnecting.value = true
  qrCodeData.value = ''
  loginStatus.value = ''
  currentLoginPlatform.value = platform
  currentLoginName.value = name
  currentAutomationTool.value = automationTool || 'playwright'
  qrSessionInfo.sessionId = ''
  qrSessionInfo.sessionToken = ''
  qrSessionInfo.generatedAt = 0
  qrSessionInfo.expiresIn = 0
  qrSessionInfo.remainingSeconds = 0

  // 获取平台类型编号
  // 1 小红书 2 视频号 3 抖音 4 快手
  // 公众号使用视频号的登录方式（都是微信生态）
  const platformTypeMap = {
    '小红书': '1',
    '视频号': '2',
    '公众号': '2', // 公众号使用视频号的登录方式
    '抖音': '3',
    '快手': '4'
  }

  const type = platformTypeMap[platform] || '1'

  // 视频号登录：使用服务器端浏览器（非headless）进行登录
  // 这样cookie可以保存在服务器上
  // 后端会在服务器端打开浏览器，获取二维码，通过SSE发送给前端显示
  // 用户在手机上扫码后，服务器端浏览器会自动检测登录状态并保存cookie
  if (type === '2') {
    console.log('[前端] 视频号登录，使用服务器端浏览器（cookie将保存在服务器）...')
    console.log('[前端] 使用的自动化框架:', automationTool.toUpperCase())
    // 继续使用原有的SSE流程
    // 后端会在服务器端打开浏览器（根据LOCAL_CHROME_HEADLESS配置决定是否headless）
    // 获取二维码后通过SSE发送给前端显示
    // 用户扫码后，服务器端浏览器会自动检测登录并保存cookie到服务器
  }

  // 创建SSE连接 - 使用统一的工具函数（其他平台保持原有逻辑）
  const apiBaseUrl = resolveApiBaseUrl()
  // 对于视频号，添加 automationTool 参数
  let url = `${apiBaseUrl}/login?type=${type}&id=${encodeURIComponent(name)}`
  if (type === '2' && automationTool) {
    url += `&automation_tool=${automationTool}`
  }
  console.log('[前端] SSE连接URL:', url)

  eventSource = new EventSource(url)

  // 监听连接打开
  eventSource.onopen = (event) => {
    console.log('[前端] SSE连接已打开', event)
    console.log('[前端] EventSource readyState:', eventSource.readyState)
  }

  // 二维码防缓存：为URL型二维码追加时间戳
  const enhanceQrSrc = (src) => {
    if (!src) return ''
    if (src.startsWith('data:')) return src
    const separator = src.includes('?') ? '&' : '?'
    return `${src}${separator}_t=${Date.now()}`
  }

  // 监听消息
  eventSource.onmessage = (event) => {
    const data = event.data
    console.log('[前端] 收到SSE消息:', data)
    console.log('[前端] 消息类型:', typeof data, '消息长度:', data.length)

    // 处理Cookie数据（格式：cookie:JSON数据）
    if (data.startsWith('cookie:')) {
      try {
        const cookieJson = data.substring(7) // 去掉 'cookie:' 前缀
        const cookieData = JSON.parse(cookieJson)
        console.log('[前端] 收到Cookie数据:', cookieData)
        
        // 保存Cookie到服务器
        handleSaveCookieFromLogin(cookieData)
        
        // 可选：也可以下载Cookie到本地
        // handleDownloadCookieFromLogin(cookieData)
        
        return
      } catch (error) {
        console.error('[前端] 解析Cookie数据失败:', error)
        // 即使解析失败，也继续流程
      }
    }

    // 处理二维码payload（新格式：qrcode:{...}）
    if (data.startsWith('qrcode:')) {
      try {
        const payloadStr = data.substring(7)
        const payload = JSON.parse(payloadStr)
        console.log('[前端] 收到二维码payload:', payload)

        if (payload.qrCode) {
          qrCodeData.value = enhanceQrSrc(payload.qrCode)
        }
        qrSessionInfo.sessionId = payload.sessionId || ''
        qrSessionInfo.sessionToken = payload.sessionToken || ''
        qrSessionInfo.generatedAt = payload.generatedAt ? Math.floor(payload.generatedAt) : 0
        qrSessionInfo.expiresIn = payload.expiresIn || 0
        qrSessionInfo.remainingSeconds = payload.expiresIn || 0
        if (qrSessionInfo.generatedAt && qrSessionInfo.expiresIn) {
          startQrCountdown(qrSessionInfo.generatedAt, qrSessionInfo.expiresIn)
        }
        return
      } catch (e) {
        console.error('[前端] 解析二维码payload失败，尝试按旧格式处理:', e)
      }
    }

    // 处理状态消息（格式：status:消息内容）
    if (data.startsWith('status:')) {
      const statusMsg = data.replace('status:', '')
      console.log('[前端] 收到状态消息:', statusMsg)
      return
    }

    // 处理超时消息
    if (data === 'timeout') {
      console.log('[前端] 登录超时，显示手动确认选项')
      loginStatus.value = 'timeout'
      // 自动刷新二维码（仅视频号）
      if (currentLoginPlatform.value === '视频号' && currentLoginName.value) {
        if (!autoRefreshTimer) {
          autoRefreshTimer = setTimeout(() => {
            console.log('[前端] 超时自动刷新二维码')
            qrCodeData.value = ''
            loginStatus.value = ''
            connectSSE(currentLoginPlatform.value, currentLoginName.value, currentAutomationTool.value)
          }, 1500)
        }
      }
      return
    }

    // 如果还没有二维码数据，且数据长度较长，认为是二维码（旧格式兼容）
    if (!qrCodeData.value && data.length > 100) {
      try {
        if (data.startsWith('http')) {
          qrCodeData.value = enhanceQrSrc(data)
        } else if (data.startsWith('data:image')) {
          qrCodeData.value = data
        } else {
          qrCodeData.value = `data:image/png;base64,${data}`
        }
        console.log('设置二维码数据，长度:', data.length)
      } catch (error) {
        console.error('处理二维码数据出错:', error)
      }
    }
    // 如果收到状态码
    else if (data === '200' || data === '500') {
      console.log('[前端] 收到登录状态码:', data)
      loginStatus.value = data

      // 如果登录成功
      if (data === '200') {
        console.log('[前端] 登录成功，准备关闭连接和更新UI')
        setTimeout(() => {
          // 关闭连接
          closeSSEConnection()

          // 1秒后关闭对话框并开始刷新
          setTimeout(() => {
            dialogVisible.value = false
            sseConnecting.value = false

            // 根据是否是重新登录显示不同提示
            ElMessage.success(dialogType.value === 'edit' ? '重新登录成功' : '账号添加成功')

            // 优化：先快速获取账号列表（不验证），立即显示新添加的账号
            fetchAccountsQuick().then(() => {
              // 然后在后台异步验证所有账号，不阻塞UI
              ElMessage({
                type: 'info',
                message: '账号已添加，正在后台验证账号状态...',
                duration: 3000
              })
              
              // 后台验证，不阻塞用户操作
              validateAllAccountsInBackground()
              
              // 如果添加了新平台，确保切换到对应的Tab并选中该平台
              if (accountForm.platform) {
                const contentType = platformToContentType[accountForm.platform]
                if (contentType) {
                  activeTab.value = contentType
                  selectedPlatforms[contentType] = accountForm.platform
                }
              }
            })
          }, 1000)
        }, 1000)
      } else {
        // 登录失败，关闭连接
        closeSSEConnection()

        // 显示失败提示
        ElMessage.error('登录失败，可能是超时或网络问题，请重试')

        // 2秒后重置状态，允许重试
        setTimeout(() => {
          sseConnecting.value = false
          qrCodeData.value = ''
          loginStatus.value = ''
        }, 2000)
      }
    }
  }

  // 监听错误
  eventSource.onerror = (error) => {
    console.error('[前端] SSE连接错误:', error)
    console.log('[前端] EventSource readyState:', eventSource.readyState)
    console.log('[前端] EventSource URL:', eventSource.url)
    
    // EventSource readyState:
    // 0 = CONNECTING (正在连接)
    // 1 = OPEN (连接已打开)
    // 2 = CLOSED (连接已关闭)
    
    // 延迟处理错误，避免在连接建立过程中误报
    setTimeout(() => {
      // 如果连接已经关闭（readyState === 2）
      if (eventSource && eventSource.readyState === EventSource.CLOSED) {
        console.log('[前端] SSE连接已关闭')
        // 如果还没有收到状态码，可能是连接异常关闭
        if (!loginStatus.value && sseConnecting.value) {
          console.warn('[前端] 连接关闭但未收到状态码，可能是异常关闭')
          ElMessage.error('连接已断开，请重试')
          closeSSEConnection()
          sseConnecting.value = false
        }
      } 
      // 如果正在连接（readyState === 0），可能是连接失败
      else if (eventSource && eventSource.readyState === EventSource.CONNECTING) {
        console.error('[前端] SSE连接失败，无法建立连接')
        ElMessage.error('连接服务器失败，请检查网络连接')
        closeSSEConnection()
        sseConnecting.value = false
      }
      // 如果连接已打开但出现错误（readyState === 1），可能是网络问题
      else if (eventSource && eventSource.readyState === EventSource.OPEN) {
        console.warn('[前端] SSE连接打开但出现错误，可能是网络波动')
        // 不立即关闭，等待重连或后续消息
      }
      // 其他情况
      else if (eventSource && sseConnecting.value) {
        console.error('[前端] SSE连接出现未知错误')
        ElMessage.error('连接服务器失败，请稍后再试')
        closeSSEConnection()
        sseConnecting.value = false
      }
    }, 1000) // 延迟1秒处理，避免误报
  }
}

// 提交账号表单
const submitAccountForm = () => {
  accountFormRef.value.validate(async (valid) => {
    if (valid) {
      if (dialogType.value === 'add') {
        // 添加调试日志
        console.log('[前端] 提交账号表单 - 平台:', accountForm.platform, '账号名称:', accountForm.name)
        console.log('[前端] 账号名称值:', JSON.stringify(accountForm.name))
        
        // 如果添加了新平台，且该平台不在当前内容类型的筛选选项中，则添加到筛选选项
        const contentType = accountForm.contentType || platformToContentType[accountForm.platform]
        if (contentType && accountForm.platform) {
          // 检查平台是否在筛选选项中
          if (!filterOptions.value[contentType]?.includes(accountForm.platform)) {
            addPlatformToFilter(accountForm.platform, contentType)
          }
        }
        
        // 统一使用扫码登录方式：建立SSE连接（传递自动化框架选择）
        connectSSE(accountForm.platform, accountForm.name, accountForm.automationTool)
      } else {
        // 编辑账号逻辑
        try {
          // 将平台名称转换为类型数字
          const platformTypeMap = {
            '快手': 1,
            '抖音': 2,
            '视频号': 3,
            '小红书': 4
          };
          const type = platformTypeMap[accountForm.platform] || 1;

          const res = await accountApi.updateAccount({
            id: accountForm.id,
            type: type,
            userName: accountForm.name
          })
          if (res.code === 200) {
            // 更新状态管理中的账号
            const updatedAccount = {
              id: accountForm.id,
              name: accountForm.name,
              platform: accountForm.platform,
              status: accountForm.status // Keep the existing status
            };
            accountStore.updateAccount(accountForm.id, updatedAccount)
            ElMessage.success('更新成功')
            dialogVisible.value = false
            // 刷新账号列表
            fetchAccounts()
          } else {
            ElMessage.error(res.msg || '更新账号失败')
          }
        } catch (error) {
          console.error('更新账号失败:', error)
          ElMessage.error('更新账号失败')
        }
      }
    } else {
      return false
    }
  })
}

// 组件卸载前关闭SSE连接
onBeforeUnmount(() => {
  closeSSEConnection()
  clearQrTimers()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.account-management {
  min-height: 100%;
  animation: fadeIn 0.6s ease-out;
  
  .account-tabs {
    background-color: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .account-tabs-nav {
      padding: 20px;
    }
  }
  
  .account-list-container {
    .filter-section {
      margin-bottom: 20px;
      padding: 16px 24px;
      background: linear-gradient(135deg, #f8f9ff 0%, #fafbff 100%);
      border-radius: 12px;
      border: 1px solid rgba(102, 126, 234, 0.1);
      display: flex;
      align-items: center;
      gap: 12px;
      
      .filter-label {
        font-size: 14px;
        font-weight: 500;
        color: #475569;
        white-space: nowrap;
      }
      
      :deep(.el-radio-group) {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }
      
      .filter-radio {
        margin-right: 0;
        padding: 8px 16px;
        border-radius: 8px;
        background: white;
        border: 1.5px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        
        :deep(.el-radio__label) {
          font-weight: 500;
          color: #64748b;
          padding-left: 8px;
        }
        
        :deep(.el-radio__input.is-checked .el-radio__inner) {
          background-color: #667eea;
          border-color: #667eea;
        }
        
        &:hover {
          border-color: #667eea;
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
        }
        
        &.is-checked {
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.08) 100%);
          border-color: #667eea;
          
          :deep(.el-radio__label) {
            color: #667eea;
            font-weight: 600;
          }
        }
      }
    }
    
    .search-toolbar {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 24px;
      padding: 24px;
      background: white;
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      border: 1px solid rgba(102, 126, 234, 0.08);
      
      .search-box {
        flex: 1;
        max-width: 500px;
        
        .search-input {
          :deep(.el-input__wrapper) {
            background: linear-gradient(135deg, #f8f9ff 0%, #fafbff 100%);
            border: 2px solid rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 4px 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            
            &:hover {
              background: white;
              border-color: rgba(102, 126, 234, 0.3);
              box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
            }
            
            &.is-focus {
              background: white;
              border-color: #667eea;
              box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }
            
            .el-input__inner {
              font-size: 15px;
              color: #1e293b;
              font-weight: 500;
              
              &::placeholder {
                color: #94a3b8;
                font-weight: 400;
              }
            }
          }
          
          .search-icon {
            font-size: 18px;
            color: #667eea;
          }
        }
      }
      
      .toolbar-actions {
        display: flex;
        gap: 8px;
        
        .el-button {
          border-radius: 8px;
          font-weight: 600;
          padding: 0 20px;
          height: 36px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          border: 2px solid transparent;
          font-size: 13px;
          letter-spacing: 0.2px;
          
          .el-icon {
            font-size: 14px;
            margin-right: 6px;
            
            &.is-loading {
              animation: rotate 1s linear infinite;
            }
          }
          
          .btn-text {
            font-weight: 600;
          }
          
          &.primary-action-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
            
            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
              opacity: 0.92;
            }
            
            &:active {
              transform: translateY(0);
            }
          }
          
          &.secondary-action-btn {
            background: white;
            border: 1.5px solid rgba(102, 126, 234, 0.2);
            color: #667eea;
            
            &:hover {
              background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
              border-color: #667eea;
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
            }
            
            &:active {
              transform: translateY(0);
            }
            
            &.is-loading {
              border-color: #667eea;
              background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
            }
          }
        }
      }
    }
    
    .account-list {
      margin-bottom: 20px;
    }
    
    .empty-data {
      padding: 40px 0;
    }
  }
  
  // 二维码容器样式
  .clickable-status {
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
    }
  }

  .qrcode-container {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 250px;
    
    .qrcode-wrapper {
      text-align: center;
      
      .qrcode-session-info {
        margin-top: 8px;
        font-size: 12px;
        color: #606266;
        .session-row {
          margin-top: 4px;
        }
        .session-hint {
          margin-top: 6px;
          color: #909399;
        }
      }
      
      .qrcode-tip {
        margin-bottom: 15px;
        color: #606266;
      }
      
      .qrcode-image {
        max-width: 200px;
        max-height: 200px;
        border: 1px solid #ebeef5;
        background-color: black;
      }
    }
    
    .loading-wrapper, .success-wrapper, .error-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      
      .el-icon {
        font-size: 48px;
        
        &.is-loading {
          animation: rotate 1s linear infinite;
        }
      }
      
      span {
        font-size: 16px;
      }
    }
    
    .success-wrapper .el-icon {
      color: #67c23a;
    }
    
    .error-wrapper .el-icon {
      color: #f56c6c;
    }
  }
  
  // 表格样式优化
  :deep(.el-table) {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    
    .el-table__header {
      th {
        background: linear-gradient(135deg, #f8f9ff 0%, #f5f7ff 100%);
        color: #64748b;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 18px 12px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.1);
      }
    }
    
    .el-table__body {
      tr {
        transition: all 0.2s ease;
        
        &:hover {
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.01) 100%);
        }
        
        td {
          padding: 16px 12px;
          border-bottom: 1px solid rgba(0, 0, 0, 0.04);
        }
      }
      
      // 账号名称样式
      .account-name {
        display: flex;
        align-items: center;
        
        .name-text {
          font-size: 14px;
          font-weight: 500;
          color: #1e293b;
        }
      }
      
      // 平台标签样式
      .platform-tag {
        font-weight: 600;
        font-size: 13px;
        padding: 6px 14px;
        border-radius: 8px;
        
        &.el-tag--success {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.08) 100%);
          color: #059669;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        &.el-tag--info {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.08) 100%);
          color: #2563eb;
          border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        &.el-tag--warning {
          background: linear-gradient(135deg, rgba(251, 146, 60, 0.1) 0%, rgba(249, 115, 22, 0.08) 100%);
          color: #ea580c;
          border: 1px solid rgba(251, 146, 60, 0.2);
        }
      }
      
      // 状态标签样式
      .status-tag {
        font-weight: 600;
        font-size: 13px;
        padding: 6px 14px;
        border-radius: 8px;
        
        &.el-tag--success {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.08) 100%);
          color: #059669;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        &.el-tag--danger {
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.08) 100%);
          color: #dc2626;
          border: 1px solid rgba(239, 68, 68, 0.2);
        }
        
        &.el-tag--info {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.08) 100%);
          color: #2563eb;
          border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        &.clickable-status {
          cursor: pointer;
          
          &:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }
        }
      }
      
      // 操作按钮组样式
      .action-buttons-group {
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        
        .action-btn {
          border-radius: 8px;
          padding: 6px 10px;
          font-size: 13px;
          font-weight: 500;
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 4px;
          
          .el-icon {
            font-size: 14px;
          }
          
          &.el-button--small {
            &:hover {
              transform: translateY(-2px);
            }
          }
          
          &.el-button--primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            
            &:hover {
              opacity: 0.9;
              box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
          }
          
          &.el-button--info {
            &:hover {
              box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
          }
          
          &.el-button--danger {
            &:hover {
              box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
            }
          }
        }
      }
    }
  }
}

// 全局动画
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
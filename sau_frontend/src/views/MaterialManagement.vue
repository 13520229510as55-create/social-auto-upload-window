<template>
  <div class="material-management">
    <!-- Tab导航 -->
    <el-tabs v-model="activeTab" class="material-tabs-nav">
      <el-tab-pane label="本地上传素材" name="local">
        <div class="material-list-container">
          <div class="search-bar">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索素材文件名..."
              prefix-icon="Search"
              clearable
              @clear="handleSearch"
              @input="handleSearch"
              class="search-input"
            />
            <div class="action-buttons">
              <el-button type="primary" @click="handleUploadMaterial" class="add-btn">
                <el-icon><Upload /></el-icon>
                上传素材
              </el-button>
              <el-button @click="fetchMaterials" :loading="isRefreshing" class="refresh-btn">
                <el-icon :class="{ 'is-loading': isRefreshing }"><Refresh /></el-icon>
                {{ isRefreshing ? '刷新中' : '刷新' }}
              </el-button>
            </div>
          </div>
          
          <div v-if="filteredLocalMaterials.length > 0" class="material-list">
            <el-table :data="filteredLocalMaterials" style="width: 100%">
              <el-table-column prop="uuid" label="UUID" width="180" />
              <el-table-column prop="filename" label="文件名" width="300" />
              <el-table-column prop="filesize" label="文件大小" width="120">
                <template #default="scope">
                  {{ scope.row.filesize }} MB
                </template>
              </el-table-column>
              <el-table-column prop="uri" label="地址" width="350" show-overflow-tooltip>
                <template #default="scope">
                  <div v-if="scope.row.uri" style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #409EFF; cursor: pointer; flex: 1;" @click="handleCopyUri(scope.row.uri)" :title="scope.row.uri">
                      {{ scope.row.uri }}
                    </span>
                  </div>
                  <span v-else style="color: #909399;">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="upload_time" label="上传时间" width="180" />
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button size="small" @click="handlePreview(scope.row)">预览</el-button>
                  <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div v-else class="empty-data">
            <el-empty description="暂无本地上传素材" />
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="谷歌上传素材" name="google">
        <div class="material-list-container">
          <div class="search-bar">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索素材文件名..."
              prefix-icon="Search"
              clearable
              @clear="handleSearch"
              @input="handleSearch"
              class="search-input"
            />
            <div class="action-buttons">
              <el-button type="primary" @click="handleUploadToGoogle" class="add-btn">
                <el-icon><Connection /></el-icon>
                上传到谷歌存储
              </el-button>
              <el-button @click="fetchMaterials" :loading="isRefreshing" class="refresh-btn">
                <el-icon :class="{ 'is-loading': isRefreshing }"><Refresh /></el-icon>
                {{ isRefreshing ? '刷新中' : '刷新' }}
              </el-button>
            </div>
          </div>
          
          <div v-if="filteredGoogleMaterials.length > 0" class="material-list">
            <el-table :data="filteredGoogleMaterials" style="width: 100%">
              <el-table-column prop="uuid" label="UUID" width="180" />
              <el-table-column prop="filename" label="文件名" width="300" />
              <el-table-column prop="filesize" label="文件大小" width="120">
                <template #default="scope">
                  {{ scope.row.filesize }} MB
                </template>
              </el-table-column>
              <el-table-column prop="uri" label="地址" width="350" show-overflow-tooltip>
                <template #default="scope">
                  <div v-if="scope.row.uri" style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #409EFF; cursor: pointer; flex: 1;" @click="handleCopyUri(scope.row.uri)" :title="scope.row.uri">
                      {{ scope.row.uri }}
                    </span>
                    <el-button 
                      size="small" 
                      type="primary" 
                      link
                      @click="handleGetPublicUrl(scope.row)"
                      :loading="scope.row.loadingPublicUrl"
                    >
                      获取公开链接
                    </el-button>
                  </div>
                  <span v-else style="color: #909399;">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="upload_time" label="上传时间" width="180" />
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button size="small" @click="handlePreview(scope.row)">预览</el-button>
                  <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div v-else class="empty-data">
            <el-empty description="暂无谷歌上传素材" />
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="生成素材" name="generated">
        <div class="material-list-container">
          <div class="search-bar">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索素材文件名..."
              prefix-icon="Search"
              clearable
              @clear="handleSearch"
              @input="handleSearch"
              class="search-input"
            />
            <div class="action-buttons">
              <el-button @click="fetchMaterials" :loading="isRefreshing" class="refresh-btn">
                <el-icon :class="{ 'is-loading': isRefreshing }"><Refresh /></el-icon>
                {{ isRefreshing ? '刷新中' : '刷新' }}
              </el-button>
            </div>
          </div>
          
          <div v-if="filteredGeneratedMaterials.length > 0" class="material-list">
            <el-table :data="filteredGeneratedMaterials" style="width: 100%">
              <el-table-column prop="uuid" label="UUID" width="180" />
              <el-table-column prop="filename" label="文件名" width="300" />
              <el-table-column prop="filesize" label="文件大小" width="120">
                <template #default="scope">
                  {{ scope.row.filesize }} MB
                </template>
              </el-table-column>
              <el-table-column prop="uri" label="地址" width="350" show-overflow-tooltip>
                <template #default="scope">
                  <div v-if="scope.row.uri" style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #409EFF; cursor: pointer; flex: 1;" @click="handleCopyUri(scope.row.uri)" :title="scope.row.uri">
                      {{ scope.row.uri }}
                    </span>
                  </div>
                  <span v-else style="color: #909399;">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="upload_time" label="上传时间" width="180" />
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button size="small" @click="handlePreview(scope.row)">预览</el-button>
                  <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div v-else class="empty-data">
            <el-empty description="暂无生成素材" />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 上传对话框（共用） -->
    <el-dialog
      v-model="uploadDialogVisible"
      :title="uploadType === 'local' ? '上传素材' : '上传到谷歌存储'"
      width="40%"
      @close="handleUploadDialogClose"
    >
      <div class="upload-form">
        <el-form label-width="80px">
          <!-- GCS Token 配置（仅谷歌上传时显示） -->
          <el-form-item v-if="uploadType === 'google'" label="GCS Token:">
            <el-input
              v-model="gcsToken"
              type="password"
              placeholder="请输入 Google Cloud Storage Access Token"
              show-password
              clearable
              style="width: 100%;"
            />
            <div class="form-tip" style="margin-top: 5px; font-size: 12px; color: #909399;">
              Token 将自动保存，下次使用时自动填充
            </div>
          </el-form-item>
          <el-form-item label="文件名称:">
            <el-input
              v-model="customFilename"
              placeholder="选填 (仅单个文件时生效)"
              :disabled="customFilenameDisabled"
              clearable
            />
          </el-form-item>
          <el-form-item label="选择文件">
            <el-upload
              class="upload-demo"
              drag
              multiple
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
            >
              <el-icon class="el-icon--upload"><Upload /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持视频、图片等格式文件，可一次选择多个文件
                </div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item label="上传列表" v-if="fileList.length > 0">
            <div class="upload-file-list">
              <div v-for="file in fileList" :key="file.uid" class="upload-file-item">
                <span class="file-name">{{ file.name }}</span>
                <el-progress
                  :percentage="uploadProgress[file.uid]?.percentage || 0"
                  :text-inside="true"
                  :stroke-width="20"
                  style="width: 100%; margin-top: 5px;"
                >
                  <span>{{ uploadProgress[file.uid]?.speed || '' }}</span>
                </el-progress>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitUpload" :loading="isUploading">
            {{ isUploading ? '上传中' : '确认上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="素材预览"
      width="50%"
      :top="'10vh'"
    >
      <div class="preview-container" v-if="currentMaterial">
        <div v-if="isVideoFile(currentMaterial.filename)" class="video-preview">
          <video controls style="max-width: 100%; max-height: 60vh;">
            <source :src="getPreviewUrl(currentMaterial.file_path)" type="video/mp4">
            您的浏览器不支持视频播放
          </video>
        </div>
        <div v-else-if="isImageFile(currentMaterial.filename)" class="image-preview">
          <img :src="getPreviewUrl(currentMaterial.file_path)" style="max-width: 100%; max-height: 60vh;" />
        </div>
        <div v-else class="file-info">
          <p>文件名: {{ currentMaterial.filename }}</p>
          <p>文件大小: {{ currentMaterial.filesize }} MB</p>
          <p>上传时间: {{ currentMaterial.upload_time }}</p>
          <el-button type="primary" @click="downloadFile(currentMaterial)">下载文件</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Refresh, Upload, FolderOpened, Connection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { materialApi } from '@/api/material'
import { useAppStore } from '@/stores/app'

// 获取应用状态管理
const appStore = useAppStore()

// Tab控制
const activeTab = ref('local') // 'local', 'google', 'generated'

// 搜索和状态控制
const searchKeyword = ref('')
const isRefreshing = ref(false)
const isUploading = ref(false)

// 对话框控制
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const currentMaterial = ref(null)
const uploadType = ref('local') // 'local' 或 'google'，用于区分上传类型

// 文件上传（共用）
const fileList = ref([])
const customFilename = ref('')
const customFilenameDisabled = computed(() => fileList.value.length > 1)
const uploadProgress = ref({}); // { [uid]: { percentage: 0, speed: '' } }

// GCS Token 配置
const GCS_TOKEN_STORAGE_KEY = 'gcs_access_token'
const gcsToken = ref('')


watch(fileList, (newList) => {
  if (newList.length <= 1) {
    // If you want to clear the custom name when going back to single file, uncomment below
    // customFilename.value = ''
  }
});


// 获取素材列表
const fetchMaterials = async (autoSwitchTab = false) => {
  isRefreshing.value = true
  try {
    const response = await materialApi.getAllMaterials()
    
    if (response.code === 200) {
      appStore.setMaterials(response.data)
      console.log('[MaterialManagement] 获取素材列表成功，数量:', response.data.length)
      console.log('[MaterialManagement] 素材来源分布:', {
        local: response.data.filter(m => !m.source || m.source === '本地上传').length,
        google: response.data.filter(m => m.source === '谷歌存储上传').length,
        generated: response.data.filter(m => m.source === '生成素材').length
      })
      
      // 只有在初始化时（autoSwitchTab=true）才自动切换tab，刷新时保持当前tab
      if (autoSwitchTab && response.data.length > 0) {
        const hasLocal = response.data.some(m => !m.source || m.source === '本地上传')
        const hasGoogle = response.data.some(m => m.source === '谷歌存储上传')
        const hasGenerated = response.data.some(m => m.source === '生成素材')
        
        // 检查当前 tab 是否有数据
        const currentTabHasData = 
          (activeTab.value === 'local' && hasLocal) ||
          (activeTab.value === 'google' && hasGoogle) ||
          (activeTab.value === 'generated' && hasGenerated)
        
        // 如果当前 tab 没有数据，切换到有数据的 tab
        if (!currentTabHasData) {
          if (hasGenerated) {
            activeTab.value = 'generated'
            console.log('[MaterialManagement] 自动切换到生成素材 tab')
          } else if (hasGoogle) {
            activeTab.value = 'google'
            console.log('[MaterialManagement] 自动切换到谷歌上传素材 tab')
          } else if (hasLocal) {
            activeTab.value = 'local'
            console.log('[MaterialManagement] 自动切换到本地上传素材 tab')
          }
        }
      }
      
      ElMessage.success('刷新成功')
    } else {
      ElMessage.error('获取素材列表失败')
    }
  } catch (error) {
    console.error('获取素材列表出错:', error)
    ElMessage.error('获取素材列表失败')
  } finally {
    isRefreshing.value = false
  }
}

// 根据Tab过滤素材
const filteredLocalMaterials = computed(() => {
  let materials = appStore.materials.filter(m => 
    !m.source || m.source === '本地上传'
  )
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    materials = materials.filter(material => 
      material.filename.toLowerCase().includes(keyword)
    )
  }
  
  return materials
})

const filteredGoogleMaterials = computed(() => {
  let materials = appStore.materials.filter(m => 
    m.source === '谷歌存储上传'
  )
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    materials = materials.filter(material => 
      material.filename.toLowerCase().includes(keyword)
    )
  }
  
  return materials
})

const filteredGeneratedMaterials = computed(() => {
  let materials = appStore.materials.filter(m => 
    m.source === '生成素材'
  )
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    materials = materials.filter(material => 
      material.filename.toLowerCase().includes(keyword)
    )
  }
  
  return materials
})

// 兼容旧代码（保留）
const filteredMaterials = computed(() => {
  if (!searchKeyword.value) return appStore.materials
  
  const keyword = searchKeyword.value.toLowerCase()
  return appStore.materials.filter(material => 
    material.filename.toLowerCase().includes(keyword)
  )
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已通过计算属性实现
}

// 上传素材（本地）
const handleUploadMaterial = () => {
  // 清空变量
  fileList.value = []
  customFilename.value = ''
  uploadProgress.value = {}
  uploadType.value = 'local'
  uploadDialogVisible.value = true
}

// 上传到谷歌存储
const handleUploadToGoogle = () => {
  // 清空变量
  fileList.value = []
  customFilename.value = ''
  uploadProgress.value = {}
  uploadType.value = 'google'
  // 从 localStorage 读取保存的 token
  const savedToken = localStorage.getItem(GCS_TOKEN_STORAGE_KEY)
  if (savedToken) {
    gcsToken.value = savedToken
  } else {
    gcsToken.value = ''
  }
  uploadDialogVisible.value = true
}

// 关闭上传对话框时清空变量
const handleUploadDialogClose = () => {
  fileList.value = []
  customFilename.value = ''
  uploadProgress.value = {}
  // 注意：不在这里清空 gcsToken，保留用户输入
}

// 文件选择变更
const handleFileChange = (file, uploadFileList) => {
  fileList.value = uploadFileList;
  const newProgress = {};
  for (const f of uploadFileList) {
    newProgress[f.uid] = { percentage: 0, speed: '' };
  }
  uploadProgress.value = newProgress;
}

const handleFileRemove = (file, uploadFileList) => {
  fileList.value = uploadFileList;
  const newProgress = { ...uploadProgress.value };
  delete newProgress[file.uid];
  uploadProgress.value = newProgress;
}

// 提交上传（根据类型调用不同的上传函数）
const handleSubmitUpload = () => {
  if (uploadType.value === 'local') {
    submitLocalUpload()
  } else {
    submitGoogleUpload()
  }
}

// 提交本地上传
const submitLocalUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  
  isUploading.value = true
  
  for (const file of fileList.value) {
    try {
      // 确保文件对象存在
      if (!file || !file.raw) {
        ElMessage.warning(`文件 ${file.name} 对象无效，已跳过`)
        continue
      }
      
      const formData = new FormData()
      formData.append('file', file.raw)
      
      // 只有当只有一个文件时，自定义文件名才生效
      if (fileList.value.length === 1 && customFilename.value.trim()) {
        formData.append('filename', customFilename.value.trim())
      }
      
      let lastLoaded = 0;
      let lastTime = Date.now();

      const response = await materialApi.uploadMaterial(formData, (progressEvent) => {
        const progressData = uploadProgress.value[file.uid];
        if (!progressData) return;

        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        progressData.percentage = progress;

        const currentTime = Date.now();
        const timeDiff = (currentTime - lastTime) / 1000; // in seconds
        const loadedDiff = progressEvent.loaded - lastLoaded;

        if (timeDiff > 0.5) { // Update speed every 0.5 seconds
          const speed = loadedDiff / timeDiff; // bytes per second
          if (speed > 1024 * 1024) {
            progressData.speed = (speed / (1024 * 1024)).toFixed(2) + ' MB/s';
          } else {
            progressData.speed = (speed / 1024).toFixed(2) + ' KB/s';
          }
          lastLoaded = progressEvent.loaded;
          lastTime = currentTime;
        }
      })
      
      if (response.code === 200) {
        ElMessage.success(`文件 ${file.name} 上传成功`)
        const progressData = uploadProgress.value[file.uid];
        if(progressData) progressData.speed = '完成';
      } else {
        ElMessage.error(`文件 ${file.name} 上传失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      console.error(`上传文件 ${file.name} 出错:`, error)
      ElMessage.error(`文件 ${file.name} 上传失败: ${error.message || '未知错误'}`)
    }
  }
  
  isUploading.value = false
  // Keep dialog open to show results
  // uploadDialogVisible.value = false 
  await fetchMaterials()
}

// 预览素材
const handlePreview = async (material) => {
  currentMaterial.value = null
  previewDialogVisible.value = true
  ElMessage.info('加载中...')
  try {
    // 等待一小段时间以确保对话框已打开
    await new Promise(resolve => setTimeout(resolve, 100))
    currentMaterial.value = material
  } catch (error) {
    console.error('预览素材出错:', error)
    ElMessage.error('预览加载失败')
    previewDialogVisible.value = false
  }
}

// 删除素材
const handleDelete = (material) => {
  ElMessageBox.confirm(
    `确定要删除素材 ${material.filename} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        const response = await materialApi.deleteMaterial(material.id)
        
        if (response.code === 200) {
          appStore.removeMaterial(material.id)
          ElMessage.success('删除成功')
        } else {
          ElMessage.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除素材出错:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// 获取预览URL
const getPreviewUrl = (filePath) => {
  const filename = filePath.split('/').pop()
  return materialApi.getMaterialPreviewUrl(filename)
}

// 下载文件
const downloadFile = (material) => {
  const url = materialApi.downloadMaterial(material.file_path)
  window.open(url, '_blank')
}

// 判断文件类型
const isVideoFile = (filename) => {
  const videoExtensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
  return videoExtensions.some(ext => filename.toLowerCase().endsWith(ext))
}

const isImageFile = (filename) => {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
  return imageExtensions.some(ext => filename.toLowerCase().endsWith(ext))
}

// 复制URI地址
const handleCopyUri = (uri) => {
  if (!uri) return
  navigator.clipboard.writeText(uri).then(() => {
    ElMessage.success('URI地址已复制到剪贴板')
  }).catch(() => {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = uri
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('URI地址已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败')
    }
    document.body.removeChild(textarea)
  })
}

// 获取谷歌存储文件的公开链接
const handleGetPublicUrl = async (material) => {
  if (!material.uri) {
    ElMessage.warning('该素材没有URI地址')
    return
  }
  
  // 设置加载状态
  material.loadingPublicUrl = true
  
  try {
    const response = await materialApi.getGoogleFilePublicUrl(material.uri)
    
    if (response.code === 200 && response.data) {
      const fileInfo = response.data.file_info
      const fileId = response.data.file_id
      
      // 说明：Google Generative AI API的文件需要通过API访问，没有直接的公开链接
      // 如果需要公开链接，需要将文件上传到Google Cloud Storage并设置公开权限
      // 这里显示文件信息和API访问地址
      const message = `文件ID: ${fileId}\n状态: ${fileInfo?.state || '未知'}\n\n注意：Google Generative AI API的文件需要通过API Key访问，没有直接的公开链接。\n\n如果需要公开链接，请将文件上传到Google Cloud Storage并设置公开权限。\n\nAPI访问地址已复制到剪贴板。`
      
      ElMessageBox.alert(message, '文件信息', {
        confirmButtonText: '确定',
        type: 'info'
      })
      
      // 复制API访问地址
      handleCopyUri(material.uri)
    } else {
      ElMessage.error(response.msg || '获取文件信息失败')
    }
  } catch (error) {
    console.error('获取公开链接出错:', error)
    ElMessage.error('获取文件信息失败: ' + (error.message || '未知错误'))
  } finally {
    material.loadingPublicUrl = false
  }
}

// 提交谷歌上传
const submitGoogleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  
  // 从输入框读取 token（每次上传都使用输入框的当前值）
  const tokenFromInput = gcsToken.value?.trim() || ''
  if (!tokenFromInput) {
    ElMessage.warning('请输入 GCS Token')
    return
  }
  
  // 保存当前输入框的 token 到 localStorage（用于下次打开对话框时自动填充）
  localStorage.setItem(GCS_TOKEN_STORAGE_KEY, tokenFromInput)
  
  isUploading.value = true
  
  for (const file of fileList.value) {
    try {
      // 确保文件对象存在
      if (!file || !file.raw) {
        ElMessage.warning(`文件 ${file.name} 对象无效，已跳过`)
        continue
      }
      
      // 确定文件名（支持自定义文件名）
      let filename = file.name
      if (fileList.value.length === 1 && customFilename.value.trim()) {
        // 如果有自定义文件名，保留原文件扩展名
        const ext = file.name.split('.').pop()
        filename = `${customFilename.value.trim()}.${ext}`
      }
      
      let lastLoaded = 0
      let lastTime = Date.now()

      // 使用从输入框读取的 token
      const response = await materialApi.uploadToGoogleStorage(
        file.raw, 
        filename,
        tokenFromInput, // 使用输入框中的 token
        (progressEvent) => {
          const progressData = uploadProgress.value[file.uid]
          if (!progressData) return

          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          progressData.percentage = progress

          const currentTime = Date.now()
          const timeDiff = (currentTime - lastTime) / 1000 // in seconds
          const loadedDiff = progressEvent.loaded - lastLoaded

          if (timeDiff > 0.5) { // Update speed every 0.5 seconds
            const speed = loadedDiff / timeDiff // bytes per second
            if (speed > 1024 * 1024) {
              progressData.speed = (speed / (1024 * 1024)).toFixed(2) + ' MB/s'
            } else {
              progressData.speed = (speed / 1024).toFixed(2) + ' KB/s'
            }
            lastLoaded = progressEvent.loaded
            lastTime = currentTime
          }
        }
      )
      
      if (response.status === 200 || response.status === 201 || response.data) {
        ElMessage.success(`文件 ${file.name} 上传到谷歌存储成功`)
        const progressData = uploadProgress.value[file.uid]
        if (progressData) {
          progressData.percentage = 100
          progressData.speed = '完成'
        }
        
        // 获取公开访问URL
        let uri = null
        if (response.data) {
          // Google Cloud Storage返回的公开URL
          uri = response.data.publicUrl || response.data.uri || null
        }
        
        // 计算文件大小（MB）
        const fileSizeMB = (file.raw.size / (1024 * 1024)).toFixed(2)
        
        // 保存素材信息到数据库
        try {
          const saveData = {
            filename: filename,
            filesize: parseFloat(fileSizeMB),
            uri: uri,
            custom_filename: null // 已经在filename中处理了
          }
          
          const saveResponse = await materialApi.saveGoogleStorageMaterial(saveData)
          if (saveResponse.code === 200) {
            console.log('素材信息已保存到数据库')
            // 刷新素材列表
            await fetchMaterials()
          } else {
            console.error('保存素材信息失败:', saveResponse.msg)
            ElMessage.warning(`文件 ${file.name} 上传成功，但保存信息失败: ${saveResponse.msg}`)
          }
        } catch (saveError) {
          console.error('保存素材信息出错:', saveError)
          ElMessage.warning(`文件 ${file.name} 上传成功，但保存信息出错`)
        }
      } else {
        ElMessage.error(`文件 ${file.name} 上传失败: ${response.data?.error?.message || '未知错误'}`)
      }
    } catch (error) {
      console.error(`上传文件 ${file.name} 到谷歌存储出错:`, error)
      const errorMessage = error.response?.data?.error?.message || error.message || '未知错误'
      ElMessage.error(`文件 ${file.name} 上传失败: ${errorMessage}`)
      const progressData = uploadProgress.value[file.uid]
      if (progressData) {
        progressData.speed = '失败'
      }
    }
  }
  
  isUploading.value = false
  // Keep dialog open to show results
  // uploadDialogVisible.value = false
}

// 组件挂载时获取素材列表
onMounted(async () => {
  // 只有store中没有数据时才获取，初始化时允许自动切换tab
  if (appStore.materials.length === 0) {
    await fetchMaterials(true) // 传入true，允许自动切换tab
  }
  
  // 根据数据自动切换到有数据的 tab（仅在初始化时）
  if (appStore.materials.length > 0) {
    // 检查哪个 tab 有数据
    const hasLocal = appStore.materials.some(m => !m.source || m.source === '本地上传')
    const hasGoogle = appStore.materials.some(m => m.source === '谷歌存储上传')
    const hasGenerated = appStore.materials.some(m => m.source === '生成素材')
    
    // 优先切换到有数据的 tab
    if (hasGenerated && activeTab.value === 'local') {
      activeTab.value = 'generated'
    } else if (hasGoogle && activeTab.value === 'local' && !hasGenerated) {
      activeTab.value = 'google'
    } else if (hasLocal && activeTab.value === 'local') {
      // 保持 local tab
    }
  }
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

.material-management {
  min-height: 100%;
  animation: fadeIn 0.6s ease-out;
  
  // Tab导航样式（参考制作中心）
  .material-tabs-nav {
    margin-bottom: 0;
    
    :deep(.el-tabs__header) {
      margin: 0 0 0 0;
      background: white;
      border-radius: 16px 16px 0 0;
      padding: 0 24px;
      border-bottom: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    :deep(.el-tabs__nav-wrap) {
      &::after {
        display: none;
      }
    }
    
    :deep(.el-tabs__item) {
      height: 56px;
      line-height: 56px;
      font-size: 15px;
      font-weight: 500;
      color: #64748b;
      padding: 0 24px;
      transition: all 0.3s ease;
      
      &:hover {
        color: #667eea;
      }
      
      &.is-active {
        color: #667eea;
        font-weight: 600;
      }
    }
    
    :deep(.el-tabs__active-bar) {
      background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
      height: 3px;
    }
  }
  
  .material-list-container {
    background-color: #fff;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    padding: 20px;
    border-top: 1px solid rgba(102, 126, 234, 0.1);
    
    .search-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      padding: 12px 16px;
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.02) 100%);
      border-radius: 10px;
      border: 1px solid rgba(102, 126, 234, 0.08);
      
      .search-input {
        max-width: 400px;
        flex: 1;
        
        :deep(.el-input__wrapper) {
          background: white;
          border-radius: 10px;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
          transition: all 0.3s;
          
          &:hover {
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
          }
          
          &.is-focus {
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }
        }
      }
      
      .action-buttons {
        display: flex;
        gap: 8px;
        
        .el-button {
          border-radius: 8px;
          font-weight: 500;
          height: 36px;
          padding: 0 16px;
          font-size: 13px;
          transition: all 0.3s ease;
          
          &.add-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
            
            &:hover {
              opacity: 0.92;
              transform: translateY(-1px);
              box-shadow: 0 4px 10px rgba(102, 126, 234, 0.35);
            }
            
            .el-icon {
              margin-right: 4px;
              font-size: 14px;
            }
          }
          
          &.refresh-btn {
            .el-icon {
              margin-right: 6px;
              
              &.is-loading {
                animation: rotate 1s linear infinite;
              }
            }
          }
        }
      }
    }
    
    .material-list {
      margin-top: 20px;
    }
    
    .empty-data {
      padding: 40px 0;
    }
  }
  
  .material-upload {
    width: 100%;
  }
  
  .preview-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 0 20px;
    
    .file-info {
      text-align: center;
      margin-top: 20px;
    }
  }
}

.upload-form {
  padding: 0 20px;
  
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
  
  .upload-demo {
    width: 100%;
  }
}

.dialog-footer {
  padding: 0 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-file-list {
  width: 100%;
}

.upload-file-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.upload-file-item .file-name {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
  display: block;
}

/* 覆盖Element Plus对话框样式 */
:deep(.el-dialog__body) {
  padding: 20px 0;
}

:deep(.el-dialog__header) {
  padding-left: 20px;
  padding-right: 20px;
  margin-right: 0;
}

:deep(.el-dialog__footer) {
  padding-top: 10px;
  padding-bottom: 15px;
}

/* 修改上传进度条样式 */
:deep(.el-progress__text) {
  color: #303133 !important; /* 深灰色字体，确保在各种背景上都可见 */
  font-size: 12px;
}

:deep(.el-progress--line) {
  margin-bottom: 10px;
}

.upload-file-item {
  border: 1px solid #dcdfe6;
  border-radius: 6px; /* 增加圆角 */
  padding: 12px; /* 增加内边距 */
  margin-bottom: 12px; /* 增加外边距 */
  background-color: #fafafa; /* 轻微背景色 */
  transition: box-shadow 0.3s; /* 添加过渡效果 */
}

.upload-file-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 悬停效果 */
}

.upload-file-item .file-name {
  font-size: 14px;
  color: #303133; /* 深灰色字体 */
  margin-bottom: 8px; /* 增加底部间距 */
  display: block;
  font-weight: 500;
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
      padding: 16px 12px;
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
        padding: 14px 12px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.04);
      }
    }
    
    .el-button {
      border-radius: 8px;
      padding: 6px 12px;
      font-size: 13px;
      transition: all 0.3s ease;
      
      &.el-button--primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        
        &:hover {
          opacity: 0.9;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
      }
      
      &.el-button--danger {
        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
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

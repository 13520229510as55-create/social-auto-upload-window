<template>
  <div>
    <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center">
      <h2 style="margin: 0">任务管理</h2>
      <el-button
        type="primary"
        :icon="VideoPlay"
        @click="startModalVisible = true"
      >
        启动新任务
      </el-button>
    </div>

    <el-card>
      <el-table
        :data="tasks"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="task_id" label="任务ID" show-overflow-tooltip />
        <el-table-column prop="platform" label="平台">
          <template #default="{ row }">
            {{ platformNames[row.platform] || row.platform }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度">
          <template #default="{ row }">
            {{ row.progress || 0 }}%
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'running'"
              size="small"
              type="danger"
              :icon="VideoPause"
              @click="handleStopTask(row.task_id)"
            >
              停止
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="startModalVisible"
      title="启动新任务"
      width="600px"
      @close="handleCloseModal"
    >
      <el-form
        ref="formRef"
        :model="formData"
        label-width="150px"
        :rules="rules"
      >
        <el-form-item label="平台" prop="platform">
          <el-select
            v-model="formData.platform"
            placeholder="请选择平台"
            @change="handlePlatformChange"
          >
            <el-option label="小红书" value="xhs" />
            <el-option label="抖音" value="dy" />
            <el-option label="快手" value="ks" />
            <el-option label="B站" value="bili" />
            <el-option label="微博" value="wb" />
            <el-option label="百度贴吧" value="tieba" />
            <el-option label="知乎" value="zhihu" />
            <el-option label="掘金" value="juejin" />
            <el-option label="Medium" value="medium" />
            <el-option label="公众号" value="wechat" />
          </el-select>
        </el-form-item>

        <template v-if="formData.platform === 'wechat'">
          <el-form-item label="公众号分享链接" prop="wxs_links">
            <el-input
              v-model="formData.wxs_links"
              type="textarea"
              :rows="4"
              placeholder="请输入公众号文章分享链接，一行一条，例如：&#10;https://mp.weixin.qq.com/s/xxxxxx&#10;https://mp.weixin.qq.com/s/yyyyyy"
            />
          </el-form-item>
        </template>

        <template v-else>
          <el-form-item label="爬取类型" prop="crawler_type">
            <el-select v-model="formData.crawler_type">
              <el-option label="关键词搜索" value="search" />
              <el-option label="指定帖子详情" value="detail" />
              <el-option label="创作者主页" value="creator" />
            </el-select>
          </el-form-item>

          <el-form-item label="关键词（搜索模式，多个用逗号分隔）">
            <el-select
              v-model="formData.keywords"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入关键词，按回车添加多个，或直接输入逗号分隔的字符串"
            />
          </el-form-item>

          <el-form-item label="最大爬取数量">
            <el-select v-model="formData.max_notes_count">
              <el-option :label="10" :value="10" />
              <el-option :label="15" :value="15" />
              <el-option :label="20" :value="20" />
              <el-option :label="50" :value="50" />
            </el-select>
          </el-form-item>

          <el-form-item label="无头模式（不显示浏览器窗口）">
            <el-switch
              v-model="formData.headless"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>

          <el-form-item label="是否爬取评论">
            <el-switch
              v-model="formData.enable_get_comments"
              active-text="是"
              inactive-text="否"
            />
          </el-form-item>

          <el-form-item label="最大评论数量">
            <el-select v-model="formData.max_comments_count">
              <el-option :label="5" :value="5" />
              <el-option :label="10" :value="10" />
              <el-option :label="20" :value="20" />
              <el-option :label="50" :value="50" />
            </el-select>
          </el-form-item>

          <el-form-item label="强制重新登录">
            <el-switch
              v-model="formData.force_relogin"
              active-text="是"
              inactive-text="否"
            />
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <el-button @click="handleCloseModal">取消</el-button>
        <el-button type="primary" @click="handleStartTask" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import crawlerApi from '@/api/crawler'

const tasks = ref([])
const loading = ref(false)
const startModalVisible = ref(false)
const formRef = ref(null)

const formData = reactive({
  platform: '',
  crawler_type: 'search',
  keywords: [],
  max_notes_count: 15,
  headless: false,
  enable_get_comments: true,
  max_comments_count: 10,
  force_relogin: false,
  wxs_links: ''
})

const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  crawler_type: [{ required: true, message: '请选择爬取类型', trigger: 'change' }],
  wxs_links: [{ required: true, message: '请输入公众号分享链接', trigger: 'blur' }]
}

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

const statusMap = {
  running: { type: 'success', text: '运行中' },
  completed: { type: 'info', text: '已完成' },
  failed: { type: 'danger', text: '失败' },
  cancelled: { type: 'info', text: '已取消' },
  pending: { type: 'warning', text: '等待中' }
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
}

const getStatusText = (status) => {
  return statusMap[status]?.text || status
}

let intervalId = null

onMounted(() => {
  loadTasks()
  // 每5秒刷新一次
  intervalId = setInterval(loadTasks, 5000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

const loadTasks = async () => {
  try {
    const data = await crawlerApi.getTasks()
    tasks.value = data.tasks || []
  } catch (error) {
    console.error('加载任务列表失败:', error)
  }
}

const handleStartTask = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    // 如果是公众号任务，使用不同的处理逻辑
    if (formData.platform === 'wechat') {
      const wxsLinks = formData.wxs_links ? formData.wxs_links.split('\n').filter(link => link.trim()) : []
      if (wxsLinks.length === 0) {
        ElMessage.error('请至少输入一个公众号分享链接')
        loading.value = false
        return
      }

      // 处理每个公众号链接
      for (const wxsLink of wxsLinks) {
        try {
          // 获取公众号信息
          const mpInfoResult = await crawlerApi.getWechatMpInfo(wxsLink.trim())
          if (mpInfoResult.mp_info && mpInfoResult.mp_info.length > 0) {
            const mpInfo = mpInfoResult.mp_info[0]
            
            // 添加订阅源
            await crawlerApi.addWechatFeed({
              feed_id: mpInfo.id,
              mp_name: mpInfo.name,
              mp_cover: mpInfo.cover,
              mp_intro: mpInfo.intro,
              update_time: mpInfo.updateTime,
              status: 1
            })

            // 刷新文章
            await crawlerApi.refreshWechatFeed(mpInfo.id)
            
            ElMessage.success(`公众号 ${mpInfo.name} 添加成功`)
          } else {
            ElMessage.error('获取公众号信息失败，请检查链接是否正确')
          }
        } catch (error) {
          ElMessage.error(`处理链接失败: ${error.message}`)
        }
      }

      startModalVisible.value = false
      handleCloseModal()
      return
    }

    // 处理关键词：如果是数组则转换为逗号分隔的字符串
    let keywords = formData.keywords || []
    if (Array.isArray(keywords)) {
      keywords = keywords.join(',')
    }

    const taskRequest = {
      platform: formData.platform,
      config: {
        platform: formData.platform,
        keywords: keywords,
        login_type: formData.force_relogin ? 'qrcode' : 'auto',
        crawler_type: formData.crawler_type || 'search',
        start_page: 1,
        max_notes_count: formData.max_notes_count || 15,
        enable_get_comments: formData.enable_get_comments !== false,
        max_comments_count: formData.max_comments_count || 10,
        enable_get_medias: false,
        headless: formData.headless === undefined ? false : formData.headless,
        save_data_option: 'json',
        force_relogin: formData.force_relogin || false
      }
    }

    await crawlerApi.startTask(taskRequest)
    ElMessage.success('任务已启动')
    startModalVisible.value = false
    handleCloseModal()
    loadTasks()
  } catch (error) {
    ElMessage.error('启动任务失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleStopTask = async (taskId) => {
  try {
    await crawlerApi.stopTask(taskId)
    ElMessage.success('任务已停止')
    loadTasks()
  } catch (error) {
    ElMessage.error('停止任务失败: ' + error.message)
  }
}

const handlePlatformChange = (value) => {
  // 切换平台时重置表单
  if (value === 'wechat') {
    formData.crawler_type = undefined
    formData.keywords = []
    formData.wxs_links = ''
  } else {
    formData.crawler_type = 'search'
    formData.wxs_links = undefined
  }
}

const handleCloseModal = () => {
  startModalVisible.value = false
  formRef.value?.resetFields()
  Object.assign(formData, {
    platform: '',
    crawler_type: 'search',
    keywords: [],
    max_notes_count: 15,
    headless: false,
    enable_get_comments: true,
    max_comments_count: 10,
    force_relogin: false,
    wxs_links: ''
  })
}
</script>

<style scoped>
</style>


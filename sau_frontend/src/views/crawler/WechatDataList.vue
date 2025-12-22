<template>
  <div style="display: flex; gap: 16px">
    <el-card
      title="公众号订阅源"
      style="width: 400px; flex-shrink: 0"
    >
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>公众号订阅源</span>
          <el-space>
            <el-button size="small" @click="loadFeeds">刷新列表</el-button>
            <el-button 
              size="small" 
              :icon="Refresh"
              @click="handleRefreshAll"
              :loading="refreshing"
            >
              刷新全部
            </el-button>
          </el-space>
        </div>
      </template>
      
      <el-table
        :data="feeds"
        v-loading="loading"
        size="small"
        @row-click="(row) => setSelectedFeedId(row.id)"
        :row-style="getRowStyle"
      >
        <el-table-column label="公众号">
          <template #default="{ row }">
            <el-space>
              <el-avatar :src="row.mp_cover" :size="24" />
              <span>{{ row.mp_name }}</span>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后同步" width="180">
          <template #default="{ row }">
            {{ formatTime(row.sync_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-space>
              <el-button
                size="small"
                type="primary"
                link
                @click.stop="setSelectedFeedId(row.id)"
              >
                查看文章
              </el-button>
              <el-button
                size="small"
                :icon="Refresh"
                :loading="refreshing && selectedFeedId === row.id"
                @click.stop="handleRefreshFeed(row.id)"
              >
                刷新
              </el-button>
              <el-button
                v-if="row.has_history === 1"
                size="small"
                :icon="Clock"
                :loading="gettingHistory && historyProgress.id === row.id"
                @click.stop="handleGetHistoryArticles(row.id)"
              >
                {{ historyProgress.id === row.id ? '停止获取' : '获取历史' }}
              </el-button>
              <el-switch
                size="small"
                :model-value="row.status === 1"
                @change="(checked) => handleUpdateFeedStatus(row.id, checked ? 1 : 2)"
                active-text="启用"
                inactive-text="禁用"
              />
              <el-button
                size="small"
                type="danger"
                link
                @click.stop="handleDeleteFeed(row.id)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card
      :title="selectedFeedId ? `文章列表 (${getFeedName(selectedFeedId)})` : '文章列表'"
      style="flex: 1"
    >
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>{{ selectedFeedId ? `文章列表 (${getFeedName(selectedFeedId)})` : '文章列表' }}</span>
          <el-space v-if="selectedFeedId">
            <el-button
              size="small"
              :icon="Refresh"
              :loading="refreshing"
              @click="handleRefreshFeed(selectedFeedId)"
            >
              刷新文章
            </el-button>
            <el-button
              v-if="getFeedById(selectedFeedId)?.has_history === 1"
              size="small"
              :icon="Clock"
              :loading="gettingHistory && historyProgress.id === selectedFeedId"
              @click="handleGetHistoryArticles(selectedFeedId)"
            >
              {{ historyProgress.id === selectedFeedId ? '停止获取' : '获取历史' }}
            </el-button>
          </el-space>
        </div>
      </template>
      
      <div v-if="selectedFeedId">
        <el-table
          :data="articles"
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="title" label="标题" show-overflow-tooltip>
            <template #default="{ row }">
              <a
                :href="`https://mp.weixin.qq.com/s/${row.id}`"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ row.title }}
              </a>
            </template>
          </el-table-column>
          <el-table-column prop="publish_time" label="发布时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.publish_time) }}
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
          style="margin-top: 16px"
        />
      </div>
      <div v-else style="text-align: center; padding: 40px; color: #999">
        请选择一个公众号查看文章列表
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { Refresh, Clock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import crawlerApi from '@/api/crawler'
import dayjs from 'dayjs'

const feeds = ref([])
const articles = ref([])
const selectedFeedId = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const gettingHistory = ref(false)
const historyProgress = ref({ id: '', page: 1 })
const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0
})

let progressInterval = null

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
  return dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss')
}

const getFeedName = (feedId) => {
  const feed = feeds.value.find(f => f.id === feedId)
  return feed?.mp_name || ''
}

const getFeedById = (feedId) => {
  return feeds.value.find(f => f.id === feedId)
}

const getRowStyle = ({ row }) => {
  return {
    cursor: 'pointer',
    backgroundColor: selectedFeedId.value === row.id ? '#e6f7ff' : 'transparent'
  }
}

onMounted(() => {
  loadFeeds()
  
  // 轮询获取历史文章进度
  progressInterval = setInterval(async () => {
    try {
      const progress = await crawlerApi.getWechatHistoryProgress()
      historyProgress.value = progress
    } catch (error) {
      // 忽略错误
    }
  }, 2000)
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})

watch(selectedFeedId, (newId) => {
  if (newId !== null) {
    pagination.value.current = 1
    loadArticles()
  }
})

watch([pagination], () => {
  if (selectedFeedId.value) {
    loadArticles()
  }
}, { deep: true })

const loadFeeds = async () => {
  try {
    loading.value = true
    const data = await crawlerApi.getWechatFeeds()
    feeds.value = data.feeds || []
  } catch (error) {
    ElMessage.error('加载订阅源列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadArticles = async () => {
  try {
    loading.value = true
    const params = {
      mp_id: selectedFeedId.value || undefined,
      limit: pagination.value.pageSize,
      offset: (pagination.value.current - 1) * pagination.value.pageSize
    }
    const data = await crawlerApi.getWechatArticles(params)
    articles.value = data.articles || []
    pagination.value.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载文章列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const setSelectedFeedId = (feedId) => {
  selectedFeedId.value = feedId
}

const handleRefreshFeed = async (feedId) => {
  try {
    refreshing.value = true
    await crawlerApi.refreshWechatFeed(feedId)
    ElMessage.success('刷新成功')
    await loadFeeds()
    if (feedId === selectedFeedId.value) {
      await loadArticles()
    }
  } catch (error) {
    ElMessage.error('刷新失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

const handleUpdateFeedStatus = async (feedId, status) => {
  try {
    await crawlerApi.updateWechatFeedStatus(feedId, status)
    ElMessage.success('状态更新成功')
    await loadFeeds()
  } catch (error) {
    ElMessage.error('更新状态失败: ' + error.message)
  }
}

const handleDeleteFeed = async (feedId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个订阅源吗？已获取的文章不会被删除。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await crawlerApi.deleteWechatFeed(feedId)
    ElMessage.success('删除成功')
    if (feedId === selectedFeedId.value) {
      selectedFeedId.value = null
      articles.value = []
    }
    await loadFeeds()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const handleGetHistoryArticles = async (feedId) => {
  try {
    gettingHistory.value = true
    if (historyProgress.value.id === feedId) {
      // 停止获取
      await crawlerApi.getWechatHistoryArticles(feedId)
      ElMessage.info('已停止获取历史文章')
    } else {
      // 开始获取
      await crawlerApi.getWechatHistoryArticles(feedId)
      ElMessage.success('开始获取历史文章，请耐心等待')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  } finally {
    gettingHistory.value = false
  }
}

const handleRefreshAll = async () => {
  try {
    refreshing.value = true
    const feedsData = await crawlerApi.getWechatFeeds()
    for (const feed of feedsData.feeds || []) {
      if (feed.status === 1) {
        try {
          await crawlerApi.refreshWechatFeed(feed.id)
        } catch (error) {
          console.error(`刷新 ${feed.mp_name} 失败:`, error)
        }
      }
    }
    ElMessage.success('批量刷新完成')
    await loadFeeds()
    if (selectedFeedId.value) {
      await loadArticles()
    }
  } catch (error) {
    ElMessage.error('批量刷新失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

const handlePageChange = (page) => {
  pagination.value.current = page
}

const handlePageSizeChange = (size) => {
  pagination.value.pageSize = size
  pagination.value.current = 1
}
</script>


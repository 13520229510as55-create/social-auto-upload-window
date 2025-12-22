<template>
  <div>
    <h2 style="margin-bottom: 24px">数据列表</h2>
    <el-tabs v-model="currentPlatform" @tab-change="handlePlatformChange">
      <el-tab-pane
        v-for="platform in nonWechatPlatforms"
        :key="platform.value"
        :label="platform.label"
        :name="platform.value"
      >
        <el-card style="margin-bottom: 16px">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>数据筛选</span>
            </div>
          </template>
          <el-space style="margin-bottom: 16px" wrap>
            <!-- 小红书和快手显示筛选选项 -->
            <template v-if="platform.value === 'xhs' || platform.value === 'ks'">
              <el-select
                v-model="filterCrawlerType"
                placeholder="爬取类型"
                clearable
                style="width: 150px"
                @change="handleFilterChange"
              >
                <el-option label="关键词搜索" value="search" />
                <el-option label="指定帖子详情" value="detail" />
                <el-option label="创作者主页" value="creator" />
              </el-select>
              <el-select
                v-model="filterKeyword"
                placeholder="关键词"
                clearable
                filterable
                style="width: 150px"
                @change="handleFilterChange"
              >
                <el-option
                  v-for="kw in filterOptions.keywords"
                  :key="kw"
                  :label="kw"
                  :value="kw"
                />
              </el-select>
              <el-select
                v-model="filterNoteType"
                placeholder="内容类型"
                clearable
                style="width: 120px"
                @change="handleFilterChange"
              >
                <el-option label="图文" value="图文" />
                <el-option label="视频" value="视频" />
                <el-option label="文章" value="文章" />
              </el-select>
            </template>
            
            <el-input
              v-model="searchText"
              placeholder="搜索标题或作者"
              style="width: 300px"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
            
            <el-button @click="handleReset">重置</el-button>
            <el-button :icon="Refresh" @click="handleRefresh" :loading="loading">
              刷新
            </el-button>
          </el-space>
        </el-card>
        
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>数据列表</span>
              <span style="color: #909399; font-size: 14px">共 {{ pagination.total }} 条</span>
            </div>
          </template>
          <el-table
            :data="data"
            v-loading="loading"
            style="width: 100%"
            @sort-change="handleSortChange"
          >
            <el-table-column prop="title" label="标题" width="300" show-overflow-tooltip>
              <template #default="{ row }">
                <a :href="row.note_url" target="_blank" rel="noopener noreferrer">
                  {{ row.title || '-' }}
                </a>
              </template>
            </el-table-column>
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="publish_time" label="发布时间" width="180" />
            <el-table-column
              prop="liked_count"
              label="点赞数"
              width="100"
              sortable="custom"
            >
              <template #default="{ row }">
                <el-tag v-if="row.liked_count" type="danger">{{ row.liked_count }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="comment_count"
              label="评论数"
              width="100"
              sortable="custom"
            >
              <template #default="{ row }">
                <el-tag v-if="row.comment_count" type="primary">{{ row.comment_count }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="collected_count"
              label="收藏数"
              width="100"
              sortable="custom"
            >
              <template #default="{ row }">
                <el-tag v-if="row.collected_count" type="success">{{ row.collected_count }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.type === 'video'" type="warning">视频</el-tag>
                <el-tag v-else>图文</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  :icon="ChatLineRound"
                  @click="handleViewComments(row.id)"
                >
                  查看评论
                </el-button>
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
            style="margin-top: 16px; justify-content: flex-end"
          />
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="公众号" name="wechat">
        <WechatDataList />
      </el-tab-pane>
    </el-tabs>

    <!-- 评论弹窗 -->
    <el-dialog
      v-model="commentsModalVisible"
      :title="`评论列表 (共 ${commentsPagination.total} 条)`"
      width="800px"
      @close="handleCommentsModalClose"
    >
      <el-skeleton v-if="commentsLoading" :rows="5" animated />
      <el-list v-else>
        <el-list-item v-for="comment in comments" :key="comment.id">
          <el-avatar :src="comment.avatar">{{ comment.author?.[0] || '?' }}</el-avatar>
          <div style="margin-left: 12px; flex: 1">
            <div style="margin-bottom: 8px">
              <el-space>
                <span>{{ comment.author || '匿名用户' }}</span>
                <el-tag v-if="comment.ip_location" size="small">{{ comment.ip_location }}</el-tag>
                <el-tag v-if="comment.like_count > 0" type="danger" size="small">
                  👍 {{ comment.like_count }}
                </el-tag>
                <el-tag v-if="comment.sub_comment_count > 0" type="primary" size="small">
                  回复 {{ comment.sub_comment_count }}
                </el-tag>
              </el-space>
            </div>
            <div style="margin-bottom: 8px">{{ comment.content || '-' }}</div>
            <div style="font-size: 12px; color: #999">{{ comment.create_time || '-' }}</div>
          </div>
        </el-list-item>
      </el-list>
      
      <el-pagination
        v-model:current-page="commentsPagination.current"
        :page-size="commentsPagination.pageSize"
        :total="commentsPagination.total"
        layout="total, prev, pager, next"
        @current-change="handleCommentsPageChange"
        style="margin-top: 16px"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, Refresh, ChatLineRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import crawlerApi from '@/api/crawler'
import WechatDataList from './WechatDataList.vue'

const route = useRoute()
const router = useRouter()
const currentPlatform = ref(route.params.platform || 'xhs')
const data = ref([])
const loading = ref(false)
const searchText = ref('')
const filterCrawlerType = ref('')
const filterKeyword = ref('')
const filterNoteType = ref('')
const filterOptions = reactive({ keywords: [], crawler_types: [] })
const sortInfo = reactive({ field: '', order: '' })
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})
const commentsModalVisible = ref(false)
const currentNoteId = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const commentsPagination = reactive({
  current: 1,
  pageSize: 50,
  total: 0
})

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

const platforms = ref([])
const nonWechatPlatforms = computed(() => {
  if (platforms.value.length > 0) {
    return platforms.value.filter(p => p.value !== 'wechat')
  }
  // 默认平台列表
  return Object.keys(platformNames)
    .filter(key => key !== 'wechat')
    .map(key => ({ value: key, label: platformNames[key] }))
})

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const response = await crawlerApi.getPlatforms()
    platforms.value = response.platforms || []
  } catch (error) {
    console.error('加载平台列表失败:', error)
    // 使用默认平台列表
    platforms.value = Object.keys(platformNames).map(key => ({
      value: key,
      label: platformNames[key]
    }))
  }
}

onMounted(async () => {
  await loadPlatforms()
  // 如果有路由参数，设置当前平台
  if (route.params.platform) {
    currentPlatform.value = route.params.platform
  }
})

watch(currentPlatform, (newPlatform) => {
  if (newPlatform !== 'wechat') {
    searchText.value = ''
    filterCrawlerType.value = ''
    filterKeyword.value = ''
    filterNoteType.value = ''
    sortInfo.field = ''
    sortInfo.order = ''
    pagination.current = 1
    pagination.pageSize = 20
    pagination.total = 0
    
    // 加载筛选选项（小红书和快手）
    if (newPlatform === 'xhs' || newPlatform === 'ks') {
      loadFilterOptions()
    }
    // 加载数据
    loadData()
  }
}, { immediate: true })

watch(
  [currentPlatform, () => pagination.current, () => pagination.pageSize, filterCrawlerType, filterKeyword, filterNoteType, () => sortInfo.field, () => sortInfo.order],
  () => {
    if (currentPlatform.value !== 'wechat') {
      loadData()
    }
  }
)

const loadFilterOptions = async () => {
  try {
    const result = await crawlerApi.getFilterOptions(currentPlatform.value)
    filterOptions.keywords = result.keywords || []
    filterOptions.crawler_types = result.crawler_types || []
  } catch (error) {
    console.error('加载筛选选项失败:', error)
  }
}

const loadData = async (showMessage = false) => {
  try {
    loading.value = true
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: searchText.value
    }
    
    // 小红书和快手添加筛选参数
    if (currentPlatform.value === 'xhs' || currentPlatform.value === 'ks') {
      if (filterCrawlerType.value) {
        params.crawler_type = filterCrawlerType.value
      }
      if (filterKeyword.value) {
        params.source_keyword = filterKeyword.value
      }
      if (filterNoteType.value) {
        params.note_type = filterNoteType.value
      }
      if (sortInfo.field && sortInfo.order) {
        params.sort_field = sortInfo.field
        params.sort_order = sortInfo.order
      }
    }
    
    const result = await crawlerApi.getData(currentPlatform.value, params)
    data.value = result.data || []
    pagination.total = result.total || 0
    
    if (showMessage) {
      ElMessage.success('数据刷新成功')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadData(true)
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  searchText.value = ''
  if (currentPlatform.value === 'xhs' || currentPlatform.value === 'ks') {
    filterCrawlerType.value = ''
    filterKeyword.value = ''
    filterNoteType.value = ''
    sortInfo.field = ''
    sortInfo.order = ''
  }
  pagination.current = 1
  loadData()
}

const handleFilterChange = () => {
  pagination.current = 1
  loadData()
}

const handleSortChange = ({ prop, order }) => {
  if (order) {
    sortInfo.field = prop
    sortInfo.order = order === 'ascending' ? 'asc' : 'desc'
  } else {
    sortInfo.field = ''
    sortInfo.order = ''
  }
  loadData()
}

const handlePageChange = (page) => {
  pagination.current = page
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.current = 1
}

const loadComments = async (noteId, page = 1) => {
  try {
    commentsLoading.value = true
    const result = await crawlerApi.getComments(currentPlatform.value, noteId, {
      page: page,
      page_size: commentsPagination.pageSize
    })
    comments.value = result.comments || []
    commentsPagination.current = page
    commentsPagination.total = result.total || 0
  } catch (error) {
    console.error('加载评论失败:', error)
    ElMessage.error('加载评论失败: ' + (error.message || '未知错误'))
  } finally {
    commentsLoading.value = false
  }
}

const handleViewComments = (noteId) => {
  currentNoteId.value = noteId
  commentsModalVisible.value = true
  commentsPagination.current = 1
  commentsPagination.total = 0
  loadComments(noteId, 1)
}

const handleCommentsModalClose = () => {
  commentsModalVisible.value = false
  currentNoteId.value = null
  comments.value = []
}

const handleCommentsPageChange = (page) => {
  if (currentNoteId.value) {
    loadComments(currentNoteId.value, page)
  }
}

const handlePlatformChange = (value) => {
  currentPlatform.value = value
  // 更新路由
  if (value === 'wechat') {
    route.params.platform !== 'wechat' && router.replace('/crawler/data/wechat')
  } else {
    route.params.platform !== value && router.replace(`/crawler/data/${value}`)
  }
}
</script>

<style scoped>
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 500;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  border-radius: 4px;
}

:deep(.el-pagination) {
  display: flex;
}
</style>


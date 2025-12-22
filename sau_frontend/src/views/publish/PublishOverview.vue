<template>
  <div class="publish-overview">
    <div class="overview-header">
      <h2 class="page-title">发布中心总览</h2>
      <p class="page-subtitle">查看发布统计信息和数据概览</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="stat in stats" :key="stat.key">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" :style="{ background: stat.color }">
                <el-icon :size="24"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 发布类型统计 -->
    <el-card class="type-stats-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">发布类型统计</span>
          <el-button 
            type="text" 
            @click="refreshStats"
            :loading="loading"
            size="small"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="type-stats-content">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="type in contentTypeStats" :key="type.type">
            <div class="type-stat-item">
              <div class="type-stat-icon" :style="{ background: type.color }">
                <el-icon :size="32"><component :is="type.icon" /></el-icon>
              </div>
              <div class="type-stat-info">
                <div class="type-stat-value">{{ type.count }}</div>
                <div class="type-stat-label">{{ type.label }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 平台发布统计 -->
    <el-card class="platform-stats-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">平台发布统计</span>
        </div>
      </template>
      <div class="platform-stats-content">
        <el-table :data="platformStats" style="width: 100%">
          <el-table-column prop="platform" label="平台" width="120">
            <template #default="scope">
              <el-tag :type="getPlatformTagType(scope.row.platform)">
                {{ scope.row.platform }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total" label="总数" width="100" align="center" />
          <el-table-column prop="success" label="成功" width="100" align="center">
            <template #default="scope">
              <span style="color: #67c23a">{{ scope.row.success }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="failed" label="失败" width="100" align="center">
            <template #default="scope">
              <span style="color: #f56c6c">{{ scope.row.failed }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="pending" label="待发布" width="100" align="center">
            <template #default="scope">
              <span style="color: #e6a23c">{{ scope.row.pending }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="successRate" label="成功率" width="120" align="center">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.successRate" 
                :color="getSuccessRateColor(scope.row.successRate)"
                :stroke-width="8"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 最近发布记录 -->
    <el-card class="recent-records-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">最近发布记录</span>
          <el-button 
            type="text" 
            @click="$router.push('/publish/data-list')"
            size="small"
          >
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      <div class="recent-records-content">
        <el-table :data="recentRecords" style="width: 100%" v-loading="loading">
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column prop="content_type" label="类型" width="100">
            <template #default="scope">
              <el-tag :type="getContentTypeTagType(scope.row.content_type)">
                {{ getContentTypeLabel(scope.row.content_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="platform" label="平台" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.platform" type="success">
                {{ scope.row.platform }}
              </el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column prop="publish_status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                {{ getPublishStatusLabel(scope.row.publish_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button 
                type="text" 
                @click="$router.push({ path: '/publish/data-list', query: { id: scope.row.id } })"
                size="small"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document, Picture, VideoCamera, Promotion,
  Refresh, ArrowRight
} from '@element-plus/icons-vue'
import { resolveApiBaseUrl } from '@/utils/apiConfig'

const router = useRouter()
const loading = ref(false)

// 统计数据
const stats = ref([
  { key: 'total', label: '总发布数', value: 0, icon: Document, color: '#409eff' },
  { key: 'success', label: '成功发布', value: 0, icon: Promotion, color: '#67c23a' },
  { key: 'failed', label: '发布失败', value: 0, icon: Document, color: '#f56c6c' },
  { key: 'pending', label: '待发布', value: 0, icon: Document, color: '#e6a23c' }
])

// 内容类型统计
const contentTypeStats = ref([
  { type: 'image-text', label: '图文', count: 0, icon: Picture, color: '#409eff' },
  { type: 'video', label: '视频', count: 0, icon: VideoCamera, color: '#67c23a' },
  { type: 'article', label: '文章', count: 0, icon: Document, color: '#e6a23c' }
])

// 平台统计
const platformStats = ref([])

// 最近发布记录
const recentRecords = ref([])

const apiBaseUrl = resolveApiBaseUrl()

// 获取统计数据
const fetchStats = async () => {
  try {
    loading.value = true
    // 获取发布记录列表
    const response = await fetch(`${apiBaseUrl}/publish/records`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.code === 200 && result.data) {
      const records = Array.isArray(result.data) ? result.data : []
      
      // 计算总统计
      stats.value[0].value = records.length
      stats.value[1].value = records.filter(r => r.publish_status === 'success').length
      stats.value[2].value = records.filter(r => r.publish_status === 'failed').length
      stats.value[3].value = records.filter(r => r.publish_status === 'pending' || !r.publish_status).length

      // 计算内容类型统计
      contentTypeStats.value[0].count = records.filter(r => r.content_type === 'image-text').length
      contentTypeStats.value[1].count = records.filter(r => r.content_type === 'video').length
      contentTypeStats.value[2].count = records.filter(r => r.content_type === 'article').length

      // 计算平台统计
      const platformMap = {}
      records.forEach(record => {
        if (record.platform) {
          if (!platformMap[record.platform]) {
            platformMap[record.platform] = {
              platform: record.platform,
              total: 0,
              success: 0,
              failed: 0,
              pending: 0
            }
          }
          platformMap[record.platform].total++
          if (record.publish_status === 'success') {
            platformMap[record.platform].success++
          } else if (record.publish_status === 'failed') {
            platformMap[record.platform].failed++
          } else {
            platformMap[record.platform].pending++
          }
        }
      })

      platformStats.value = Object.values(platformMap).map(p => ({
        ...p,
        successRate: p.total > 0 ? Math.round((p.success / p.total) * 100) : 0
      }))

      // 最近发布记录（取前10条）
      recentRecords.value = records
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 10)
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新统计
const refreshStats = () => {
  fetchStats()
}

// 获取内容类型标签类型
const getContentTypeTagType = (type) => {
  const typeMap = {
    'image-text': 'primary',
    'video': 'success',
    'article': 'warning'
  }
  return typeMap[type] || 'info'
}

// 获取内容类型标签
const getContentTypeLabel = (type) => {
  const labelMap = {
    'image-text': '图文',
    'video': '视频',
    'article': '文章'
  }
  return labelMap[type] || type
}

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  return 'success'
}

// 获取发布状态标签类型
const getPublishStatusTagType = (status) => {
  const statusMap = {
    'success': 'success',
    'failed': 'danger',
    'pending': 'warning'
  }
  return statusMap[status] || 'info'
}

// 获取发布状态标签
const getPublishStatusLabel = (status) => {
  const labelMap = {
    'success': '已发布',
    'failed': '发布失败',
    'pending': '待发布'
  }
  return labelMap[status] || '未知'
}

// 获取成功率颜色
const getSuccessRateColor = (rate) => {
  if (rate >= 80) return '#67c23a'
  if (rate >= 50) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="scss" scoped>
.publish-overview {
  padding: 20px;

  .overview-header {
    margin-bottom: 24px;

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .stats-cards {
    margin-bottom: 24px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #303133;
            line-height: 1.2;
            margin-bottom: 4px;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .type-stats-card,
  .platform-stats-card,
  .recent-records-card {
    margin-bottom: 24px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    .type-stats-content {
      .type-stat-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        margin-bottom: 16px;
        transition: all 0.3s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
        }

        .type-stat-icon {
          width: 64px;
          height: 64px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .type-stat-info {
          flex: 1;

          .type-stat-value {
            font-size: 32px;
            font-weight: 600;
            color: #303133;
            line-height: 1.2;
            margin-bottom: 4px;
          }

          .type-stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }
}
</style>


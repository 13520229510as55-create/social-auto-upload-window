<template>
  <div class="crawler-dashboard">
    <h2 style="margin-bottom: 24px">爬虫总览</h2>
    
    <el-row :gutter="16" style="margin-bottom: 24px">
      <el-col :span="6">
        <el-card>
          <el-statistic
            title="总任务数"
            :value="stats.total_tasks || 0"
          >
            <template #prefix>
              <el-icon><Box /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic
            title="运行中任务"
            :value="stats.running_tasks || 0"
            :value-style="{ color: '#3f8600' }"
          >
            <template #prefix>
              <el-icon><VideoPlay /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic
            title="已完成任务"
            :value="(stats.total_tasks || 0) - (stats.running_tasks || 0)"
            :value-style="{ color: '#1890ff' }"
          >
            <template #prefix>
              <el-icon><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic
            title="平台数量"
            :value="Object.keys(stats.stats || {}).length"
          >
            <template #prefix>
              <el-icon><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <span>平台数据统计</span>
      </template>
      <el-table :data="platformStats" style="width: 100%" v-if="platformStats.length > 0">
        <el-table-column prop="platform" label="平台" width="150" />
        <el-table-column prop="dataCount" label="数据量" width="120">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.dataCount }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastCrawlTime" label="最后爬取时间" />
      </el-table>
      <el-empty v-else description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Box, VideoPlay, CircleCheck, Clock } from '@element-plus/icons-vue'
import crawlerApi from '@/api/crawler'
import { ElMessage } from 'element-plus'

const stats = ref({})
const loading = ref(true)
let intervalId = null

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

const platformStats = ref([])

const loadStats = async () => {
  try {
    loading.value = true
    const response = await crawlerApi.getDashboardStats()
    // axios 响应会自动解包，response 就是数据本身
    const data = response || {}
    stats.value = {
      total_tasks: data.total_tasks || 0,
      running_tasks: data.running_tasks || 0,
      stats: data.stats || {}
    }
    
    // 转换平台统计数据
    if (data.stats && Object.keys(data.stats).length > 0) {
      platformStats.value = Object.values(data.stats).map(stat => ({
        key: stat.name,
        platform: platformNames[stat.name] || stat.name,
        dataCount: stat.data_count || 0,
        lastCrawlTime: stat.last_crawl_time || '暂无'
      }))
    } else {
      platformStats.value = []
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败: ' + (error.response?.data?.error || error.message || '未知错误'))
    // 设置默认值避免页面崩溃
    stats.value = { total_tasks: 0, running_tasks: 0, stats: {} }
    platformStats.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  // 每30秒刷新一次
  intervalId = setInterval(loadStats, 30000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<style scoped>
.crawler-dashboard {
  padding: 20px;
}
</style>


<template>
  <div class="production-overview">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">制作中心总览</span>
          <el-button 
            type="primary" 
            :icon="RefreshRight" 
            @click="loadStats"
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="总数据量" :value="stats.totalData">
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="总素材数" :value="stats.totalMaterials">
              <template #prefix>
                <el-icon><Picture /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="图片素材" :value="stats.imageMaterials">
              <template #prefix>
                <el-icon><PictureFilled /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="视频素材" :value="stats.videoMaterials">
              <template #prefix>
                <el-icon><VideoCamera /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>平台数据统计</span>
            </template>
            <p>各平台爬取的数据统计信息，可在"数据列表"中查看详情。</p>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>素材统计</span>
            </template>
            <p>素材管理统计信息，可在"素材管理"中查看和管理素材。</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  RefreshRight, Document, Picture, PictureFilled, VideoCamera 
} from '@element-plus/icons-vue'

const loading = ref(false)
const stats = ref({
  totalData: 0,
  totalMaterials: 0,
  imageMaterials: 0,
  videoMaterials: 0
})

const loadStats = async () => {
  try {
    loading.value = true
    // TODO: 调用后端API获取统计数据
    // const result = await api.get('/production/stats')
    // stats.value = result.data
    ElMessage.success('统计数据已刷新')
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.production-overview {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .card-title {
      font-size: 18px;
      font-weight: 600;
    }
  }
  
  .stat-card {
    text-align: center;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
}
</style>





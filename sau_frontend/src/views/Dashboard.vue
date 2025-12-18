<template>
  <div class="dashboard">
    <div class="dashboard-content">
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <!-- 账号统计卡片 -->
        <el-col :span="6">
          <div class="stat-card card-1">
            <div class="stat-card-bg"></div>
            <div class="stat-card-content">
              <div class="stat-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ accountStats.total }}</div>
                <div class="stat-label">账号总数</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-item success">
                <span class="dot"></span>
                <span>正常 {{ accountStats.normal }}</span>
              </div>
              <div class="stat-item error">
                <span class="dot"></span>
                <span>异常 {{ accountStats.abnormal }}</span>
              </div>
            </div>
          </div>
        </el-col>
        
        <!-- 平台统计卡片 -->
        <el-col :span="6">
          <div class="stat-card card-2">
            <div class="stat-card-bg"></div>
            <div class="stat-card-content">
              <div class="stat-icon">
                <el-icon><Platform /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ platformStats.total }}</div>
                <div class="stat-label">平台总数</div>
              </div>
            </div>
            <div class="stat-footer platforms">
              <el-tooltip content="快手" placement="top">
                <div class="platform-badge">{{ platformStats.kuaishou }}</div>
              </el-tooltip>
              <el-tooltip content="抖音" placement="top">
                <div class="platform-badge">{{ platformStats.douyin }}</div>
              </el-tooltip>
              <el-tooltip content="视频号" placement="top">
                <div class="platform-badge">{{ platformStats.channels }}</div>
              </el-tooltip>
              <el-tooltip content="小红书" placement="top">
                <div class="platform-badge">{{ platformStats.xiaohongshu }}</div>
              </el-tooltip>
            </div>
          </div>
        </el-col>
        
        <!-- 任务统计卡片 -->
        <el-col :span="6">
          <div class="stat-card card-3">
            <div class="stat-card-bg"></div>
            <div class="stat-card-content">
              <div class="stat-icon">
                <el-icon><List /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ taskStats.total }}</div>
                <div class="stat-label">任务总数</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-item success">
                <span class="dot"></span>
                <span>完成 {{ taskStats.completed }}</span>
              </div>
              <div class="stat-item warning">
                <span class="dot"></span>
                <span>进行中 {{ taskStats.inProgress }}</span>
              </div>
              <div class="stat-item error">
                <span class="dot"></span>
                <span>失败 {{ taskStats.failed }}</span>
              </div>
            </div>
          </div>
        </el-col>
        
        <!-- 内容统计卡片 -->
        <el-col :span="6">
          <div class="stat-card card-4">
            <div class="stat-card-bg"></div>
            <div class="stat-card-content">
              <div class="stat-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ contentStats.total }}</div>
                <div class="stat-label">内容总数</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-item success">
                <span class="dot"></span>
                <span>已发布 {{ contentStats.published }}</span>
              </div>
              <div class="stat-item info">
                <span class="dot"></span>
                <span>草稿 {{ contentStats.draft }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 快捷操作区域 -->
      <div class="quick-actions">
        <div class="section-header">
          <h2>
            <el-icon><Star /></el-icon>
            快捷操作
          </h2>
        </div>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="action-card" @click="navigateTo('/account-management')">
              <div class="action-card-bg"></div>
              <div class="action-content">
                <div class="action-icon icon-1">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="action-title">账号管理</div>
                <div class="action-desc">管理所有平台账号</div>
                <div class="action-arrow">
                  <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="action-card" @click="navigateTo('/material-management')">
              <div class="action-card-bg"></div>
              <div class="action-content">
                <div class="action-icon icon-2">
                  <el-icon><Upload /></el-icon>
                </div>
                <div class="action-title">内容上传</div>
                <div class="action-desc">上传视频和图文内容</div>
                <div class="action-arrow">
                  <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="action-card" @click="navigateTo('/publish-center')">
              <div class="action-card-bg"></div>
              <div class="action-content">
                <div class="action-icon icon-3">
                  <el-icon><Timer /></el-icon>
                </div>
                <div class="action-title">定时发布</div>
                <div class="action-desc">设置内容发布时间</div>
                <div class="action-arrow">
                  <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="action-card">
              <div class="action-card-bg"></div>
              <div class="action-content">
                <div class="action-icon icon-4">
                  <el-icon><DataAnalysis /></el-icon>
                </div>
                <div class="action-title">数据分析</div>
                <div class="action-desc">查看内容数据分析</div>
                <div class="action-arrow">
                  <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 最近任务列表 -->
      <div class="recent-tasks">
        <div class="section-header">
          <h2>
            <el-icon><Clock /></el-icon>
            最近任务
          </h2>
          <el-button type="primary" link @click="navigateTo('/publish-center')">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        
        <div class="tasks-table-wrapper">
          <el-table :data="recentTasks" class="modern-table">
            <el-table-column prop="title" label="任务名称" min-width="200">
              <template #default="scope">
                <div class="task-name">
                  <el-icon><Document /></el-icon>
                  <span>{{ scope.row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="platform" label="平台" width="120">
              <template #default="scope">
                <el-tag
                  :type="getPlatformTagType(scope.row.platform)"
                  effect="light"
                  round
                >
                  {{ scope.row.platform }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="account" label="账号" width="150" />
            <el-table-column prop="createTime" label="创建时间" width="180">
              <template #default="scope">
                <div class="time-info">
                  <el-icon><Clock /></el-icon>
                  <span>{{ scope.row.createTime }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag
                  :type="getStatusTagType(scope.row.status)"
                  effect="light"
                  round
                >
                  <el-icon v-if="scope.row.status === '已完成'"><CircleCheck /></el-icon>
                  <el-icon v-else-if="scope.row.status === '进行中'"><Loading /></el-icon>
                  <el-icon v-else-if="scope.row.status === '已失败'"><CircleClose /></el-icon>
                  <el-icon v-else><Clock /></el-icon>
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button size="small" @click="viewTaskDetail(scope.row)">
                    <el-icon><View /></el-icon>
                    查看
                  </el-button>
                  <el-button 
                    size="small" 
                    type="primary" 
                    v-if="scope.row.status === '待执行'"
                    @click="executeTask(scope.row)"
                  >
                    <el-icon><VideoPlay /></el-icon>
                    执行
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    v-if="scope.row.status !== '已完成' && scope.row.status !== '已失败'"
                    @click="cancelTask(scope.row)"
                  >
                    <el-icon><Close /></el-icon>
                    取消
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, UserFilled, Platform, List, Document, 
  Upload, Timer, DataAnalysis, Odometer, Star,
  Clock, ArrowRight, CircleCheck, CircleClose,
  Loading, View, VideoPlay, Close
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 账号统计数据
const accountStats = reactive({
  total: 12,
  normal: 10,
  abnormal: 2
})

// 平台统计数据
const platformStats = reactive({
  total: 4,
  kuaishou: 3,
  douyin: 4,
  channels: 2,
  xiaohongshu: 3
})

// 任务统计数据
const taskStats = reactive({
  total: 24,
  completed: 18,
  inProgress: 5,
  failed: 1
})

// 内容统计数据
const contentStats = reactive({
  total: 36,
  published: 30,
  draft: 6
})

// 最近任务数据
const recentTasks = ref([
  {
    id: 1,
    title: '快手视频自动发布',
    platform: '快手',
    account: '快手账号1',
    createTime: '2024-05-01 10:30:00',
    status: '已完成'
  },
  {
    id: 2,
    title: '抖音视频定时发布',
    platform: '抖音',
    account: '抖音账号1',
    createTime: '2024-05-01 11:15:00',
    status: '进行中'
  },
  {
    id: 3,
    title: '视频号内容上传',
    platform: '视频号',
    account: '视频号账号1',
    createTime: '2024-05-01 14:20:00',
    status: '待执行'
  },
  {
    id: 4,
    title: '小红书图文发布',
    platform: '小红书',
    account: '小红书账号1',
    createTime: '2024-05-01 16:45:00',
    status: '已失败'
  },
  {
    id: 5,
    title: '快手短视频批量上传',
    platform: '快手',
    account: '快手账号2',
    createTime: '2024-05-02 09:10:00',
    status: '待执行'
  }
])

// 根据平台获取标签类型
const getPlatformTagType = (platform) => {
  const typeMap = {
    '快手': 'success',
    '抖音': 'danger',
    '视频号': 'warning',
    '小红书': 'info'
  }
  return typeMap[platform] || 'info'
}

// 根据状态获取标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    '已完成': 'success',
    '进行中': 'warning',
    '待执行': 'info',
    '已失败': 'danger'
  }
  return typeMap[status] || 'info'
}

// 导航到指定路由
const navigateTo = (path) => {
  router.push(path)
}

// 查看任务详情
const viewTaskDetail = (task) => {
  ElMessage.info(`查看任务: ${task.title}`)
  // 实际应用中应该跳转到任务详情页面
}

// 执行任务
const executeTask = (task) => {
  ElMessageBox.confirm(
    `确定要执行任务 ${task.title} 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    }
  )
    .then(() => {
      // 更新任务状态
      const index = recentTasks.value.findIndex(t => t.id === task.id)
      if (index !== -1) {
        recentTasks.value[index].status = '进行中'
      }
      ElMessage({
        type: 'success',
        message: '任务已开始执行',
      })
    })
    .catch(() => {
      // 取消执行
    })
}

// 取消任务
const cancelTask = (task) => {
  ElMessageBox.confirm(
    `确定要取消任务 ${task.title} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      // 更新任务状态
      const index = recentTasks.value.findIndex(t => t.id === task.id)
      if (index !== -1) {
        recentTasks.value[index].status = '已取消'
      }
      ElMessage({
        type: 'success',
        message: '任务已取消',
      })
    })
    .catch(() => {
      // 取消操作
    })
}
</script>

<style lang="scss" scoped>
.dashboard {
  min-height: 100%;
  animation: fadeIn 0.6s ease-out;
  
  // 统计卡片行
  .stats-row {
    margin-bottom: 32px;
  }
  
  // 统计卡片
  .stat-card {
    position: relative;
    background: white;
    border-radius: 16px;
    padding: 24px;
    height: 160px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    animation: slideUp 0.6s ease-out backwards;
    
    @for $i from 1 through 4 {
      &:nth-child(#{$i}) {
        animation-delay: #{$i * 0.1}s;
      }
    }
    
    &:hover {
      transform: translateY(-8px);
      box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
      
      .stat-card-bg {
        opacity: 1;
      }
    }
    
    .stat-card-bg {
      position: absolute;
      top: 0;
      right: 0;
      width: 120px;
      height: 120px;
      opacity: 0.5;
      transition: opacity 0.3s ease;
    }
    
    &.card-1 .stat-card-bg {
      background: radial-gradient(circle, rgba(102, 126, 234, 0.15), transparent 70%);
    }
    
    &.card-2 .stat-card-bg {
      background: radial-gradient(circle, rgba(52, 211, 153, 0.15), transparent 70%);
    }
    
    &.card-3 .stat-card-bg {
      background: radial-gradient(circle, rgba(251, 146, 60, 0.15), transparent 70%);
    }
    
    &.card-4 .stat-card-bg {
      background: radial-gradient(circle, rgba(59, 130, 246, 0.15), transparent 70%);
    }
    
    .stat-card-content {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      position: relative;
      z-index: 1;
      
      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        
        .el-icon {
          font-size: 28px;
          color: white;
        }
      }
      
      .stat-info {
        flex: 1;
        
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          line-height: 1;
          margin-bottom: 6px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #64748b;
          font-weight: 500;
        }
      }
    }
    
    &.card-1 {
      .stat-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      }
      .stat-value {
        color: #667eea;
      }
    }
    
    &.card-2 {
      .stat-icon {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        box-shadow: 0 4px 12px rgba(52, 211, 153, 0.3);
      }
      .stat-value {
        color: #10b981;
      }
    }
    
    &.card-3 {
      .stat-icon {
        background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
        box-shadow: 0 4px 12px rgba(251, 146, 60, 0.3);
      }
      .stat-value {
        color: #f97316;
      }
    }
    
    &.card-4 {
      .stat-icon {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
      }
      .stat-value {
        color: #2563eb;
      }
    }
    
    .stat-footer {
      border-top: 1px solid rgba(0, 0, 0, 0.06);
      padding-top: 12px;
      display: flex;
      gap: 16px;
      position: relative;
      z-index: 1;
      
      &.platforms {
        justify-content: space-around;
      }
      
      .stat-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        
        .dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
        }
        
        &.success .dot {
          background: #10b981;
        }
        
        &.warning .dot {
          background: #f59e0b;
        }
        
        &.error .dot {
          background: #ef4444;
        }
        
        &.info .dot {
          background: #3b82f6;
        }
      }
      
      .platform-badge {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 600;
        color: #667eea;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          transform: scale(1.1);
        }
      }
    }
  }
  
  // 快捷操作
  .quick-actions {
    margin: 32px 0;
    animation: slideUp 0.6s ease-out 0.4s backwards;
    
    .section-header {
      margin-bottom: 20px;
      
      h2 {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        
        .el-icon {
          font-size: 22px;
          color: #667eea;
        }
      }
    }
    
    .action-card {
      position: relative;
      background: white;
      border-radius: 16px;
      padding: 28px 24px;
      height: 180px;
      overflow: hidden;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      
      .action-card-bg {
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        opacity: 0;
        transition: all 0.4s ease;
      }
      
      &:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        
        .action-card-bg {
          opacity: 0.15;
        }
        
        .action-arrow {
          opacity: 1;
          transform: translateX(0);
        }
      }
      
      .action-content {
        position: relative;
        z-index: 1;
        height: 100%;
        display: flex;
        flex-direction: column;
        
        .action-icon {
          width: 56px;
          height: 56px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 16px;
          
          .el-icon {
            font-size: 28px;
            color: white;
          }
          
          &.icon-1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
          }
          
          &.icon-2 {
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
            box-shadow: 0 4px 12px rgba(52, 211, 153, 0.3);
          }
          
          &.icon-3 {
            background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
            box-shadow: 0 4px 12px rgba(251, 146, 60, 0.3);
          }
          
          &.icon-4 {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          }
        }
        
        .action-title {
          font-size: 18px;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 8px;
        }
        
        .action-desc {
          font-size: 14px;
          color: #64748b;
          line-height: 1.5;
        }
        
        .action-arrow {
          position: absolute;
          bottom: 0;
          right: 0;
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          opacity: 0;
          transform: translateX(-10px);
          transition: all 0.3s ease;
        }
      }
    }
  }
  
  // 最近任务
  .recent-tasks {
    margin-top: 32px;
    animation: slideUp 0.6s ease-out 0.5s backwards;
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      h2 {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        
        .el-icon {
          font-size: 22px;
          color: #667eea;
        }
      }
      
      .el-button {
        font-weight: 600;
        
        .el-icon {
          margin-left: 4px;
        }
      }
    }
    
    .tasks-table-wrapper {
      background: white;
      border-radius: 16px;
      padding: 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      overflow: hidden;
      
      :deep(.modern-table) {
        .el-table__header {
          th {
            background: #f8fafc;
            color: #64748b;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
          }
        }
        
        .el-table__row {
          transition: all 0.3s ease;
          
          &:hover {
            background: rgba(102, 126, 234, 0.03);
          }
          
          td {
            border: none;
            padding: 16px 12px;
          }
        }
        
        .task-name {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          
          .el-icon {
            color: #667eea;
            font-size: 16px;
          }
        }
        
        .time-info {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #64748b;
          font-size: 14px;
          
          .el-icon {
            font-size: 14px;
          }
        }
        
        .el-tag {
          font-weight: 500;
          border: none;
          padding: 6px 12px;
          
          .el-icon {
            margin-right: 4px;
          }
        }
        
        .action-buttons {
          display: flex;
          gap: 8px;
          
          .el-button {
            border-radius: 8px;
            font-weight: 500;
            
            .el-icon {
              margin-right: 4px;
            }
          }
        }
      }
    }
  }
}

// 动画
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式
@media (max-width: 1200px) {
  .dashboard {
    .stat-card {
      height: 180px;
    }
    
    .action-card {
      height: 200px;
    }
  }
}
</style>
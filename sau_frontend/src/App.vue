<template>
  <div id="app">
    <!-- 登录页面：全屏显示，无布局 -->
    <router-view v-if="isLoginPage" />
    
    <!-- 主应用布局：仅在已登录时显示 -->
    <el-container v-else>
      <el-aside :width="isCollapse ? '80px' : '240px'">
        <div class="sidebar">
          <!-- Logo 区域 -->
          <div class="logo-section">
            <div class="logo-wrapper">
              <div class="logo-icon" v-show="!isCollapse">
                <el-icon :size="32"><VideoCamera /></el-icon>
              </div>
              <div class="logo-icon-collapsed" v-show="isCollapse">
                <el-icon :size="28"><VideoCamera /></el-icon>
              </div>
            </div>
            <div class="logo-text" v-show="!isCollapse">
              <h2 class="logo-title">AutoPost-Ai</h2>
              <p class="logo-subtitle">社媒运营平台</p>
            </div>
          </div>

          <!-- 菜单区域 -->
          <el-menu
            :router="true"
            :default-active="activeMenu"
            :default-openeds="defaultOpenedMenus"
            :collapse="isCollapse"
            :collapse-transition="false"
            class="sidebar-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <template #title>
                <span>首页</span>
              </template>
            </el-menu-item>
            
            <!-- 账号管理已移动到发布中心 > 配置管理，暂时隐藏 -->
            <!--
            <el-menu-item index="/account-management">
              <el-icon><User /></el-icon>
              <template #title>
                <span>账号管理</span>
              </template>
            </el-menu-item>
            -->
            
            <!-- 爬虫管理菜单（手风琴展开） -->
            <el-sub-menu index="/crawler">
              <template #title>
                <el-icon><Grid /></el-icon>
                <span>爬虫管理</span>
              </template>
              
              <!-- 总览（一级菜单项，直接显示） -->
              <el-menu-item index="/crawler/dashboard">
                <el-icon><Odometer /></el-icon>
                <span>总览</span>
              </el-menu-item>
              
              <!-- 配置管理（二级菜单） -->
              <el-menu-item index="/crawler/config">
                <el-icon><Setting /></el-icon>
                <span>配置管理</span>
              </el-menu-item>
              
              <!-- 任务管理（二级菜单） -->
              <el-menu-item index="/crawler/tasks">
                <el-icon><VideoPlay /></el-icon>
                <span>任务管理</span>
              </el-menu-item>
              
              <!-- 数据列表（二级菜单） -->
              <el-menu-item index="/crawler/data">
                <el-icon><DataBoard /></el-icon>
                <span>数据列表</span>
              </el-menu-item>
              
              <!-- 热点中心（二级菜单，最后一个） -->
              <el-menu-item index="/crawler/hotspot-center">
                <el-icon><TrendCharts /></el-icon>
                <span>热点中心</span>
              </el-menu-item>
            </el-sub-menu>
            
            <!-- 制作中心菜单（手风琴展开） -->
            <el-sub-menu index="/production">
              <template #title>
                <el-icon><Tools /></el-icon>
                <span>制作中心</span>
              </template>
              
              <!-- 总览（一级菜单项，直接显示） -->
              <el-menu-item index="/production/overview">
                <el-icon><Odometer /></el-icon>
                <span>总览</span>
            </el-menu-item>
              
              <!-- 素材管理（二级菜单） -->
              <el-menu-item index="/production/materials">
                <el-icon><Picture /></el-icon>
                <span>素材管理</span>
              </el-menu-item>
              
              <!-- 数据列表（二级菜单） -->
              <el-menu-item index="/production/data">
                <el-icon><DataBoard /></el-icon>
                <span>数据列表</span>
              </el-menu-item>
            </el-sub-menu>
            
            <!-- 发布中心菜单（手风琴展开） -->
            <el-sub-menu index="/publish">
              <template #title>
                <el-icon><Upload /></el-icon>
                <span>发布中心</span>
              </template>
              
              <!-- 总览（一级菜单项，直接显示） -->
              <el-menu-item index="/publish/overview">
                <el-icon><Odometer /></el-icon>
                <span>总览</span>
              </el-menu-item>
              
              <!-- 配置管理（二级菜单） -->
              <el-menu-item index="/publish/config">
                <el-icon><Setting /></el-icon>
                <span>配置管理</span>
              </el-menu-item>
              
              <!-- 数据列表（二级菜单） -->
              <el-menu-item index="/publish/data-list">
                <el-icon><DataBoard /></el-icon>
                <span>数据列表</span>
              </el-menu-item>
            </el-sub-menu>
            
            <el-menu-item index="/website">
              <el-icon><Monitor /></el-icon>
              <template #title>
                <span>网站</span>
              </template>
            </el-menu-item>
            
            <el-menu-item index="/data">
              <el-icon><DataAnalysis /></el-icon>
              <template #title>
                <span>数据</span>
              </template>
            </el-menu-item>
          </el-menu>

          <!-- 折叠按钮 -->
          <div class="collapse-btn" @click="toggleSidebar">
            <el-icon :size="18">
              <DArrowLeft v-if="!isCollapse" />
              <DArrowRight v-else />
            </el-icon>
          </div>
        </div>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-content">
            <div class="header-left">
              <el-icon class="toggle-sidebar" @click="toggleSidebar"><Fold /></el-icon>
            </div>
            <div class="header-center" v-if="getPageTitle(route.path)">
              <div class="page-title-header">
                <span class="title-icon-header">
                  <el-icon><component :is="getPageIcon(route.path)" /></el-icon>
                </span>
                <span class="title-text-header">{{ getPageTitle(route.path) }}</span>
              </div>
            </div>
            <div class="header-right">
              <el-dropdown @command="handleCommand">
                <div class="user-dropdown">
                  <el-avatar :size="32" :style="{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                  <span class="username">{{ userStore.userInfo.nickname || userStore.userInfo.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item disabled>
                      <el-icon><User /></el-icon>
                      <span>{{ userStore.userInfo.username }}</span>
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      <span>退出登录</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view :key="route.fullPath" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  HomeFilled, User, Monitor, DataAnalysis, 
  Fold, Picture, Upload, ArrowDown, SwitchButton,
  DArrowLeft, DArrowRight, VideoCamera, Promotion,
  Odometer, UserFilled, FolderOpened, Tools, TrendCharts,
  Grid, Setting, VideoPlay, DataBoard
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 判断是否为登录页面
const isLoginPage = computed(() => {
  return route.path === '/login'
})

// 默认展开的子菜单
const defaultOpenedMenus = computed(() => {
  const path = route.path || route.fullPath.replace(/#/g, '')
  const opened = []
  if (path.startsWith('/crawler/')) {
    opened.push('/crawler')
  }
  if (path.startsWith('/publish/')) {
    opened.push('/publish')
  }
  if (path.startsWith('/production/')) {
    opened.push('/production')
  }
  return opened
})

// 当前激活的菜单项
const activeMenu = computed(() => {
  // 确保路由路径正确匹配，包括 hash 模式
  let path = route.path || route.fullPath.replace(/#/g, '')
  // 处理爬虫管理路由，确保子路由也能正确激活父菜单
  if (path.startsWith('/crawler/')) {
    // 对于子路由，返回父路由路径以激活父菜单
    if (path !== '/crawler/dashboard' && path !== '/crawler/config' && path !== '/crawler/tasks' && path !== '/crawler/data' && path !== '/crawler/hotspot-center') {
      // 带参数的路由，提取基础路径
      if (path.startsWith('/crawler/config/')) {
        return '/crawler/config'
      }
      if (path.startsWith('/crawler/data/')) {
        return '/crawler/data'
      }
    }
  }
  // 处理制作中心路由，确保子路由也能正确激活父菜单
  if (path.startsWith('/production/')) {
    // 对于子路由，返回父路由路径以激活父菜单
    if (path !== '/production/overview' && path !== '/production/materials' && path !== '/production/data') {
      // 带参数的路由，提取基础路径
      if (path.startsWith('/production/materials/')) {
        return '/production/materials'
      }
      if (path.startsWith('/production/data/')) {
        return '/production/data'
      }
    }
  }
  // 处理发布中心路由，确保子路由也能正确激活父菜单
  if (path.startsWith('/publish/')) {
    // 对于子路由，返回父路由路径以激活父菜单
    if (path !== '/publish/overview' && path !== '/publish/config' && path !== '/publish/data-list') {
      // 带参数的路由，提取基础路径
      if (path.startsWith('/publish/config/')) {
        return '/publish/config'
      }
      if (path.startsWith('/publish/data-list/')) {
        return '/publish/data-list'
      }
    }
  }
  return path
})

// 侧边栏折叠状态
const isCollapse = ref(false)

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

/**
 * 根据路由路径获取页面标题
 */
const getPageTitle = (path) => {
  const titleMap = {
    '/': '工作台',
    '/account-management': '账号管理',
    '/material-management': '素材管理',
    '/publish-center': '发布中心',
    '/production-center': '制作中心',
    '/hotspot-center': '热点中心',
    '/crawler/dashboard': '爬虫总览',
    '/crawler/config': '配置管理',
    '/crawler/tasks': '任务管理',
    '/crawler/data': '数据列表',
    '/crawler/hotspot-center': '热点中心',
    '/publish/overview': '发布中心总览',
    '/publish/config': '配置管理',
    '/publish/data-list': '数据列表',
    '/production/overview': '制作中心总览',
    '/production/materials': '素材管理',
    '/production/data': '数据列表'
  }
  // 处理带参数的路由
  if (path.startsWith('/crawler/config')) return '配置管理'
  if (path.startsWith('/crawler/data')) return '数据列表'
  if (path.startsWith('/crawler/hotspot-center')) return '热点中心'
  if (path.startsWith('/publish/config')) return '配置管理'
  if (path.startsWith('/publish/data-list')) return '数据列表'
  if (path.startsWith('/production/materials')) return '素材管理'
  if (path.startsWith('/production/data')) return '数据列表'
  return titleMap[path] || null
}

/**
 * 根据路由路径获取页面图标
 */
const getPageIcon = (path) => {
  const iconMap = {
    '/': Odometer,
    '/account-management': UserFilled,
    '/material-management': FolderOpened,
    '/publish-center': Promotion,
    '/production-center': Tools,
    '/hotspot-center': TrendCharts,
    '/crawler/dashboard': Odometer,
    '/crawler/config': Setting,
    '/crawler/tasks': VideoPlay,
    '/crawler/data': DataBoard,
    '/crawler/hotspot-center': TrendCharts,
    '/publish/overview': Odometer,
    '/publish/config': Setting,
    '/publish/data-list': DataBoard,
    '/production/overview': Odometer,
    '/production/materials': Picture,
    '/production/data': DataBoard
  }
  // 处理带参数的路由
  if (path.startsWith('/crawler/config')) return Setting
  if (path.startsWith('/crawler/data')) return DataBoard
  if (path.startsWith('/crawler/hotspot-center')) return TrendCharts
  if (path.startsWith('/publish/config')) return Setting
  if (path.startsWith('/publish/data-list')) return DataBoard
  if (path.startsWith('/production/materials')) return Picture
  if (path.startsWith('/production/data')) return DataBoard
  return iconMap[path] || null
}

/**
 * 处理菜单选择
 */
const handleMenuSelect = (index) => {
  // 强制路由跳转，确保内容更新
  if (index !== route.path) {
    router.push(index).catch(err => {
      // 忽略重复导航错误
      if (err.name !== 'NavigationDuplicated') {
        console.error('路由跳转错误:', err)
      }
    })
  }
}

/**
 * 处理下拉菜单命令
 */
const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm(
        '确定要退出登录吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 执行退出登录
      userStore.logout()
      
      ElMessage.success('已退出登录')
      
      // 跳转到登录页
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

#app {
  min-height: 100vh;
  
  // 登录页面时不需要任何限制
  > .login-container {
    height: 100vh;
    width: 100vw;
  }
}

.el-container {
  height: 100vh;
}

.el-aside {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: #fff;
  height: 100vh;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: radial-gradient(circle at top left, rgba(102, 126, 234, 0.15), transparent 60%);
    pointer-events: none;
  }
  
  .sidebar {
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    z-index: 1;
    
    // Logo 区域
    .logo-section {
      padding: 24px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      margin-bottom: 16px;
      
      .logo-wrapper {
        .logo-icon {
          width: 48px;
          height: 48px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          transition: all 0.3s ease;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
          }
        }
        
        .logo-icon-collapsed {
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          margin: 0 auto;
        }
      }
      
      .logo-text {
        flex: 1;
        
        .logo-title {
          font-size: 16px;
          font-weight: 700;
          background: linear-gradient(135deg, #fff 0%, #e2e8f0 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin: 0 0 4px 0;
          line-height: 1.2;
        }
        
        .logo-subtitle {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.6);
          margin: 0;
          font-weight: 500;
        }
      }
    }
    
    // 菜单样式
    .sidebar-menu {
      border-right: none;
      flex: 1;
      background: transparent;
      padding: 0 12px;
      overflow-y: auto;
      
      &::-webkit-scrollbar {
        width: 4px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
      }
      
      :deep(.el-menu-item) {
        height: 48px;
        line-height: 48px;
        margin-bottom: 4px;
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.85);
        background: transparent;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 0;
          bottom: 0;
          width: 3px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          transform: scaleY(0);
          transition: transform 0.3s ease;
        }
        
        .el-icon {
          font-size: 20px;
          color: rgba(255, 255, 255, 0.7);
          transition: all 0.3s ease;
        }
        
        span {
          font-size: 14px;
          font-weight: 500;
          transition: all 0.3s ease;
        }
        
        &:hover {
          background: rgba(102, 126, 234, 0.15);
          color: #fff;
          
          .el-icon {
            color: #667eea;
            transform: scale(1.1);
          }
        }
        
        &.is-active {
          background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.15) 100%);
          color: #fff;
          box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
          
          &::before {
            transform: scaleY(1);
          }
          
          .el-icon {
            color: #667eea;
          }
          
          span {
            font-weight: 600;
          }
        }
      }
      
      // 子菜单样式
      :deep(.el-sub-menu) {
        margin-bottom: 4px;
        
        .el-sub-menu__title {
          height: 48px;
          line-height: 48px;
          border-radius: 10px;
          color: rgba(255, 255, 255, 0.85);
          background: transparent;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
          
          &::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transform: scaleY(0);
            transition: transform 0.3s ease;
          }
          
          .el-icon {
            font-size: 20px;
            color: rgba(255, 255, 255, 0.7);
            transition: all 0.3s ease;
          }
          
          span {
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
          }
          
          &:hover {
            background: rgba(102, 126, 234, 0.15);
            color: #fff;
            
            .el-icon {
              color: #667eea;
              transform: scale(1.1);
            }
          }
        }
        
        // 子菜单打开状态
        &.is-opened {
          > .el-sub-menu__title {
            background: rgba(102, 126, 234, 0.1);
            color: #fff;
            
            .el-icon {
              color: #667eea;
            }
          }
        }
        
        // 子菜单项样式（继承父级样式）
        .el-menu {
          background: transparent;
          
          .el-menu-item {
            height: 48px;
            line-height: 48px;
            margin-bottom: 4px;
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.85);
            background: transparent;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            padding-left: 48px !important;
            
            &::before {
              content: '';
              position: absolute;
              left: 0;
              top: 0;
              bottom: 0;
              width: 3px;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              transform: scaleY(0);
              transition: transform 0.3s ease;
            }
            
            .el-icon {
              font-size: 20px;
              color: rgba(255, 255, 255, 0.7);
              transition: all 0.3s ease;
            }
            
            span {
              font-size: 14px;
              font-weight: 500;
              transition: all 0.3s ease;
            }
            
            &:hover {
              background: rgba(102, 126, 234, 0.15);
              color: #fff;
              
              .el-icon {
                color: #667eea;
                transform: scale(1.1);
              }
            }
            
            &.is-active {
              background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.15) 100%);
              color: #fff;
              box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
              
              &::before {
                transform: scaleY(1);
              }
              
              .el-icon {
                color: #667eea;
              }
              
              span {
                font-weight: 600;
              }
            }
          }
        }
      }
      
      // 折叠状态下的菜单项
      &.el-menu--collapse {
        :deep(.el-menu-item) {
          padding: 0;
          display: flex;
          justify-content: center;
          
          .el-icon {
            margin-right: 0;
          }
        }
      }
    }
    
    // 折叠按钮
    .collapse-btn {
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      cursor: pointer;
      color: rgba(255, 255, 255, 0.6);
      transition: all 0.3s ease;
      background: rgba(255, 255, 255, 0.02);
      
      &:hover {
        background: rgba(102, 126, 234, 0.15);
        color: #667eea;
        
        .el-icon {
          transform: scale(1.2);
        }
      }
      
      .el-icon {
        transition: transform 0.3s ease;
      }
    }
  }
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0;
  height: 60px;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    padding: 0 16px;
    position: relative;
    
    .header-left {
      .toggle-sidebar {
        font-size: 20px;
        cursor: pointer;
        color: $text-regular;
        
        &:hover {
          color: $primary-color;
        }
      }
    }
    
    .header-center {
      position: absolute;
      left: 50px;
      top: 50%;
      transform: translateY(-50%);
      display: flex;
      align-items: center;
      
      .page-title-header {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .title-icon-header {
          width: 32px;
          height: 32px;
          background: #6366f1;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          
          .el-icon {
            font-size: 18px;
          }
        }
        
        .title-text-header {
          font-size: 24px;
          font-weight: 600;
          color: #0f172a;
          letter-spacing: -0.02em;
        }
      }
    }
    
    .header-right {
      .user-dropdown {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        padding: 4px 12px;
        border-radius: 8px;
        transition: all 0.3s ease;
        
        &:hover {
          background-color: rgba(102, 126, 234, 0.1);
        }
        
        .username {
          color: $text-regular;
          font-size: 14px;
          font-weight: 500;
        }
        
        .el-icon {
          font-size: 12px;
          color: $text-secondary;
          transition: transform 0.3s ease;
        }
        
        &:hover .el-icon:last-child {
          transform: translateY(2px);
        }
      }
    }
  }
}

.el-main {
  background-color: $bg-color-page;
  padding: 20px;
  overflow-y: auto;
}
</style>

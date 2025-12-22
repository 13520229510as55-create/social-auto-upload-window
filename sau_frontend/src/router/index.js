import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import Dashboard from '../views/Dashboard.vue'
import AccountManagement from '../views/AccountManagement.vue'
import MaterialManagement from '../views/MaterialManagement.vue'
import PublishCenter from '../views/PublishCenter.vue'
import ProductionCenter from '../views/ProductionCenter.vue'
import HotspotCenter from '../views/HotspotCenter.vue'
import About from '../views/About.vue'
import Login from '../views/Login.vue'

// 发布中心相关组件
import PublishOverview from '../views/publish/PublishOverview.vue'
import PublishConfig from '../views/publish/PublishConfig.vue'
import PublishDataList from '../views/publish/PublishDataList.vue'

// 爬虫管理相关组件
import CrawlerDashboard from '../views/crawler/CrawlerDashboard.vue'
import CrawlerConfig from '../views/crawler/CrawlerConfig.vue'
import CrawlerTasks from '../views/crawler/CrawlerTasks.vue'
import CrawlerData from '../views/crawler/CrawlerData.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: '登录'
    }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: '工作台'
    }
  },
  {
    path: '/account-management',
    name: 'AccountManagement',
    component: AccountManagement,
    meta: {
      requiresAuth: true,
      title: '账号管理'
    }
  },
  // 发布中心路由
  {
    path: '/publish/overview',
    name: 'PublishOverview',
    component: PublishOverview,
    meta: {
      requiresAuth: true,
      title: '发布中心总览'
    }
  },
  {
    path: '/publish/config',
    name: 'PublishConfig',
    component: PublishConfig,
    meta: {
      requiresAuth: true,
      title: '配置管理'
    }
  },
  {
    path: '/publish/data-list',
    name: 'PublishDataList',
    component: PublishDataList,
    meta: {
      requiresAuth: true,
      title: '数据列表'
    }
  },
  // 制作中心路由
  {
    path: '/production/overview',
    name: 'ProductionOverview',
    component: () => import('../views/production/ProductionOverview.vue'),
    meta: {
      requiresAuth: true,
      title: '制作中心总览'
    }
  },
  {
    path: '/production/materials',
    name: 'ProductionMaterials',
    component: MaterialManagement,
    meta: {
      requiresAuth: true,
      title: '素材管理'
    }
  },
  {
    path: '/production/data',
    name: 'ProductionData',
    component: ProductionCenter,
    meta: {
      requiresAuth: true,
      title: '数据列表'
    }
  },
  // 保留旧路由以兼容，重定向到新路由
  {
    path: '/material-management',
    redirect: '/production/materials'
  },
  {
    path: '/publish-center',
    redirect: '/publish/overview'
  },
  {
    path: '/production-center',
    redirect: '/production/overview'
  },
  // 热点中心已移动到爬虫管理下
  {
    path: '/crawler/hotspot-center',
    name: 'HotspotCenter',
    component: HotspotCenter,
    meta: {
      requiresAuth: true,
      title: '热点中心'
    }
  },
  // 保留旧路由以兼容，重定向到新路由
  {
    path: '/hotspot-center',
    redirect: '/crawler/hotspot-center'
  },
  // 爬虫管理路由
  {
    path: '/crawler/dashboard',
    name: 'CrawlerDashboard',
    component: CrawlerDashboard,
    meta: {
      requiresAuth: true,
      title: '爬虫总览'
    }
  },
  {
    path: '/crawler/config/:platform?',
    name: 'CrawlerConfig',
    component: CrawlerConfig,
    meta: {
      requiresAuth: true,
      title: '配置管理'
    }
  },
  {
    path: '/crawler/tasks',
    name: 'CrawlerTasks',
    component: CrawlerTasks,
    meta: {
      requiresAuth: true,
      title: '任务管理'
    }
  },
  {
    path: '/crawler/data/:platform?',
    name: 'CrawlerData',
    component: CrawlerData,
    meta: {
      requiresAuth: true,
      title: '数据列表'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      requiresAuth: true,
      title: '关于'
    }
  }
]

const router = createRouter({
  history: createWebHashHistory('/app'),
  routes
})

/**
 * 路由守卫：检查登录状态
 */
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 社交媒体自动发布平台` : '社交媒体自动发布平台'
  
  // 检查登录状态
  userStore.checkLoginStatus()
  
  // 如果需要登录但用户未登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    console.log('⚠️ 未登录，跳转到登录页')
    next({
      path: '/login',
      query: { redirect: to.fullPath }  // 保存目标路由，登录后跳转
    })
  } 
  // 如果已登录但访问登录页，跳转到首页
  else if (to.path === '/login' && userStore.isLoggedIn) {
    console.log('✅ 已登录，跳转到首页')
    next({ path: '/' })
  } 
  // 其他情况正常访问
  else {
    next()
  }
})

export default router
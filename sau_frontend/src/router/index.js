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
  {
    path: '/material-management',
    name: 'MaterialManagement',
    component: MaterialManagement,
    meta: {
      requiresAuth: true,
      title: '素材管理'
    }
  },
  {
    path: '/publish-center',
    name: 'PublishCenter',
    component: PublishCenter,
    meta: {
      requiresAuth: true,
      title: '发布中心'
    }
  },
  {
    path: '/production-center',
    name: 'ProductionCenter',
    component: ProductionCenter,
    meta: {
      requiresAuth: true,
      title: '制作中心'
    }
  },
  {
    path: '/hotspot-center',
    name: 'HotspotCenter',
    component: HotspotCenter,
    meta: {
      requiresAuth: true,
      title: '热点中心'
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
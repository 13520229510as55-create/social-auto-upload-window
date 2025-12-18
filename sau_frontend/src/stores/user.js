import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'sau_user_info'
const TOKEN_KEY = 'sau_token'

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 恢复登录状态
  const storedUser = localStorage.getItem(STORAGE_KEY)
  const storedToken = localStorage.getItem(TOKEN_KEY)
  
  const userInfo = ref(storedUser ? JSON.parse(storedUser) : {
    username: '',
    nickname: '',
    role: ''
  })
  
  const token = ref(storedToken || '')
  const isLoggedIn = ref(!!storedToken)
  
  /**
   * 登录
   * @param {Object} info - 用户信息
   * @param {boolean} remember - 是否记住登录状态
   */
  const login = (info, remember = true) => {
    userInfo.value = {
      username: info.username || '',
      nickname: info.nickname || info.username || '',
      role: info.role || 'user'
    }
    
    // 生成简单的token（实际项目中应该从后端获取）
    const newToken = `sau_${Date.now()}_${Math.random().toString(36).substr(2)}`
    token.value = newToken
    isLoggedIn.value = true
    
    if (remember) {
      // 持久化存储
      localStorage.setItem(STORAGE_KEY, JSON.stringify(userInfo.value))
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      // 仅在会话期间有效
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(userInfo.value))
      sessionStorage.setItem(TOKEN_KEY, newToken)
    }
    
    console.log('✅ 用户已登录:', userInfo.value)
  }
  
  /**
   * 设置用户信息（兼容旧方法）
   */
  const setUserInfo = (info) => {
    login(info, true)
  }
  
  /**
   * 登出
   */
  const logout = () => {
    userInfo.value = {
      username: '',
      nickname: '',
      role: ''
    }
    token.value = ''
    isLoggedIn.value = false
    
    // 清除存储
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(STORAGE_KEY)
    sessionStorage.removeItem(TOKEN_KEY)
    
    console.log('✅ 用户已登出')
  }
  
  /**
   * 检查登录状态
   */
  const checkLoginStatus = () => {
    const localToken = localStorage.getItem(TOKEN_KEY)
    const sessionToken = sessionStorage.getItem(TOKEN_KEY)
    
    if (localToken || sessionToken) {
      const storedUserInfo = localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY)
      if (storedUserInfo) {
        userInfo.value = JSON.parse(storedUserInfo)
        token.value = localToken || sessionToken
        isLoggedIn.value = true
        return true
      }
    }
    
    return false
  }
  
  return {
    userInfo,
    token,
    isLoggedIn,
    login,
    setUserInfo,
    logout,
    checkLoginStatus
  }
})
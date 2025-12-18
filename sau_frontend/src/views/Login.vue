<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <el-icon :size="48"><VideoCamera /></el-icon>
          </div>
        </div>
        <h1 class="title">
          <span class="title-main">AutoPost Ai</span>
          <span class="title-sub">全自动社媒运营平台</span>
        </h1>
        <p class="subtitle">欢迎回来，请登录您的账户</p>
      </div>

      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item class="remember-row">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="login-button"
          :loading="loading"
          @click="handleLogin"
        >
          <span v-if="!loading">登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form>
    </div>

    <!-- 装饰元素 -->
    <div class="decoration-elements">
      <div class="deco-circle deco-1"></div>
      <div class="deco-circle deco-2"></div>
      <div class="deco-circle deco-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, VideoCamera } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: true
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

/**
 * 处理登录
 */
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    
    loading.value = true

    // 模拟登录延迟
    await new Promise(resolve => setTimeout(resolve, 800))

    // 简单的登录验证（实际项目中应该调用后端API）
    if (loginForm.username === 'zhaoll01' && loginForm.password === '15831929073asAS') {
      // 保存登录状态
      userStore.login({
        username: loginForm.username,
        nickname: '赵老师',
        role: 'admin'
      }, loginForm.remember)

      ElMessage.success({
        message: '🎉 登录成功！欢迎回来',
        duration: 2000
      })

      // 跳转到首页或之前访问的页面
      const redirect = router.currentRoute.value.query.redirect || '/'
      setTimeout(() => {
        router.push(redirect)
      }, 500)
    } else {
      ElMessage.error('用户名或密码错误')
    }
  } catch (error) {
    if (error !== false) {
      console.error('登录验证失败:', error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  padding: 20px;
}

// 动态背景
.animated-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  
  .gradient-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.6;
    animation: float 20s infinite ease-in-out;
    
    &.orb-1 {
      width: 500px;
      height: 500px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      top: -250px;
      left: -250px;
      animation-delay: 0s;
    }
    
    &.orb-2 {
      width: 400px;
      height: 400px;
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      bottom: -200px;
      right: -200px;
      animation-delay: -7s;
    }
    
    &.orb-3 {
      width: 350px;
      height: 350px;
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation-delay: -14s;
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

// 装饰元素
.decoration-elements {
  position: absolute;
  inset: 0;
  pointer-events: none;
  
  .deco-circle {
    position: absolute;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    animation: rotate 30s linear infinite;
    
    &.deco-1 {
      width: 400px;
      height: 400px;
      top: 10%;
      left: 5%;
      animation-duration: 25s;
    }
    
    &.deco-2 {
      width: 300px;
      height: 300px;
      bottom: 15%;
      right: 10%;
      animation-duration: 35s;
      animation-direction: reverse;
    }
    
    &.deco-3 {
      width: 200px;
      height: 200px;
      top: 60%;
      left: 15%;
      animation-duration: 20s;
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 登录卡片
.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  .logo-wrapper {
    display: flex;
    justify-content: center;
    margin-bottom: 24px;
    
    .logo-icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
      animation: pulse 2s ease-in-out infinite;
    }
  }
  
  .title {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    margin: 0 0 12px 0;
    
    .title-main {
      font-size: 36px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: 2px;
    }
    
    .title-sub {
      font-size: 18px;
      font-weight: 600;
      color: #64748b;
      letter-spacing: 1px;
    }
  }
  
  .subtitle {
    font-size: 14px;
    color: #64748b;
    margin: 0;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
    
    .el-input__wrapper {
      border-radius: 12px;
      padding: 12px 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      transition: all 0.3s ease;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      }
      
      &.is-focus {
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
    }
    
    .el-input__inner {
      font-size: 15px;
    }
  }
  
  .remember-row {
    margin-bottom: 32px;
    
    :deep(.el-checkbox__label) {
      color: #64748b;
      font-size: 14px;
    }
  }
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  margin-top: 32px;
  
  .tips {
    text-align: center;
    font-size: 13px;
    color: #64748b;
    margin: 0;
    padding: 16px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    
    .el-icon {
      color: #667eea;
      font-size: 16px;
    }
    
    strong {
      color: #667eea;
      font-weight: 600;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .login-card {
    padding: 36px 28px;
    border-radius: 20px;
  }
  
  .login-header {
    .title {
      font-size: 24px;
    }
    
    .logo-wrapper .logo-icon {
      width: 64px;
      height: 64px;
      
      .el-icon {
        font-size: 36px;
      }
    }
  }
  
  .decoration-elements .deco-circle {
    display: none;
  }
}
</style>


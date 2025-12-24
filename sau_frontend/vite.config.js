import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 移除自动导入，改用@use语法
      }
    }
  },
  server: {
    host: '0.0.0.0',  // 监听所有网络接口，允许外部访问
    port: 5173,
    open: true,
    // 允许的主机名列表
    allowedHosts: ['yutt.xyz'],
    // 优化开发服务器性能
    hmr: {
      overlay: true
    },
    // 启用文件系统缓存
    fs: {
      strict: false
    },
    proxy: {
      // crawler API 保持 /api/crawler 前缀
      '/api/crawler': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false
      },
      // production 和 publish API 需要移除 /api 前缀
      '/api/production': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/publish': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // hotspot API 需要移除 /api 前缀
      '/api/hotspot': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // getFiles, getAccounts, getValidAccounts 等需要移除 /api 前缀
      '/api/getFiles': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/getAccounts': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/getValidAccounts': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // 账号管理相关 API 需要移除 /api 前缀
      '/api/deleteAccount': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/addAccountDirect': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/updateUserinfo': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/account': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/login': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/manualConfirmLogin': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/postVideo': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/postImageText': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/postVideoBatch': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/uploadCookie': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/downloadCookie': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/generateImageText': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/deleteFile': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/upload': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/uploadSave': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/getFile': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/saveGoogleStorageMaterial': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/getGoogleFilePublicUrl': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // 其他 /api 路由保持原样
      '/api': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false
      }
    }
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'element-plus'],
    exclude: []
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1600,
    // 使用相对路径，适配根路径和子路径部署
    base: './',
    rollupOptions: {
      output: {
        // 简化分包策略
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          elementPlus: ['element-plus'],
          utils: ['axios']
        }
      }
    }
  }
})

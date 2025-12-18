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
      '/api': {
        target: 'http://localhost:5409',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
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

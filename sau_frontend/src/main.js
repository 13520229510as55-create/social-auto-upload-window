import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.scss'

const app = createApp(App)

// 只注册实际使用的图标，而不是所有图标（大幅减少初始加载时间）
// 收集所有组件中使用的图标
import {
  // App.vue
  HomeFilled, User, Monitor, DataAnalysis, Fold, Picture, Upload,
  ArrowDown, SwitchButton, DArrowLeft, DArrowRight, VideoCamera, Promotion, Tools, TrendCharts,
  // PublishCenter.vue
  Plus, Close, Folder, Document, Check, CircleCheckFilled,
  // AccountManagement.vue
  Refresh, CircleCloseFilled, Download, Loading, UserFilled, Edit, Delete,
  // MaterialManagement.vue
  FolderOpened,
  // Login.vue
  Lock,
  // Dashboard.vue
  Timer, Odometer, Star, Clock, ArrowRight, CircleCheck, CircleClose, View, VideoPlay,
  // Home.vue
  Lightning, Setting
} from '@element-plus/icons-vue'

const icons = {
  HomeFilled, User, Monitor, DataAnalysis, Fold, Picture, Upload,
  ArrowDown, SwitchButton, DArrowLeft, DArrowRight, VideoCamera, Promotion, Tools, TrendCharts,
  Plus, Close, Folder, Document, Check, CircleCheckFilled,
  Refresh, CircleCloseFilled, Download, Loading, UserFilled, Edit, Delete,
  FolderOpened, Lock, Timer, Odometer, Star, Clock, ArrowRight, CircleCheck, CircleClose, View, VideoPlay,
  Lightning, Setting
}

// 注册图标组件
Object.keys(icons).forEach(key => {
  app.component(key, icons[key])
})

app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.mount('#app')

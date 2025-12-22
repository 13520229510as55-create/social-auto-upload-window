<template>
  <div>
    <h2 style="margin-bottom: 24px">配置管理</h2>
    <el-tabs v-model="currentPlatform" @tab-change="handlePlatformChange">
      <el-tab-pane
        v-for="platform in platforms"
        :key="platform.value"
        :label="platform.label"
        :name="platform.value"
      >
        <el-form
          ref="formRef"
          :model="formData"
          label-width="150px"
          label-position="left"
        >
          <el-card title="登录状态" style="margin-bottom: 16px">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>登录状态</span>
                <el-space>
                  <el-tag v-if="hasCookie" type="success">已登录</el-tag>
                  <el-tag v-else type="danger">未登录</el-tag>
                  <el-button
                    v-if="hasCookie"
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="handleDeleteCookie"
                  >
                    清除Cookie
                  </el-button>
                  <QRCodeLogin
                    :platform="currentPlatform"
                    @success="handleLoginSuccess"
                  />
                </el-space>
              </div>
            </template>
            
            <el-form-item label="登录方式">
              <el-select v-model="formData.login_type">
                <el-option label="二维码登录" value="qrcode" />
                <el-option label="Cookie登录" value="cookie" />
                <el-option label="手机号登录" value="phone" />
              </el-select>
            </el-form-item>
          </el-card>

          <el-card title="基础配置" style="margin-bottom: 16px">
            <el-form-item label="爬取类型">
              <el-select v-model="formData.crawler_type">
                <el-option label="关键词搜索" value="search" />
                <el-option label="指定帖子详情" value="detail" />
                <el-option label="创作者主页" value="creator" />
              </el-select>
            </el-form-item>

            <el-form-item label="关键词（搜索模式）">
              <el-input
                v-model="formData.keywords"
                placeholder="多个关键词用英文逗号分隔"
              />
            </el-form-item>

            <el-form-item label="起始页数">
              <el-input-number v-model="formData.start_page" :min="1" />
            </el-form-item>

            <el-form-item label="最大爬取数量">
              <el-input-number v-model="formData.max_notes_count" :min="1" />
            </el-form-item>

            <el-form-item label="数据保存格式">
              <el-select v-model="formData.save_data_option">
                <el-option label="JSON" value="json" />
                <el-option label="CSV" value="csv" />
                <el-option label="Excel" value="excel" />
                <el-option label="数据库" value="db" />
                <el-option label="SQLite" value="sqlite" />
              </el-select>
            </el-form-item>
          </el-card>

          <el-card title="评论配置" style="margin-bottom: 16px">
            <el-form-item label="是否爬取评论">
              <el-switch v-model="formData.enable_get_comments" />
            </el-form-item>

            <el-form-item label="单帖子最大评论数">
              <el-input-number v-model="formData.max_comments_count" :min="0" />
            </el-form-item>
          </el-card>

          <el-card title="其他配置" style="margin-bottom: 16px">
            <el-form-item label="是否爬取媒体文件">
              <el-switch v-model="formData.enable_get_medias" />
            </el-form-item>

            <el-form-item label="无头模式">
              <el-switch v-model="formData.headless" />
            </el-form-item>
          </el-card>

          <el-card v-if="currentPlatform === 'xhs'" title="小红书特定配置" style="margin-bottom: 16px">
            <el-form-item label="指定笔记URL列表（每行一个）">
              <el-input
                v-model="formData.specified_urls"
                type="textarea"
                :rows="4"
                placeholder="请输入完整的笔记URL，每行一个"
              />
            </el-form-item>

            <el-form-item label="指定创作者ID列表（每行一个）">
              <el-input
                v-model="formData.creator_ids"
                type="textarea"
                :rows="4"
                placeholder="请输入完整的创作者URL，每行一个"
              />
            </el-form-item>
          </el-card>

          <el-card>
            <el-button
              type="primary"
              :icon="Check"
              @click="handleSave"
              :loading="loading"
              size="large"
            >
              保存配置
            </el-button>
          </el-card>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="公众号" name="wechat">
        <WechatAccountManager />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import crawlerApi from '@/api/crawler'
import QRCodeLogin from './QRCodeLogin.vue'
import WechatAccountManager from './WechatAccountManager.vue'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const platforms = ref([])
const currentPlatform = ref(route.params.platform || 'xhs')
const loading = ref(false)
const hasCookie = ref(false)

const formData = reactive({
  login_type: 'qrcode',
  crawler_type: 'search',
  keywords: '',
  start_page: 1,
  max_notes_count: 15,
  enable_get_comments: true,
  max_comments_count: 10,
  enable_get_medias: false,
  headless: false,
  save_data_option: 'json',
  specified_urls: '',
  creator_ids: ''
})

onMounted(async () => {
  await loadPlatforms()
  // 如果有路由参数，加载对应平台的配置
  if (route.params.platform) {
    currentPlatform.value = route.params.platform
    if (route.params.platform !== 'wechat') {
      await loadConfig(route.params.platform)
      await checkCookie(route.params.platform)
    }
  } else {
    // 默认加载第一个平台
    if (platforms.value.length > 0 && platforms.value[0].value !== 'wechat') {
      currentPlatform.value = platforms.value[0].value
      await loadConfig(platforms.value[0].value)
      await checkCookie(platforms.value[0].value)
    }
  }
})

watch(currentPlatform, (newPlatform) => {
  if (newPlatform && newPlatform !== 'wechat') {
    if (route.params.platform !== newPlatform) {
      router.replace(`/crawler/config/${newPlatform}`)
    }
    loadConfig(newPlatform)
    checkCookie(newPlatform)
  } else if (newPlatform === 'wechat') {
    if (route.params.platform !== 'wechat') {
      router.replace('/crawler/config/wechat')
    }
  }
})

const loadPlatforms = async () => {
  try {
    const response = await crawlerApi.getPlatforms()
    // axios 响应会自动解包
    const data = response
    platforms.value = data.platforms || []
    // 如果没有平台数据，设置默认平台
    if (platforms.value.length === 0) {
      platforms.value = [
        { value: 'xhs', label: '小红书' },
        { value: 'dy', label: '抖音' },
        { value: 'ks', label: '快手' },
        { value: 'bili', label: 'B站' },
        { value: 'wb', label: '微博' },
        { value: 'tieba', label: '百度贴吧' },
        { value: 'zhihu', label: '知乎' },
        { value: 'wechat', label: '公众号' }
      ]
    }
  } catch (error) {
    console.error('加载平台列表失败:', error)
    ElMessage.error('加载平台列表失败: ' + (error.response?.data?.error || error.message || '未知错误'))
    // 设置默认平台
    platforms.value = [
      { value: 'xhs', label: '小红书' },
      { value: 'dy', label: '抖音' },
      { value: 'ks', label: '快手' },
      { value: 'bili', label: 'B站' },
      { value: 'wb', label: '微博' },
      { value: 'tieba', label: '百度贴吧' },
      { value: 'zhihu', label: '知乎' },
      { value: 'wechat', label: '公众号' }
    ]
  }
}

const loadConfig = async (platform) => {
  try {
    loading.value = true
    const response = await crawlerApi.getConfig(platform)
    // axios 响应会自动解包
    const data = response
    if (data && Object.keys(data).length > 0) {
      Object.assign(formData, {
        ...data,
        specified_urls: Array.isArray(data.specified_urls) ? data.specified_urls.join('\n') : (data.specified_urls || ''),
        creator_ids: Array.isArray(data.creator_ids) ? data.creator_ids.join('\n') : (data.creator_ids || '')
      })
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败: ' + (error.response?.data?.error || error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const checkCookie = async (platform) => {
  try {
    const data = await crawlerApi.getCookie(platform)
    hasCookie.value = data.has_cookie
  } catch (error) {
    hasCookie.value = false
  }
}

const handleSave = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    const configData = {
      platform: currentPlatform.value,
      keywords: formData.keywords || '',
      login_type: formData.login_type || 'qrcode',
      crawler_type: formData.crawler_type || 'search',
      start_page: formData.start_page || 1,
      max_notes_count: formData.max_notes_count || 15,
      enable_get_comments: formData.enable_get_comments !== false,
      max_comments_count: formData.max_comments_count || 10,
      enable_get_medias: formData.enable_get_medias || false,
      headless: formData.headless || false,
      save_data_option: formData.save_data_option || 'json',
      specified_urls: formData.specified_urls ? formData.specified_urls.split('\n').filter(Boolean) : [],
      creator_ids: formData.creator_ids ? formData.creator_ids.split('\n').filter(Boolean) : [],
      platform_specific: {}
    }

    await crawlerApi.saveConfig(currentPlatform.value, configData)
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handlePlatformChange = (value) => {
  currentPlatform.value = value
}

const handleLoginSuccess = () => {
  hasCookie.value = true
  ElMessage.success('登录成功，Cookie已保存')
}

const handleDeleteCookie = async () => {
  try {
    const response = await crawlerApi.deleteCookie(currentPlatform.value)
    if (response.success) {
      hasCookie.value = false
      ElMessage.success('Cookie已清除')
    } else {
      ElMessage.warning(response.message || '清除失败')
    }
  } catch (error) {
    ElMessage.error('清除Cookie失败: ' + (error.message || '未知错误'))
  }
}
</script>

<style scoped>
</style>


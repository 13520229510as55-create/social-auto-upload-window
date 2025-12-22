/**
 * MediaCrawler API 接口
 * 文件位置：sau_frontend/src/api/crawler.js
 */
import request from '@/utils/request'

const crawlerApi = {
  /**
   * 总览统计
   */
  getDashboardStats() {
    return request.get('/crawler/dashboard/stats')
  },

  /**
   * 平台列表
   */
  getPlatforms() {
    return request.get('/crawler/platforms')
  },

  /**
   * 配置管理
   */
  getConfig(platform) {
    return request.get(`/crawler/config/${platform}`)
  },
  saveConfig(platform, config) {
    return request.post(`/crawler/config/${platform}`, config)
  },

  /**
   * 登录相关
   */
  getQRCode(platform, force = false) {
    return request.post('/crawler/login/qrcode', null, {
      params: { platform, force }
    })
  },
  checkLoginStatus(qrcodeId) {
    return request.get(`/crawler/login/status/${qrcodeId}`)
  },
  getCookie(platform) {
    return request.get(`/crawler/login/cookie/${platform}`)
  },
  deleteCookie(platform) {
    return request.delete(`/crawler/login/cookie/${platform}`)
  },

  /**
   * 任务管理
   */
  getTasks() {
    return request.get('/crawler/tasks')
  },
  startTask(taskData) {
    return request.post('/crawler/tasks/start', taskData)
  },
  stopTask(taskId) {
    return request.delete(`/crawler/tasks/${taskId}`)
  },

  /**
   * 数据列表
   */
  getData(platform, params) {
    return request.get(`/crawler/data/${platform}`, { params })
  },
  getComments(platform, noteId, params) {
    return request.get(`/crawler/data/${platform}/comments/${noteId}`, { params })
  },
  getFilterOptions(platform) {
    return request.get(`/crawler/data/${platform}/filter-options`)
  },

  /**
   * 微信公众号相关
   */
  // 账号管理
  getWechatAccounts() {
    return request.get('/crawler/wechat/accounts')
  },
  addWechatAccount(accountData) {
    return request.post('/crawler/wechat/accounts', accountData)
  },
  updateWechatAccountStatus(accountId, status) {
    return request.put(`/crawler/wechat/accounts/${accountId}/status`, { status })
  },
  deleteWechatAccount(accountId) {
    return request.delete(`/crawler/wechat/accounts/${accountId}`)
  },
  
  // 登录相关
  createWechatLoginUrl() {
    return request.post('/crawler/wechat/login/create-url')
  },
  getWechatLoginResult(uuid) {
    return request.get(`/crawler/wechat/login/result/${uuid}`)
  },
  
  // 订阅源管理
  getWechatFeeds() {
    return request.get('/crawler/wechat/feeds')
  },
  addWechatFeed(feedData) {
    return request.post('/crawler/wechat/feeds', feedData)
  },
  refreshWechatFeed(feedId) {
    return request.post(`/crawler/wechat/feeds/${feedId}/refresh`)
  },
  getWechatHistoryArticles(feedId) {
    return request.post(`/crawler/wechat/feeds/${feedId}/history`)
  },
  updateWechatFeedStatus(feedId, status) {
    return request.put(`/crawler/wechat/feeds/${feedId}/status`, { status })
  },
  deleteWechatFeed(feedId) {
    return request.delete(`/crawler/wechat/feeds/${feedId}`)
  },
  
  // 公众号信息
  getWechatMpInfo(wxsLink) {
    return request.post('/crawler/wechat/mp/info', { wxs_link: wxsLink })
  },
  
  // 文章列表
  getWechatArticles(params) {
    return request.get('/crawler/wechat/articles', { params })
  },
  
  // 历史文章进度
  getWechatHistoryProgress() {
    return request.get('/crawler/wechat/feeds/history/progress')
  }
}

export default crawlerApi


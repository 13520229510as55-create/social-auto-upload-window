/**
 * 统一的 API 基础 URL 解析工具
 * 确保所有组件使用相同的逻辑，避免重复添加 /api 前缀等问题
 * 
 * 使用规则：
 * 1. yutt.xyz 域名：强制使用 /api（相对路径）
 * 2. localhost/127.0.0.1：忽略环境变量，使用 /api（相对路径）
 * 3. 其他情况：根据环境变量决定
 * 4. 自动检测并避免重复添加 /api 前缀
 */

/**
 * 解析 API 基础 URL
 * @returns {string} API 基础 URL（不包含尾部斜杠）
 */
export function resolveApiBaseUrl() {
  const API_PATH_PREFIX = import.meta.env.VITE_API_PATH_PREFIX || '/api'
  const hostname = typeof window !== 'undefined' ? window.location.hostname : ''
  
  // 规则 1: yutt.xyz 域名，强制使用 /api（相对路径），忽略所有环境变量
  // 这是最重要的规则，必须优先检查，避免环境变量干扰
  if (hostname === 'yutt.xyz' || hostname === 'www.yutt.xyz' || hostname.includes('yutt.xyz')) {
    return '/api'
  }
  
  let API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  
  // 规则 2: localhost/127.0.0.1，忽略环境变量，使用相对路径
  if (API_BASE_URL && (API_BASE_URL.includes('localhost') || API_BASE_URL.includes('127.0.0.1'))) {
    return API_PATH_PREFIX
  }
  
  // 规则 3: 如果设置了环境变量且不是 localhost
  if (API_BASE_URL) {
    // 确保不以 / 结尾
    if (API_BASE_URL.endsWith('/')) {
      API_BASE_URL = API_BASE_URL.slice(0, -1)
    }
    
    // 规则 4: 检查是否已经包含 /api，避免重复添加
    const normalizedPrefix = API_PATH_PREFIX.replace(/\/$/, '') // 移除尾部斜杠
    if (API_BASE_URL.endsWith('/api') || API_BASE_URL.endsWith(normalizedPrefix)) {
      // 如果环境变量是完整URL且包含 /api，直接返回（用于非yutt.xyz域名）
      // 如果是相对路径且包含 /api，也直接返回
      return API_BASE_URL
    }
    
    // 如果是完整 URL（http/https），通常不需要添加 /api（后端直接监听在端口上）
    if (API_BASE_URL.startsWith('http://') || API_BASE_URL.startsWith('https://')) {
      return API_BASE_URL
    }
    
    // 相对路径，添加 /api 前缀
    return `${API_BASE_URL}${API_PATH_PREFIX}`
  }
  
  // 默认：使用相对路径
  return API_PATH_PREFIX
}

/**
 * 构建完整的 API URL
 * @param {string} path - API 路径（如 '/production/records'）
 * @returns {string} 完整的 API URL
 */
export function buildApiUrl(path) {
  const baseUrl = resolveApiBaseUrl()
  // 确保 path 以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  // 确保 baseUrl 不以 / 结尾（避免双斜杠）
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl
  return `${normalizedBase}${normalizedPath}`
}

/**
 * 获取 API 路径前缀（用于 axios baseURL 等场景）
 * @returns {string} API 路径前缀
 */
export function getApiPathPrefix() {
  return import.meta.env.VITE_API_PATH_PREFIX || '/api'
}


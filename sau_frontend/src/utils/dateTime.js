/**
 * 时间工具函数 - 统一使用北京时间（UTC+8）
 */

/**
 * 获取当前北京时间
 * @returns {Date} 北京时间对象
 */
export function getBeijingTime() {
  const now = new Date()
  // 获取 UTC 时间戳
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60 * 1000)
  // 转换为北京时间（UTC+8）
  const beijingTime = new Date(utcTime + (8 * 60 * 60 * 1000))
  return beijingTime
}

/**
 * 格式化日期为北京时间字符串（ISO 8601 格式，带时区）
 * @returns {string} 格式化的时间字符串，例如：2024-01-01T12:00:00.000+08:00
 */
export function formatDateWithOffset() {
  const date = getBeijingTime()
  const pad = (num, size = 2) => String(num).padStart(size, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  const seconds = pad(date.getSeconds())
  const milliseconds = pad(date.getMilliseconds(), 3)
  // 固定使用 +08:00（北京时间）
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}+08:00`
}

/**
 * 格式化日期为本地化字符串（北京时间）
 * @param {Date|string} date - 日期对象或日期字符串
 * @param {object} options - 格式化选项
 * @returns {string} 格式化的时间字符串
 */
export function formatLocalDateTime(date, options = {}) {
  const beijingDate = date instanceof Date ? date : new Date(date)
  // 转换为北京时间
  const utcTime = beijingDate.getTime() + (beijingDate.getTimezoneOffset() * 60 * 1000)
  const beijingTime = new Date(utcTime + (8 * 60 * 60 * 1000))
  
  const defaultOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai',
    ...options
  }
  
  return beijingTime.toLocaleString('zh-CN', defaultOptions)
}

/**
 * 格式化日期为中文格式（北京时间）
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 格式化的时间字符串，例如：2024年1月1日
 */
export function formatChineseDate(date) {
  if (!date) return '刚刚'
  const beijingDate = date instanceof Date ? date : new Date(date)
  if (Number.isNaN(beijingDate.getTime())) return date
  
  // 转换为北京时间
  const utcTime = beijingDate.getTime() + (beijingDate.getTimezoneOffset() * 60 * 1000)
  const beijingTime = new Date(utcTime + (8 * 60 * 60 * 1000))
  
  return `${beijingTime.getFullYear()}年${beijingTime.getMonth() + 1}月${beijingTime.getDate()}日`
}

/**
 * 获取当前北京时间的 ISO 字符串
 * @returns {string} ISO 格式的时间字符串
 */
export function getBeijingTimeISOString() {
  return getBeijingTime().toISOString()
}

/**
 * 将任意日期转换为北京时间
 * @param {Date|string|number} date - 日期对象、字符串或时间戳
 * @returns {Date} 北京时间对象
 */
export function toBeijingTime(date) {
  const inputDate = date instanceof Date ? date : new Date(date)
  // 获取 UTC 时间戳
  const utcTime = inputDate.getTime() + (inputDate.getTimezoneOffset() * 60 * 1000)
  // 转换为北京时间（UTC+8）
  return new Date(utcTime + (8 * 60 * 60 * 1000))
}





import { http } from '@/utils/request'
import axios from 'axios'
import { buildApiUrl } from '@/utils/apiConfig'

// 素材管理API
export const materialApi = {
  // 获取所有素材
  getAllMaterials: () => {
    return http.get('/getFiles')
  },
  
  // 上传素材
  uploadMaterial: (formData, onUploadProgress) => {
    // 使用http.upload方法，它已经配置了正确的Content-Type
    return http.upload('/uploadSave', formData, onUploadProgress)
  },
  
  // 删除素材
  deleteMaterial: (id) => {
    return http.get(`/deleteFile?id=${id}`)
  },
  
  // 下载素材
  downloadMaterial: (filePath) => {
    return buildApiUrl(`/download/${filePath}`)
  },
  
  // 获取素材预览URL
  getMaterialPreviewUrl: (filename) => {
    return buildApiUrl(`/getFile?filename=${filename}`)
  },
  
  // 获取文件MIME类型
  getFileMimeType: (filename) => {
    const ext = filename.toLowerCase().split('.').pop()
    const mimeTypes = {
      'mp4': 'video/mp4',
      'avi': 'video/x-msvideo',
      'mov': 'video/quicktime',
      'wmv': 'video/x-ms-wmv',
      'flv': 'video/x-flv',
      'mkv': 'video/x-matroska',
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'bmp': 'image/bmp',
      'webp': 'image/webp'
    }
    return mimeTypes[ext] || 'application/octet-stream'
  },
  
  // 上传到谷歌存储（使用Google Cloud Storage API分步上传）
  uploadToGoogleStorage: async function(file, filename, onUploadProgress) {
    const bucketName = 'n8n-test-3344'
    const accessToken = 'AIzaSyBWj4raKG-ayYkKOVP9eHSdpZO7oT7TuWo'
    
    // 获取文件MIME类型
    const contentType = this.getFileMimeType(filename)
    
    // 对文件名进行URL编码（处理中文字符）
    const encodedFilename = encodeURIComponent(filename)
    
    // 第一步：初始化分步上传，获取上传URL
    const initUrl = `https://storage.googleapis.com/upload/storage/v1/b/${bucketName}/o?uploadType=resumable`
    
    try {
      const initResponse = await axios.post(initUrl, {
        name: filename, // 使用原始文件名，Google Cloud Storage 会自动处理编码
        contentType: contentType
        // 注意：如果存储桶启用了 Bucket Policy Only 或 Public Access Prevention，
        // 则不能使用 ACL。如果需要公开访问，请通过 IAM 策略设置
        // acl: [
        //   {
        //     entity: 'allUsers',
        //     role: 'READER'
        //   }
        // ]
      }, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json; charset=UTF-8',
          'X-Upload-Content-Type': contentType
        },
        validateStatus: (status) => status < 500 // 允许 4xx 错误以便处理
      })
      
      // 检查是否有错误
      if (initResponse.status >= 400) {
        const errorMsg = initResponse.data?.error?.message || `初始化上传失败: ${initResponse.status}`
        throw new Error(errorMsg)
      }
      
      // 从响应头获取上传URL
      const uploadUrl = initResponse.headers.location || initResponse.headers.Location
      
      if (!uploadUrl) {
        throw new Error('无法获取上传URL，响应头中缺少 Location 字段')
      }
      
      // 第二步：使用PUT请求上传文件内容
      const uploadResponse = await axios.put(uploadUrl, file, {
        headers: {
          'Content-Type': contentType
        },
        onUploadProgress: (progressEvent) => {
          if (onUploadProgress) {
            onUploadProgress(progressEvent)
          }
        },
        validateStatus: (status) => status < 500
      })
      
      // 检查上传是否成功
      if (uploadResponse.status >= 400) {
        const errorMsg = uploadResponse.data?.error?.message || `文件上传失败: ${uploadResponse.status}`
        throw new Error(errorMsg)
      }
      
      // 返回上传结果，包含公开访问URL（需要对文件名进行URL编码）
      const publicUrl = `https://storage.googleapis.com/${bucketName}/${encodedFilename}`
      
      return {
        ...uploadResponse,
        data: {
          ...uploadResponse.data,
          publicUrl: publicUrl,
          uri: publicUrl
        }
      }
    } catch (error) {
      // 处理错误
      if (error.response) {
        // API 返回的错误
        const errorData = error.response.data?.error || {}
        const errorMessage = errorData.message || `上传失败: ${error.response.status}`
        const errorCode = errorData.code || error.response.status
        
        // 特殊处理常见错误
        if (errorCode === 401) {
          throw new Error('访问令牌无效或已过期，请检查访问令牌')
        } else if (errorCode === 403) {
          throw new Error('权限不足，请检查存储桶权限设置')
        } else if (errorCode === 400) {
          throw new Error(`请求参数错误: ${errorMessage}`)
        } else {
          throw new Error(`${errorMessage} (错误代码: ${errorCode})`)
        }
      } else if (error.request) {
        // 请求发送但无响应
        throw new Error('网络错误：无法连接到 Google Cloud Storage')
      } else {
        // 其他错误
        throw error
      }
    }
  },
  
  // 保存谷歌存储上传的素材信息
  saveGoogleStorageMaterial: (data) => {
    return http.post('/saveGoogleStorageMaterial', data)
  },
  
  // 获取谷歌存储文件的公开访问链接
  getGoogleFilePublicUrl: (uri) => {
    return http.post('/getGoogleFilePublicUrl', { uri })
  }
}
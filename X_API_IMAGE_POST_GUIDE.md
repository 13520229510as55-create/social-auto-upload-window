# X (Twitter) API v1 发图指南

## 概述

本文档介绍如何使用 X (Twitter) 的 v1 API 发布包含图片的推文。

## 前置准备

### 1. 注册 X 开发者账号

1. 访问 [X Developer Portal](https://developer.twitter.com/)
2. 注册开发者账号并创建应用
3. 获取以下凭证：
   - **API Key** (Consumer Key)
   - **API Secret Key** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**

### 2. 设置应用权限

确保应用具有以下权限：
- **Read and Write** (读写权限)
- **Media Upload** (媒体上传权限)

## API 端点

### 1. 上传媒体 (Media Upload)

**端点**: `https://upload.twitter.com/1.1/media/upload.json`

**方法**: `POST`

**认证**: OAuth 1.0a

**参数**:
- `media`: 图片文件（multipart/form-data）
- `media_category`: 媒体类别（可选，如 `tweet_image`）

**响应**:
```json
{
  "media_id": 1234567890123456789,
  "media_id_string": "1234567890123456789",
  "size": 12345,
  "expires_after_secs": 86400,
  "image": {
    "image_type": "image/jpeg",
    "w": 1920,
    "h": 1080
  }
}
```

### 2. 发布推文 (Status Update)

**端点**: `https://api.twitter.com/1.1/statuses/update.json`

**方法**: `POST`

**认证**: OAuth 1.0a

**参数**:
- `status`: 推文文本内容
- `media_ids`: 媒体ID列表（逗号分隔的 media_id_string）

## Python 实现示例

### 方法一：使用 tweepy 库（推荐）

```python
import tweepy
from pathlib import Path

def post_image_to_x(
    api_key: str,
    api_secret_key: str,
    access_token: str,
    access_token_secret: str,
    image_path: str,
    text: str = ""
):
    """
    使用 X API v1 发布带图片的推文
    
    参数:
        api_key: API Key
        api_secret_key: API Secret Key
        access_token: Access Token
        access_token_secret: Access Token Secret
        image_path: 图片文件路径
        text: 推文文本内容
    """
    # 认证
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret_key,
        access_token,
        access_token_secret
    )
    api = tweepy.API(auth)
    
    # 上传图片
    media = api.media_upload(image_path)
    
    # 发布推文
    api.update_status(status=text, media_ids=[media.media_id])
    
    print(f"✅ 推文发布成功，media_id: {media.media_id}")

# 使用示例
if __name__ == "__main__":
    post_image_to_x(
        api_key="YOUR_API_KEY",
        api_secret_key="YOUR_API_SECRET_KEY",
        access_token="YOUR_ACCESS_TOKEN",
        access_token_secret="YOUR_ACCESS_TOKEN_SECRET",
        image_path="/path/to/image.jpg",
        text="这是一条带图片的推文 #测试"
    )
```

### 方法二：使用 requests 库（原生实现）

```python
import requests
from requests_oauthlib import OAuth1
from pathlib import Path

def post_image_to_x_native(
    api_key: str,
    api_secret_key: str,
    access_token: str,
    access_token_secret: str,
    image_path: str,
    text: str = ""
):
    """
    使用原生 requests 库发布带图片的推文
    """
    # OAuth 1.0a 认证
    auth = OAuth1(
        api_key,
        api_secret_key,
        access_token,
        access_token_secret
    )
    
    # 步骤1: 上传图片
    upload_url = "https://upload.twitter.com/1.1/media/upload.json"
    
    with open(image_path, 'rb') as image_file:
        files = {'media': image_file}
        response = requests.post(upload_url, auth=auth, files=files)
        response.raise_for_status()
        media_data = response.json()
        media_id = media_data['media_id_string']
    
    print(f"✅ 图片上传成功，media_id: {media_id}")
    
    # 步骤2: 发布推文
    update_url = "https://api.twitter.com/1.1/statuses/update.json"
    params = {
        'status': text,
        'media_ids': media_id
    }
    
    response = requests.post(update_url, auth=auth, params=params)
    response.raise_for_status()
    
    tweet_data = response.json()
    print(f"✅ 推文发布成功，tweet_id: {tweet_data['id']}")
    return tweet_data

# 使用示例
if __name__ == "__main__":
    post_image_to_x_native(
        api_key="YOUR_API_KEY",
        api_secret_key="YOUR_API_SECRET_KEY",
        access_token="YOUR_ACCESS_TOKEN",
        access_token_secret="YOUR_ACCESS_TOKEN_SECRET",
        image_path="/path/to/image.jpg",
        text="这是一条带图片的推文 #测试"
    )
```

## 多张图片发布

```python
import tweepy

def post_multiple_images_to_x(
    api_key: str,
    api_secret_key: str,
    access_token: str,
    access_token_secret: str,
    image_paths: list,
    text: str = ""
):
    """
    发布包含多张图片的推文（最多4张）
    """
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret_key,
        access_token,
        access_token_secret
    )
    api = tweepy.API(auth)
    
    # 上传所有图片
    media_ids = []
    for image_path in image_paths[:4]:  # 最多4张图片
        media = api.media_upload(image_path)
        media_ids.append(media.media_id)
    
    # 发布推文
    api.update_status(status=text, media_ids=media_ids)
    print(f"✅ 推文发布成功，包含 {len(media_ids)} 张图片")
```

## 错误处理

```python
import tweepy
from tweepy.errors import TweepyException

def post_image_with_error_handling(
    api_key: str,
    api_secret_key: str,
    access_token: str,
    access_token_secret: str,
    image_path: str,
    text: str = ""
):
    try:
        auth = tweepy.OAuth1UserHandler(
            api_key,
            api_secret_key,
            access_token,
            access_token_secret
        )
        api = tweepy.API(auth)
        
        # 上传图片
        media = api.media_upload(image_path)
        
        # 发布推文
        api.update_status(status=text, media_ids=[media.media_id])
        
        print(f"✅ 推文发布成功")
        return True
        
    except TweepyException as e:
        print(f"❌ 发布失败: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ 图片文件不存在: {image_path}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False
```

## 注意事项

1. **图片格式**: 支持 JPEG、PNG、GIF、WebP
2. **图片大小**: 单个文件最大 5MB
3. **图片数量**: 单条推文最多 4 张图片
4. **文本长度**: 推文文本最多 280 个字符
5. **速率限制**: 
   - 媒体上传: 每15分钟最多 75 次
   - 推文发布: 每15分钟最多 300 次
6. **认证**: 必须使用 OAuth 1.0a 认证
7. **权限**: 应用必须具有 "Read and Write" 权限

## 依赖安装

```bash
# 方法一：使用 tweepy
pip install tweepy

# 方法二：使用原生 requests
pip install requests requests-oauthlib
```

## 参考文档

- [X API v1.1 文档](https://developer.twitter.com/en/docs/twitter-api/v1)
- [Media Upload API](https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media)
- [Status Update API](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update)


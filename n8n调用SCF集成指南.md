# n8n 调用腾讯云 SCF 集成指南

## 📋 概述

**是的，n8n 完全可以调用腾讯云 SCF（Serverless Cloud Function）接口！**

n8n 是一个强大的开源工作流自动化工具，支持通过 HTTP Request 节点调用任何 HTTP/HTTPS API，包括腾讯云的 SCF 函数。

---

## ✅ 可行性说明

### n8n 支持的方式

1. **HTTP Request 节点** - 最常用的方式，支持所有 HTTP 方法
2. **Webhook 节点** - 接收来自 SCF 的回调
3. **自定义代码节点** - 使用 JavaScript/Python 调用 SCF API

### SCF 调用方式

1. **API 网关触发器** - 通过 HTTP/HTTPS 访问（推荐）
2. **直接调用 API** - 使用腾讯云 SDK
3. **事件触发** - 通过云服务事件触发

---

## 🚀 集成方案

### 方案一：通过 API 网关调用 SCF（推荐）

这是最简单和常用的方式，SCF 通过 API 网关暴露 HTTP 接口。

#### 步骤 1: 在腾讯云配置 SCF 和 API 网关

1. **创建 SCF 函数**
   - 登录腾讯云控制台
   - 进入「云函数 SCF」服务
   - 创建新函数，选择运行环境（Python/Node.js 等）
   - 编写函数代码

2. **配置 API 网关触发器**
   - 在 SCF 函数详情页，添加「API 网关触发器」
   - 配置触发方式：
     - 发布环境：发布/测试
     - 请求方法：GET/POST/PUT/DELETE 等
     - 鉴权方式：免鉴权/密钥对鉴权/OAuth 2.0
   - 获取调用 URL（格式：`https://service-xxx-xxx.apigw.tencentcs.com/release/xxx`）

3. **获取认证信息**（如果使用密钥对鉴权）
   - API 密钥 ID（SecretId）
   - API 密钥 Key（SecretKey）

#### 步骤 2: 在 n8n 中配置 HTTP Request 节点

1. **添加 HTTP Request 节点**
   - 在 n8n 工作流中添加「HTTP Request」节点

2. **配置节点参数**

   **基础配置：**
   ```
   Method: POST (或根据您的 SCF 函数配置选择)
   URL: https://service-xxx-xxx.apigw.tencentcs.com/release/xxx
   ```

   **请求头配置（Headers）：**
   ```json
   {
     "Content-Type": "application/json",
     "Authorization": "Bearer YOUR_TOKEN"  // 如果使用 OAuth
   }
   ```

   **请求体配置（Body）：**
   ```json
   {
     "key1": "value1",
     "key2": "value2"
   }
   ```

   **查询参数（Query Parameters）：**
   ```
   param1: value1
   param2: value2
   ```

3. **认证配置**

   **方式 A: 免鉴权（最简单）**
   - 在 API 网关中配置为「免鉴权」
   - n8n 中无需额外配置

   **方式 B: 密钥对鉴权**
   - 在 n8n 中使用「Custom Auth」或「Header Auth」
   - 添加认证头：
     ```
     X-API-Key: YOUR_API_KEY
     ```

   **方式 C: OAuth 2.0**
   - 在 n8n 中使用「OAuth2 API」认证类型
   - 配置 OAuth 参数

#### 步骤 3: 测试调用

1. 在 n8n 中执行工作流
2. 查看 HTTP Request 节点的响应
3. 检查返回数据是否符合预期

---

### 方案二：使用腾讯云 API 直接调用 SCF

如果需要使用腾讯云官方 API 调用 SCF（不使用 API 网关），可以使用腾讯云 API。

#### 在 n8n 中配置

1. **使用 HTTP Request 节点调用腾讯云 API**

   **URL：**
   ```
   https://scf.tencentcloudapi.com/
   ```

   **请求头：**
   ```json
   {
     "Content-Type": "application/json",
     "X-TC-Action": "Invoke",
     "X-TC-Version": "2018-04-16",
     "X-TC-Region": "ap-guangzhou",
     "Authorization": "TC3-HMAC-SHA256 ..."  // 需要计算签名
   }
   ```

   **请求体：**
   ```json
   {
     "FunctionName": "your-function-name",
     "Namespace": "default",
     "Qualifier": "$LATEST",
     "ClientContext": "{\"key\":\"value\"}"
   }
   ```

2. **签名计算（复杂）**

   腾讯云 API 需要 TC3-HMAC-SHA256 签名，建议：
   - 使用 n8n 的「Code」节点计算签名
   - 或使用「Function」节点调用预计算的签名服务

---

### 方案三：使用 n8n Webhook 接收 SCF 回调

如果 SCF 需要回调 n8n，可以配置 Webhook。

#### 步骤 1: 在 n8n 中创建 Webhook

1. 添加「Webhook」节点
2. 选择「POST」方法
3. 获取 Webhook URL（例如：`https://your-n8n.com/webhook/xxx`）

#### 步骤 2: 在 SCF 函数中调用 Webhook

```python
# Python 示例
import requests

def main_handler(event, context):
    # 处理业务逻辑
    result = process_data(event)
    
    # 回调 n8n Webhook
    webhook_url = "https://your-n8n.com/webhook/xxx"
    response = requests.post(webhook_url, json=result)
    
    return {
        "statusCode": 200,
        "body": result
    }
```

---

## 📝 完整示例

### 示例 1: n8n 调用 SCF（简单 HTTP 调用）

**n8n 工作流配置：**

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "https://service-abc123.apigw.tencentcs.com/release/my-function",
        "authentication": "none",
        "options": {
          "headers": {
            "Content-Type": "application/json"
          },
          "body": {
            "contentType": "json",
            "body": "={{ JSON.stringify($json) }}"
          }
        }
      },
      "name": "调用 SCF 函数",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1
    }
  ]
}
```

**SCF 函数代码示例（Python）：**

```python
import json

def main_handler(event, context):
    """
    主处理函数
    event: 包含请求数据的字典
    context: 运行时上下文
    """
    # 解析请求数据
    if isinstance(event, str):
        data = json.loads(event)
    else:
        data = event
    
    # 处理业务逻辑
    result = {
        "code": 200,
        "message": "处理成功",
        "data": {
            "input": data,
            "processed_at": context.get_remaining_time_in_millis()
        }
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(result, ensure_ascii=False)
    }
```

### 示例 2: 带认证的调用

**n8n HTTP Request 节点配置：**

```
Method: POST
URL: https://service-xxx.apigw.tencentcs.com/release/function
Authentication: Header Auth
Name: X-API-Key
Value: your-api-key-here
```

**请求体：**
```json
{
  "action": "process",
  "data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

### 示例 3: 使用 Code 节点处理响应

在 HTTP Request 节点后添加「Code」节点处理 SCF 返回的数据：

```javascript
// 处理 SCF 响应
const response = $input.item.json;

// 检查响应状态
if (response.statusCode === 200) {
  const body = JSON.parse(response.body);
  
  return {
    json: {
      success: true,
      data: body.data,
      message: body.message
    }
  };
} else {
  throw new Error(`SCF 调用失败: ${response.body}`);
}
```

---

## 🔧 高级配置

### 1. 错误处理

在 n8n 中配置错误处理：

1. 启用「Continue On Fail」
2. 添加「IF」节点判断响应状态
3. 使用「Switch」节点处理不同错误类型

### 2. 重试机制

在 HTTP Request 节点中配置：
- **Retry On Fail**: 启用
- **Max Tries**: 3
- **Retry Delay**: 1000ms

### 3. 超时设置

```
Timeout: 30000  // 30秒
```

### 4. 使用环境变量

在 n8n 中使用环境变量存储敏感信息：

```
URL: {{ $env.SCF_API_URL }}
API_KEY: {{ $env.SCF_API_KEY }}
```

---

## 🎯 实际应用场景

### 场景 1: 自动化数据处理

```
触发事件 → n8n Webhook → 处理数据 → 调用 SCF 函数 → 返回结果
```

### 场景 2: 定时任务

```
n8n Cron 触发器 → 调用 SCF 函数 → 处理任务 → 发送通知
```

### 场景 3: 工作流编排

```
n8n 工作流 → 调用多个 SCF 函数 → 汇总结果 → 执行后续操作
```

---

## ⚠️ 注意事项

### 1. 认证和安全

- ✅ 使用 HTTPS 协议
- ✅ 配置 API 网关鉴权
- ✅ 不要在代码中硬编码密钥
- ✅ 使用环境变量存储敏感信息

### 2. 性能优化

- ✅ 设置合理的超时时间
- ✅ 使用异步调用（如果 SCF 支持）
- ✅ 实现重试机制
- ✅ 监控调用频率和成本

### 3. 错误处理

- ✅ 处理网络错误
- ✅ 处理 SCF 函数错误
- ✅ 记录错误日志
- ✅ 实现降级方案

### 4. 成本控制

- ✅ 监控 SCF 调用次数
- ✅ 优化函数执行时间
- ✅ 使用合适的并发配置

---

## 📚 相关资源

### 腾讯云文档

- [SCF 官方文档](https://cloud.tencent.com/document/product/583)
- [API 网关文档](https://cloud.tencent.com/document/product/628)
- [SCF API 参考](https://cloud.tencent.com/document/api/583)

### n8n 文档

- [HTTP Request 节点文档](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Webhook 节点文档](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [认证配置](https://docs.n8n.io/integrations/builtin/credentials/)

---

## 🆘 常见问题

### Q1: n8n 调用 SCF 超时怎么办？

**A:** 
- 检查 SCF 函数的超时设置
- 增加 n8n HTTP Request 节点的超时时间
- 优化 SCF 函数执行效率

### Q2: 如何传递文件到 SCF？

**A:**
- 使用 Base64 编码文件内容
- 或上传到 COS，传递文件 URL
- 在请求体中包含文件数据

### Q3: SCF 返回的数据格式不对？

**A:**
- 检查 SCF 函数的返回格式
- 确保返回 JSON 格式
- 在 n8n 中使用 Code 节点解析响应

### Q4: 如何调试调用问题？

**A:**
- 查看 n8n 执行日志
- 查看 SCF 函数日志
- 使用 Postman 测试 API 网关接口
- 检查网络连接和防火墙设置

---

## ✅ 总结

**n8n 完全可以调用腾讯云 SCF 接口！**

推荐使用 **API 网关 + HTTP Request 节点** 的方式，这是最简单、最可靠的集成方案。

主要步骤：
1. ✅ 在腾讯云配置 SCF 和 API 网关
2. ✅ 在 n8n 中添加 HTTP Request 节点
3. ✅ 配置 URL、方法、请求头和请求体
4. ✅ 测试并验证调用

如有问题，请参考上述文档或查看相关日志进行排查。

---

**最后更新**: 2024-11-26




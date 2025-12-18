# SSE连接错误修复说明

## 问题描述
用户报告在添加视频号账号时，前端出现"SSE连接错误"提示，即使后端正常返回了状态码。

## 问题分析

### 1. 缺少keep-alive机制
SSE流在长时间等待用户扫码时，如果没有定期发送数据，连接可能会被代理服务器或浏览器超时关闭。

### 2. 前端错误处理过于敏感
前端的`onerror`事件会在连接正常关闭时也触发，导致误报错误。

## 修复方案

### 后端修复（`sau_backend.py`）

#### 1. 添加SSE keep-alive心跳机制
```python
# SSE 流生成器函数
def sse_stream(status_queue):
    print(f"[SSE流] 开始SSE流生成器")
    final_status_sent = False
    last_heartbeat = time.time()
    heartbeat_interval = 15  # 每15秒发送一次心跳
    
    while True:
        current_time = time.time()
        
        # 发送心跳保持连接（每15秒一次）
        if current_time - last_heartbeat >= heartbeat_interval:
            try:
                yield f": heartbeat\n\n"  # SSE注释，用于保持连接
                last_heartbeat = current_time
                print(f"[SSE流] 发送心跳保持连接")
            except Exception as e:
                print(f"[SSE流] 发送心跳失败: {e}")
                break
        # ... 其他逻辑
```

**说明**：
- 每15秒发送一次心跳（SSE注释格式 `: heartbeat`）
- 心跳不会触发前端的`onmessage`事件，只用于保持连接
- 如果发送心跳失败，说明连接已断开，退出循环

#### 2. 改进SSE响应头
```python
response.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
response.headers['Access-Control-Allow-Origin'] = '*'  # 确保CORS支持
response.headers['Access-Control-Allow-Headers'] = 'Cache-Control'
```

**说明**：
- 明确指定字符集
- 确保CORS支持，避免跨域问题

### 前端修复（`sau_frontend/src/views/AccountManagement.vue`）

#### 1. 添加连接打开监听
```javascript
// 监听连接打开
eventSource.onopen = (event) => {
  console.log('[前端] SSE连接已打开', event)
  console.log('[前端] EventSource readyState:', eventSource.readyState)
}
```

**说明**：
- 监听连接成功打开事件
- 用于调试和确认连接状态

#### 2. 改进错误处理逻辑
```javascript
// 监听错误
eventSource.onerror = (error) => {
  console.error('[前端] SSE连接错误:', error)
  console.log('[前端] EventSource readyState:', eventSource.readyState)
  
  // 延迟处理错误，避免在连接建立过程中误报
  setTimeout(() => {
    // 如果连接已经关闭（readyState === 2）
    if (eventSource && eventSource.readyState === EventSource.CLOSED) {
      console.log('[前端] SSE连接已关闭')
      // 如果还没有收到状态码，可能是连接异常关闭
      if (!loginStatus.value && sseConnecting.value) {
        console.warn('[前端] 连接关闭但未收到状态码，可能是异常关闭')
        ElMessage.error('连接已断开，请重试')
        closeSSEConnection()
        sseConnecting.value = false
      }
    } 
    // 如果正在连接（readyState === 0），可能是连接失败
    else if (eventSource && eventSource.readyState === EventSource.CONNECTING) {
      console.error('[前端] SSE连接失败，无法建立连接')
      ElMessage.error('连接服务器失败，请检查网络连接')
      closeSSEConnection()
      sseConnecting.value = false
    }
    // 如果连接已打开但出现错误（readyState === 1），可能是网络问题
    else if (eventSource && eventSource.readyState === EventSource.OPEN) {
      console.warn('[前端] SSE连接打开但出现错误，可能是网络波动')
      // 不立即关闭，等待重连或后续消息
    }
    // 其他情况
    else if (eventSource && sseConnecting.value) {
      console.error('[前端] SSE连接出现未知错误')
      ElMessage.error('连接服务器失败，请稍后再试')
      closeSSEConnection()
      sseConnecting.value = false
    }
  }, 1000) // 延迟1秒处理，避免误报
}
```

**说明**：
- 延迟1秒处理错误，避免在连接建立过程中误报
- 根据`readyState`的不同状态，提供更精确的错误处理
- 区分正常关闭和异常错误
- 只有在真正需要时才显示错误提示

## 修复效果

### 测试结果
1. ✅ SSE连接成功建立
2. ✅ 收到二维码数据
3. ✅ 收到心跳消息（`: heartbeat`），keep-alive正常工作
4. ✅ 连接保持稳定，不会因为超时断开

### 改进点
1. **连接稳定性**：通过心跳机制，确保连接在长时间等待时不会断开
2. **错误提示准确性**：改进的错误处理逻辑，避免误报
3. **调试能力**：添加了详细的日志，便于排查问题

## 部署信息

- **部署时间**：2025-12-08
- **部署脚本**：`deploy_sse_connection_fix.sh`
- **修改文件**：
  - `sau_backend.py`（SSE流生成器）
  - `sau_frontend/src/views/AccountManagement.vue`（SSE连接处理）

## 预防措施

1. **监控SSE连接**：定期检查SSE连接的健康状态
2. **日志记录**：保留详细的连接日志，便于问题排查
3. **超时配置**：根据实际业务需求调整心跳间隔和超时时间

## 相关文档

- `视频号登录超时问题修复说明.md`：视频号登录超时问题的修复说明
- `deploy_sse_connection_fix.sh`：SSE连接修复的部署脚本


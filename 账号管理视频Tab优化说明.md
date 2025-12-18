# 账号管理视频Tab优化说明

## 修改内容

### 1. 默认Tab改为视频
- **修改位置**: `sau_frontend/src/views/AccountManagement.vue` 第557行
- **修改前**: `const activeTab = ref('image-text')`
- **修改后**: `const activeTab = ref('video')`
- **效果**: 账号管理页面打开时，默认显示"视频"Tab

### 2. 视频Tab平台类型增加小红书
- **修改位置**: `sau_frontend/src/views/AccountManagement.vue` 第594行
- **修改前**: `'video': ['快手', '抖音', '视频号']`
- **修改后**: `'video': ['快手', '抖音', '视频号', '小红书']`
- **效果**: 在视频Tab的平台类型筛选中，增加了"小红书"选项

### 3. 过滤逻辑优化
- **修改位置**: `sau_frontend/src/views/AccountManagement.vue` `getAccountsByContentType` 函数
- **修改内容**: 添加了特殊处理逻辑，让小红书账号在视频Tab中也能正确显示
- **逻辑说明**:
  ```javascript
  // 特殊处理：小红书同时支持图文和视频
  if (account.platform === '小红书') {
    // 在视频Tab中，如果选中的是小红书，则显示小红书账号
    if (contentType === 'video' && selectedPlatform === '小红书') {
      return true
    }
    // 在图文Tab中，如果选中的是小红书，则显示小红书账号
    if (contentType === 'image-text' && selectedPlatform === '小红书') {
      return true
    }
  }
  ```

## 功能说明

### 小红书平台的双重支持
- **图文Tab**: 小红书账号可以显示（原有功能）
- **视频Tab**: 小红书账号也可以显示（新增功能）
- **原因**: 小红书平台同时支持图文和视频内容

### 添加账号功能
- 在视频Tab中点击"添加账号"时，平台选择下拉框会显示：
  - 快手
  - 抖音
  - 视频号
  - 小红书（新增）

## 使用说明

1. **打开账号管理页面**
   - 默认显示"视频"Tab
   - 平台类型默认选中第一个（快手）

2. **选择小红书平台**
   - 在视频Tab中，点击"小红书"单选按钮
   - 会显示所有小红书账号（无论账号原本属于哪个Tab）

3. **添加小红书账号**
   - 在视频Tab中点击"添加账号"
   - 在平台选择中选择"小红书"
   - 填写账号名称并选择Cookie类型
   - 点击确认完成添加

## 注意事项

- 小红书账号在图文Tab和视频Tab中都可以显示
- 添加账号时，平台选择会根据当前Tab自动过滤
- 账号的实际类型仍然由后端数据库中的 `type` 字段决定



# 小红书图文自动化发布接口文档

## 接口地址
```
POST /postImageText
```

## 接口说明
用于自动化发布图文内容到小红书平台，参考了小红书视频发布的逻辑。

## 请求参数

### 请求头
```
Content-Type: application/json
```

### 请求体 (JSON)
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 是 | 图文标题 |
| imageList | array | 是 | 图片文件列表，文件需先通过 `/upload` 接口上传 |
| accountList | array | 是 | 账号cookie文件列表，从 `/getValidAccounts` 接口获取 |
| tags | array | 否 | 标签列表，默认为空数组 |
| enableTimer | boolean | 否 | 是否启用定时发布，默认为 false |
| imagesPerDay | number | 否 | 每天发布图文数（启用定时发布时有效），默认为 1 |
| dailyTimes | array | 否 | 每日发布时间列表（启用定时发布时有效），默认为空数组 |
| startDays | number | 否 | 开始天数（启用定时发布时有效），0代表明天开始，默认为 0 |

## 请求示例

### 立即发布
```json
{
  "title": "我的图文标题",
  "imageList": [
    "uuid1_image1.jpg",
    "uuid2_image2.jpg"
  ],
  "accountList": [
    "account1.json",
    "account2.json"
  ],
  "tags": ["美食", "探店", "生活"],
  "enableTimer": false
}
```

### 定时发布
```json
{
  "title": "我的图文标题",
  "imageList": [
    "uuid1_image1.jpg",
    "uuid2_image2.jpg"
  ],
  "accountList": [
    "account1.json"
  ],
  "tags": ["美食", "探店"],
  "enableTimer": true,
  "imagesPerDay": 1,
  "dailyTimes": [16],
  "startDays": 0
}
```

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "msg": "图文发布任务已提交",
  "data": null
}
```

### 错误响应
```json
{
  "code": 400,
  "msg": "图片列表不能为空",
  "data": null
}
```

或

```json
{
  "code": 500,
  "msg": "发布失败: 错误信息",
  "data": null
}
```

## 使用流程

1. **上传图片文件**
   - 使用 `/upload` 接口上传图片文件
   - 获取返回的文件名（如：`uuid1_image1.jpg`）

2. **获取账号列表**
   - 使用 `/getValidAccounts` 接口获取可用账号
   - 从返回数据中获取 `filePath` 字段（如：`account1.json`）

3. **调用发布接口**
   - 使用 `/postImageText` 接口发布图文
   - 传入标题、图片列表、账号列表等参数

## 注意事项

1. 图片文件必须先通过 `/upload` 接口上传到服务器
2. 账号cookie文件必须有效，可通过 `/getValidAccounts` 接口验证
3. 图片文件路径相对于 `videoFile` 目录
4. 账号文件路径相对于 `cookiesFile` 目录
5. 定时发布功能需要正确设置 `enableTimer`、`imagesPerDay`、`dailyTimes` 和 `startDays` 参数

## 错误码说明

- `200`: 成功
- `400`: 请求参数错误（如：图片列表为空、账号列表为空、标题为空）
- `500`: 服务器内部错误（如：发布失败、文件不存在等）

## 技术实现

- 使用 Playwright 自动化浏览器操作
- 参考了 `XiaoHongShuVideo` 类的实现逻辑
- 支持多账号批量发布
- 支持定时发布功能
- 自动保存和更新cookie


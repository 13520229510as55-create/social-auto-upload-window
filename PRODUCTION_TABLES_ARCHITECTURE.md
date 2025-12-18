# 制作中心三张表架构说明

## 表结构

### 1. `production_articles` - 文章表
**字段：**
- `id` - 主键
- `title` - 标题
- `content` - 内容
- `desc` - 描述
- `url` - 图片链接
- `html` - 富文本
- `publish_status` - 发布状态
- `created_at` - 创建时间

**兼容字段（旧）：**
- `article_title`, `article_content`, `article_desc`, `article_media_url`

### 2. `production_image_text` - 图文表
**字段：**
- `id` - 主键
- `title` - 标题
- `content` - 内容
- `media_ids` - 媒体ID数组（JSON字符串）
- `height` - 高度
- `width` - 宽度
- `url` - URL（可选）
- `publish_status` - 发布状态
- `created_at` - 创建时间

### 3. `production_video` - 视频表
**字段：**
- `id` - 主键
- `title` - 标题
- `desc` - 描述
- `keywords` - 关键词（JSON字符串或逗号分隔）
- `video` - 视频URL
- `content` - 内容/文案
- `material_url` - 素材URL
- `publish_status` - 发布状态
- `created_at` - 创建时间

## 接口列表

### 创建接口（独立操作对应表）

1. **POST `/production/articles`**
   - 操作表：`production_articles`
   - 入参：`title`, `content`, `desc`, `url`, `html`

2. **POST `/production/image-text`**
   - 操作表：`production_image_text`
   - 入参：`title`, `content`, `media_ids` (数组), `height`, `width`, `url` (可选)

3. **POST `/production/video`**
   - 操作表：`production_video`
   - 入参：`title`, `desc`, `keywords`, `video`

4. **POST `/production/video-from-n8n`**
   - 操作表：`production_video`
   - 入参：`title`, `content`, `desc`, `material_url`, `url`

### 更新接口（独立操作对应表）

1. **PUT `/production/articles/<id>`**
   - 操作表：`production_articles`
   - 入参：`title`, `content`, `desc`, `url`, `html`

2. **PUT `/production/image-text/<id>`**
   - 操作表：`production_image_text`
   - 入参：`title`, `content`, `media_ids` (数组), `height`, `width`, `url` (可选)

### 查询接口（从三张表分别查询并合并）

1. **GET `/production/records`**
   - 查询表：`production_articles`, `production_image_text`, `production_video`
   - 查询参数：`content_type` (可选: `article`, `image-text`, `video`, `all`)
   - 返回：合并后的记录列表，每条记录包含 `content_type` 字段

### 删除接口（支持指定表或自动查找）

1. **DELETE `/production/records/<id>`**
   - 查询参数：`content_type` (可选: `article`, `image-text`, `video`)
   - 如果提供 `content_type`：直接操作对应的表（推荐，更高效）
   - 如果不提供：依次尝试三张表（向后兼容）

2. **DELETE `/production/records`** (批量删除)
   - 请求体格式1（推荐）：`{ "content_type": "article", "ids": [1, 2, 3] }`
   - 请求体格式2（兼容）：`{ "ids": [1, 2, 3] }` - 自动从三张表中查找

### 状态更新接口（支持指定表或自动查找）

1. **PUT `/production/records/<id>/status`**
   - 请求体：`{ "status": "pending|processing|creating|success|failed", "content_type": "article|image-text|video" (可选) }`
   - 如果提供 `content_type`：直接操作对应的表（推荐，更高效）
   - 如果不提供：依次尝试三张表（向后兼容）

## 设计原则

1. **表独立性**：每张表有独立的字段结构，互不干扰
2. **接口灵活性**：
   - 创建和更新接口明确操作对应的表
   - 删除和状态更新接口支持 `content_type` 参数，提高效率
   - 保持向后兼容，支持不传 `content_type` 的自动查找
3. **查询统一性**：列表查询接口统一从三张表查询并合并，前端无需关心表结构

## 使用建议

1. **创建记录**：使用对应的创建接口（`/production/articles`, `/production/image-text`, `/production/video`）
2. **更新记录**：使用对应的更新接口（`/production/articles/<id>`, `/production/image-text/<id>`）
3. **删除记录**：推荐传递 `content_type` 参数，提高效率
4. **更新状态**：推荐传递 `content_type` 参数，提高效率
5. **查询记录**：使用统一的 `/production/records` 接口，通过 `content_type` 参数过滤



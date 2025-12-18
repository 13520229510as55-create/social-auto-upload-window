# Xvfb 虚拟显示服务器配置说明

## 概述

Xvfb (X Virtual Framebuffer) 是一个虚拟显示服务器，允许在没有物理显示设备的服务器上运行需要图形界面的应用程序。在本项目中，Xvfb 用于支持非 headless 模式的浏览器运行。

## 为什么需要 Xvfb？

当 `LOCAL_CHROME_HEADLESS = False` 时，浏览器需要图形显示环境才能运行。但服务器通常没有物理显示设备，因此需要使用 Xvfb 创建虚拟显示环境。

## 安装 Xvfb

### Ubuntu/Debian 系统

```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

### 验证安装

```bash
which Xvfb
Xvfb -help
```

## 项目中的 Xvfb 集成

### 自动管理

项目已集成 Xvfb 自动管理功能，无需手动启动。当代码检测到需要非 headless 模式且没有 DISPLAY 环境变量时，会自动启动 Xvfb。

### 相关文件

- **`utils/xvfb_helper.py`**: Xvfb 辅助模块，提供自动启动和管理功能
- **`myUtils/auth.py`**: Cookie 验证功能，已集成 Xvfb 支持
- **`myUtils/login.py`**: 登录功能，已集成 Xvfb 支持

### 核心功能

#### 1. `ensure_display(headless: bool) -> bool`

确保有可用的显示环境。如果 `headless=False` 且没有 DISPLAY 环境变量，会自动启动 Xvfb。

**使用示例：**
```python
from utils.xvfb_helper import ensure_display
from conf import LOCAL_CHROME_HEADLESS

# 在启动浏览器前调用
ensure_display(LOCAL_CHROME_HEADLESS)
```

#### 2. `start_xvfb(display_num=None, ...) -> Optional[str]`

启动 Xvfb 虚拟显示服务器。

**参数：**
- `display_num`: 显示编号（如 99），如果为 None 则自动查找可用编号
- `screen`: 屏幕编号，默认 0
- `width`: 屏幕宽度，默认 1920
- `height`: 屏幕高度，默认 1080
- `depth`: 颜色深度，默认 24

**返回值：**
- 成功：返回 DISPLAY 环境变量值（如 `:99`）
- 失败：返回 `None`

#### 3. `stop_xvfb()`

停止 Xvfb 虚拟显示服务器并清理相关资源。

## 配置说明

### 配置文件

在 `conf.py` 中设置：

```python
LOCAL_CHROME_HEADLESS = False  # 使用非 headless 模式（需要 Xvfb）
# 或
LOCAL_CHROME_HEADLESS = True   # 使用 headless 模式（不需要 Xvfb）
```

### 工作流程

1. **Headless 模式 (`LOCAL_CHROME_HEADLESS = True`)**
   - 不需要显示环境
   - 浏览器在后台运行
   - 性能更好，资源占用更少

2. **非 Headless 模式 (`LOCAL_CHROME_HEADLESS = False`)**
   - 需要显示环境
   - 代码自动检测并启动 Xvfb（如果未设置 DISPLAY）
   - 浏览器可以正常渲染页面

## 使用示例

### 测试 Xvfb 功能

```python
from playwright.sync_api import sync_playwright
from utils.xvfb_helper import ensure_display
from conf import LOCAL_CHROME_HEADLESS

# 确保显示环境
ensure_display(LOCAL_CHROME_HEADLESS)

# 启动浏览器
with sync_playwright() as p:
    browser = p.chromium.launch(headless=LOCAL_CHROME_HEADLESS)
    page = browser.new_page()
    page.goto('https://www.example.com')
    print(page.title())
    browser.close()
```

### 手动启动 Xvfb（不推荐）

如果需要手动启动 Xvfb：

```bash
# 启动 Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac -nolisten tcp +extension RANDR &

# 设置 DISPLAY 环境变量
export DISPLAY=:99

# 运行应用程序
python your_script.py

# 停止 Xvfb（查找进程并终止）
pkill Xvfb
```

## 故障排查

### 问题 1: Xvfb 启动失败

**错误信息：**
```
❌ Xvfb 启动失败
```

**解决方案：**
1. 检查 Xvfb 是否已安装：`which Xvfb`
2. 检查是否有旧的锁文件：`ls -la /tmp/.X*-lock`
3. 清理旧的锁文件：`rm -f /tmp/.X*-lock`
4. 检查是否有其他 Xvfb 进程：`ps aux | grep Xvfb`

### 问题 2: 浏览器无法启动

**错误信息：**
```
Missing X server or $DISPLAY
```

**解决方案：**
1. 确保 `LOCAL_CHROME_HEADLESS = False` 时，代码已调用 `ensure_display()`
2. 检查 DISPLAY 环境变量：`echo $DISPLAY`
3. 手动测试 Xvfb：`Xvfb :99 -screen 0 1920x1080x24 &`

### 问题 3: 显示编号冲突

**错误信息：**
```
Server is already active for display 99
```

**解决方案：**
- 代码已自动处理此问题，会查找可用的显示编号
- 如需手动清理：`rm -f /tmp/.X99-lock && pkill -9 Xvfb`

## 性能考虑

### Headless vs 非 Headless

| 特性 | Headless 模式 | 非 Headless 模式 |
|------|--------------|-----------------|
| 性能 | 更快 | 稍慢 |
| 内存占用 | 更少 | 更多 |
| 需要显示 | 否 | 是（Xvfb）|
| 调试难度 | 较难 | 较易 |
| 适用场景 | 生产环境 | 开发/调试 |

### 建议

- **生产环境**：推荐使用 `LOCAL_CHROME_HEADLESS = True`
- **开发/调试**：可以使用 `LOCAL_CHROME_HEADLESS = False`（需要 Xvfb）

## 技术细节

### Xvfb 参数说明

- `-screen 0 1920x1080x24`: 创建屏幕 0，分辨率 1920x1080，颜色深度 24 位
- `-ac`: 禁用访问控制，允许所有连接
- `-nolisten tcp`: 不监听 TCP 连接，仅本地使用
- `+extension RANDR`: 启用 RANDR 扩展，支持动态分辨率调整

### 自动清理

代码会在以下情况自动清理 Xvfb：
- 程序正常退出（通过 `atexit`）
- 收到 SIGTERM 信号
- 收到 SIGINT 信号（Ctrl+C）

## 相关资源

- [Xvfb 官方文档](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
- [Playwright 文档](https://playwright.dev/python/)
- [X11 显示服务器](https://www.x.org/wiki/)

## 更新日志

- **2025-11-19**: 初始版本，集成 Xvfb 自动管理功能
  - 创建 `utils/xvfb_helper.py` 模块
  - 修改 `myUtils/auth.py` 和 `myUtils/login.py` 支持 Xvfb
  - 自动检测可用显示编号
  - 自动清理锁文件和进程


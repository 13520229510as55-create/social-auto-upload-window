from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.resolve()
XHS_SERVER = "http://127.0.0.1:11901"
LOCAL_CHROME_PATH = ""   # change me necessary！ for example C:/Program Files/Google/Chrome/Application/chrome.exe
LOCAL_CHROME_HEADLESS = False

# ========== 代理配置（用于访问 Google 服务）==========
# 国内服务器访问 Google Cloud Storage 需要代理
# 格式: http://proxy_host:proxy_port 或 https://proxy_host:proxy_port
# 示例: http://127.0.0.1:7890 或 http://proxy.example.com:8080
# 如果不需要代理，留空字符串 ""
HTTP_PROXY = os.getenv('HTTP_PROXY', '')  # HTTP 代理
HTTPS_PROXY = os.getenv('HTTPS_PROXY', '')  # HTTPS 代理
# 如果只设置了 HTTP_PROXY，HTTPS 请求也会使用它

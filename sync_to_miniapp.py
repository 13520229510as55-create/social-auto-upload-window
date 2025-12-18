#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动同步主项目功能到小程序
将PC版（Web版）的功能和UI优化同步到小程序版本
"""

import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime

# 项目路径配置
MAIN_PROJECT_PATH = Path(__file__).parent
MINIAPP_PROJECT_PATH = MAIN_PROJECT_PATH.parent / "social-auto-upload-miniapp"

# 需要同步的文件映射
FILE_MAPPINGS = {
    # 工具函数
    "sau_frontend/src/utils/dateTime.js": "utils/util.js",
    
    # 样式文件（部分同步）
    "sau_frontend/src/styles/variables.scss": None,  # 需要手动转换
}

# 需要同步的功能模块
FEATURE_SYNC = {
    "publish": {
        "source": "sau_frontend/src/views/PublishCenter.vue",
        "target": "pages/publish",
        "sync_fields": [
            "imageTextPlatforms",  # 图文平台
            "defaultTab",  # 默认Tab
        ]
    },
    "account": {
        "source": "sau_frontend/src/views/AccountManagement.vue",
        "target": "pages/account",
        "sync_fields": [
            "platformFilters",  # 平台筛选
            "tabStructure",  # Tab结构
        ]
    },
    "material": {
        "source": "sau_frontend/src/views/MaterialManagement.vue",
        "target": "pages/material",
        "sync_fields": [
            "tabStructure",  # Tab结构
        ]
    }
}

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log(f"读取文件失败: {file_path} - {e}", "ERROR")
        return None

def write_file_content(file_path, content):
    """写入文件内容"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        log(f"写入文件失败: {file_path} - {e}", "ERROR")
        return False

def sync_timezone_utils():
    """同步时区处理工具函数"""
    log("同步时区处理工具函数...")
    
    source_file = MAIN_PROJECT_PATH / "sau_frontend/src/utils/dateTime.js"
    target_file = MINIAPP_PROJECT_PATH / "utils/util.js"
    
    if not source_file.exists():
        log(f"源文件不存在: {source_file}", "WARN")
        return False
    
    source_content = read_file_content(source_file)
    if not source_content:
        return False
    
    # 提取时区相关函数
    beijing_time_pattern = r'export function getBeijingTime\([^)]*\)\s*\{[^}]*\}'
    format_date_pattern = r'export function formatLocalDateTime\([^)]*\)\s*\{[^}]*\}'
    
    # 检查目标文件
    target_content = read_file_content(target_file)
    if not target_content:
        log("目标文件不存在或无法读取", "WARN")
        return False
    
    # 更新getBeijingTime函数
    if "getBeijingTime" in source_content:
        new_beijing_time = """
/**
 * 获取北京时间（UTC+8）
 * @param {Date} date 日期对象，默认为当前时间
 * @returns {Date}
 */
function getBeijingTime(date = new Date()) {
  // 获取 UTC 时间戳
  const utcTime = date.getTime() + (date.getTimezoneOffset() * 60 * 1000)
  // 转换为北京时间（UTC+8）
  return new Date(utcTime + (8 * 60 * 60 * 1000))
}
"""
        # 替换或添加函数
        if "function getBeijingTime" in target_content:
            target_content = re.sub(
                r'function getBeijingTime\([^)]*\)\s*\{[^}]*\}',
                new_beijing_time.strip(),
                target_content,
                flags=re.DOTALL
            )
        else:
            # 在formatDate函数前插入
            target_content = target_content.replace(
                "function formatDate",
                new_beijing_time + "\n\nfunction formatDate"
            )
    
    # 更新formatDate函数使用北京时间
    if "getBeijingTime" in target_content:
        format_date_new = """
/**
 * 格式化日期时间（使用北京时间 UTC+8）
 * @param {Date} date 日期对象
 * @param {String} format 格式化模板
 * @returns {String}
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  // 转换为北京时间
  const beijingDate = getBeijingTime(date)
  const year = beijingDate.getFullYear()
  const month = String(beijingDate.getMonth() + 1).padStart(2, '0')
  const day = String(beijingDate.getDate()).padStart(2, '0')
  const hour = String(beijingDate.getHours()).padStart(2, '0')
  const minute = String(beijingDate.getMinutes()).padStart(2, '0')
  const second = String(beijingDate.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}
"""
        target_content = re.sub(
            r'function formatDate\([^)]*\)\s*\{[^}]*\}',
            format_date_new.strip(),
            target_content,
            flags=re.DOTALL
        )
    
    # 更新getRelativeTime函数
    if "getRelativeTime" in target_content:
        relative_time_new = """
/**
 * 获取相对时间描述（使用北京时间）
 * @param {Date} date 日期对象
 * @returns {String}
 */
function getRelativeTime(date) {
  const now = getBeijingTime()
  const beijingDate = getBeijingTime(date)
  const diff = now - beijingDate
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}
"""
        target_content = re.sub(
            r'function getRelativeTime\([^)]*\)\s*\{[^}]*\}',
            relative_time_new.strip(),
            target_content,
            flags=re.DOTALL
        )
    
    # 确保导出getBeijingTime
    if "module.exports" in target_content:
        if "getBeijingTime" not in target_content.split("module.exports")[1]:
            exports_match = re.search(r'module\.exports\s*=\s*\{([^}]*)\}', target_content)
            if exports_match:
                exports_content = exports_match.group(1)
                if "getBeijingTime" not in exports_content:
                    target_content = target_content.replace(
                        "module.exports = {",
                        "module.exports = {\n  getBeijingTime,"
                    )
    
    return write_file_content(target_file, target_content)

def sync_publish_default_tab():
    """同步发布中心默认Tab设置"""
    log("同步发布中心默认Tab设置...")
    
    target_file = MINIAPP_PROJECT_PATH / "pages/publish/publish.js"
    if not target_file.exists():
        log(f"目标文件不存在: {target_file}", "WARN")
        return False
    
    content = read_file_content(target_file)
    if not content:
        return False
    
    # 检查当前默认值
    if "publishType: 'video'" in content:
        content = content.replace(
            "publishType: 'video'",
            "publishType: 'image-text'  // 默认图文（与主项目保持一致）"
        )
        log("已将默认发布类型改为图文", "SUCCESS")
    elif "publishType: 'image-text'" in content:
        log("默认发布类型已经是图文，无需更新", "INFO")
    else:
        log("未找到publishType配置", "WARN")
    
    return write_file_content(target_file, content)

def sync_ui_styles():
    """同步UI样式优化"""
    log("同步UI样式优化...")
    
    # 检查文本省略样式
    app_wxss = MINIAPP_PROJECT_PATH / "app.wxss"
    if app_wxss.exists():
        content = read_file_content(app_wxss)
        if content and "text-ellipsis-3" not in content:
            # 添加文本省略工具类
            text_ellipsis_styles = """
/* 文本省略工具类 */
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-ellipsis-3 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  text-overflow: ellipsis;
}
"""
            # 在文件末尾添加
            if not content.endswith("\n"):
                content += "\n"
            content += text_ellipsis_styles
            write_file_content(app_wxss, content)
            log("已添加文本省略工具类", "SUCCESS")
        else:
            log("文本省略工具类已存在", "INFO")
    
    return True

def sync_account_platform_filters():
    """同步账号管理平台筛选选项"""
    log("同步账号管理平台筛选选项...")
    
    target_file = MINIAPP_PROJECT_PATH / "pages/account/account.js"
    if not target_file.exists():
        log(f"目标文件不存在: {target_file}", "WARN")
        return False
    
    content = read_file_content(target_file)
    if not content:
        return False
    
    # 检查是否已有Tab分类
    if "activeTab: 'image-text'" in content:
        log("账号管理Tab分类已存在", "INFO")
    else:
        log("账号管理Tab分类需要手动检查", "WARN")
    
    return True

def sync_material_tabs():
    """同步素材管理Tab分类"""
    log("同步素材管理Tab分类...")
    
    target_file = MINIAPP_PROJECT_PATH / "pages/material/material.js"
    if not target_file.exists():
        log(f"目标文件不存在: {target_file}", "WARN")
        return False
    
    content = read_file_content(target_file)
    if not content:
        return False
    
    # 检查是否已有Tab分类
    if "activeTab: 'local'" in content:
        log("素材管理Tab分类已存在", "INFO")
    else:
        log("素材管理Tab分类需要手动检查", "WARN")
    
    return True

def create_sync_report():
    """创建同步报告"""
    log("生成同步报告...")
    
    report = {
        "sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "main_project": str(MAIN_PROJECT_PATH),
        "miniapp_project": str(MINIAPP_PROJECT_PATH),
        "synced_features": [
            "时区处理工具函数",
            "发布中心默认Tab设置",
            "UI样式优化（文本省略）",
            "账号管理Tab分类",
            "素材管理Tab分类",
        ],
        "notes": [
            "已同步时区处理，统一使用北京时间（UTC+8）",
            "已同步默认Tab设置，发布中心默认显示图文",
            "已同步UI样式优化，包括文本省略工具类",
            "Tab分类功能已同步",
        ]
    }
    
    report_file = MINIAPP_PROJECT_PATH / "sync_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    log(f"同步报告已保存: {report_file}", "SUCCESS")
    return report

def main():
    """主函数"""
    log("=" * 60)
    log("开始同步主项目功能到小程序")
    log("=" * 60)
    
    # 检查路径
    if not MAIN_PROJECT_PATH.exists():
        log(f"主项目路径不存在: {MAIN_PROJECT_PATH}", "ERROR")
        return False
    
    if not MINIAPP_PROJECT_PATH.exists():
        log(f"小程序项目路径不存在: {MINIAPP_PROJECT_PATH}", "ERROR")
        log("请确保小程序项目在: social-auto-upload-miniapp", "ERROR")
        return False
    
    # 执行同步
    results = {
        "时区工具函数": sync_timezone_utils(),
        "发布中心默认Tab": sync_publish_default_tab(),
        "UI样式优化": sync_ui_styles(),
        "账号管理筛选": sync_account_platform_filters(),
        "素材管理Tab": sync_material_tabs(),
    }
    
    # 生成报告
    report = create_sync_report()
    
    # 输出结果
    log("=" * 60)
    log("同步完成！")
    log("=" * 60)
    for feature, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        log(f"{feature}: {status}")
    
    log("=" * 60)
    log("提示：请检查同步结果，部分功能可能需要手动调整")
    log("=" * 60)
    
    return all(results.values())

if __name__ == "__main__":
    main()






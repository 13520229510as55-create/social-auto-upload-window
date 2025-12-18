#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版自动同步脚本 - 同步PC版功能到小程序
包括：制作中心页面、功能差异对比、UI优化等
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# 项目路径配置
MAIN_PROJECT_PATH = Path(__file__).parent
MINIAPP_PROJECT_PATH = MAIN_PROJECT_PATH.parent / "social-auto-upload-miniapp"

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "")
    print(f"[{timestamp}] {icon} [{level}] {message}")

def read_file(file_path):
    """读取文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log(f"读取文件失败: {file_path} - {e}", "ERROR")
        return None

def write_file(file_path, content):
    """写入文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        log(f"写入文件失败: {file_path} - {e}", "ERROR")
        return False

def check_feature_differences():
    """检查功能差异"""
    log("检查PC版和小程序版的功能差异...")
    
    differences = {
        "missing_pages": [],
        "missing_features": [],
        "ui_differences": []
    }
    
    # 检查制作中心页面
    production_center_pc = MAIN_PROJECT_PATH / "sau_frontend/src/views/ProductionCenter.vue"
    production_center_miniapp = MINIAPP_PROJECT_PATH / "pages/production/production.js"
    
    if production_center_pc.exists() and not production_center_miniapp.exists():
        differences["missing_pages"].append({
            "name": "制作中心",
            "description": "PC版有制作中心页面，小程序缺少",
            "priority": "high"
        })
    
    # 检查发布中心功能差异
    publish_pc = read_file(MAIN_PROJECT_PATH / "sau_frontend/src/views/PublishCenter.vue")
    publish_miniapp = read_file(MINIAPP_PROJECT_PATH / "pages/publish/publish.js")
    
    if publish_pc and publish_miniapp:
        # 检查Tab分类
        if "activeContentTypeTab" in publish_pc and "activeTab" not in publish_miniapp:
            differences["missing_features"].append({
                "page": "发布中心",
                "feature": "Tab分类（全部/图文/文章/视频）",
                "description": "PC版有Tab分类，小程序需要添加"
            })
    
    return differences

def create_production_center_page():
    """创建制作中心页面（简化版）"""
    log("创建制作中心页面...")
    
    production_dir = MINIAPP_PROJECT_PATH / "pages/production"
    production_dir.mkdir(exist_ok=True)
    
    # 创建 production.json
    production_json = {
        "navigationBarTitleText": "制作中心",
        "enablePullDownRefresh": True
    }
    write_file(
        production_dir / "production.json",
        json.dumps(production_json, ensure_ascii=False, indent=2)
    )
    
    # 创建 production.wxml
    production_wxml = '''<!--制作中心页面-->
<view class="production-container">
  <!-- 页面标题 -->
  <view class="page-header">
    <view class="page-title">制作中心</view>
    <view class="page-subtitle">创建和管理内容制作任务</view>
  </view>

  <!-- 新建任务按钮 -->
  <view class="create-task-section">
    <button class="create-task-btn" bindtap="createTask">
      <text class="btn-icon">➕</text>
      <text class="btn-text">新建任务</text>
    </button>
  </view>

  <!-- Tab分类 -->
  <view class="production-tabs">
    <view 
      class="tab-item {{activeTab === 'all' ? 'active' : ''}}"
      bindtap="switchTab"
      data-tab="all"
    >
      全部
    </view>
    <view 
      class="tab-item {{activeTab === 'video' ? 'active' : ''}}"
      bindtap="switchTab"
      data-tab="video"
    >
      视频
    </view>
    <view 
      class="tab-item {{activeTab === 'image-text' ? 'active' : ''}}"
      bindtap="switchTab"
      data-tab="image-text"
    >
      图文
    </view>
    <view 
      class="tab-item {{activeTab === 'article' ? 'active' : ''}}"
      bindtap="switchTab"
      data-tab="article"
    >
      文章
    </view>
  </view>

  <!-- 任务列表 -->
  <view class="task-list" wx:if="{{filteredTasks.length > 0}}">
    <view class="task-item" wx:for="{{filteredTasks}}" wx:key="id">
      <view class="task-header">
        <view class="task-type">
          <text class="type-tag type-{{item.contentType}}">{{item.typeLabel}}</text>
        </view>
        <view class="task-status">
          <text class="status-tag status-{{item.statusType}}">{{item.status}}</text>
        </view>
      </view>
      
      <view class="task-content">
        <view class="task-title">{{item.title}}</view>
        <view class="task-meta">
          <text class="meta-item">创建时间：{{item.createTime}}</text>
        </view>
      </view>
      
      <view class="task-actions">
        <button class="action-btn view" size="mini" bindtap="viewTask" data-id="{{item.id}}">
          查看
        </button>
        <button class="action-btn publish" size="mini" bindtap="publishTask" data-id="{{item.id}}">
          发布
        </button>
        <button class="action-btn delete" size="mini" bindtap="deleteTask" data-id="{{item.id}}">
          删除
        </button>
      </view>
    </view>
  </view>

  <!-- 空状态 -->
  <view class="empty-state" wx:else>
    <text class="empty-icon">📝</text>
    <text class="empty-text">暂无制作任务</text>
    <button class="empty-btn" bindtap="createTask">创建任务</button>
  </view>
</view>
'''
    write_file(production_dir / "production.wxml", production_wxml)
    
    # 创建 production.js
    production_js = '''/**
 * 制作中心页面
 */
const app = getApp()
const util = require('../../utils/util.js')

Page({
  data: {
    activeTab: 'all', // all, video, image-text, article
    tasks: [
      // 示例数据
    ],
    filteredTasks: []
  },

  /**
   * 页面加载
   */
  onLoad() {
    this.checkLogin()
    this.loadTasks()
  },

  /**
   * 检查登录状态
   */
  checkLogin() {
    if (!app.globalData.isLoggedIn) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }
  },

  /**
   * 加载任务列表
   */
  loadTasks() {
    // TODO: 从API加载任务列表
    this.filterTasks()
  },

  /**
   * 切换Tab
   */
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      activeTab: tab
    })
    this.filterTasks()
  },

  /**
   * 过滤任务
   */
  filterTasks() {
    const { activeTab, tasks } = this.data
    let filtered = tasks

    if (activeTab !== 'all') {
      filtered = filtered.filter(task => task.contentType === activeTab)
    }

    this.setData({
      filteredTasks: filtered
    })
  },

  /**
   * 创建任务
   */
  createTask() {
    wx.showActionSheet({
      itemList: ['视频任务', '图文任务', '文章任务'],
      success: (res) => {
        const types = ['video', 'image-text', 'article']
        const type = types[res.tapIndex]
        if (type) {
          wx.navigateTo({
            url: `/pages/production/create?type=${type}`
          })
        }
      }
    })
  },

  /**
   * 查看任务
   */
  viewTask(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/production/detail?id=${id}`
    })
  },

  /**
   * 发布任务
   */
  publishTask(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/publish/publish?taskId=${id}`
    })
  },

  /**
   * 删除任务
   */
  deleteTask(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这个任务吗？',
      success: (res) => {
        if (res.confirm) {
          // TODO: 调用API删除任务
          this.loadTasks()
        }
      }
    })
  }
})
'''
    write_file(production_dir / "production.js", production_js)
    
    # 创建 production.wxss
    production_wxss = '''/* 制作中心页面样式 */
.production-container {
  min-height: 100vh;
  padding: 30rpx;
  padding-bottom: 100rpx;
  background: #f5f7fa;
}

/* 页面标题 */
.page-header {
  margin-bottom: 30rpx;
}

.page-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #1e293b;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10rpx;
}

.page-subtitle {
  font-size: 24rpx;
  color: #64748b;
}

/* 新建任务按钮 */
.create-task-section {
  margin-bottom: 30rpx;
}

.create-task-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.3);
}

.create-task-btn::after {
  border: none;
}

.btn-icon {
  font-size: 40rpx;
}

/* Tab分类 */
.production-tabs {
  display: flex;
  background: white;
  border-radius: 16rpx;
  padding: 8rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 28rpx;
  font-weight: 600;
  color: #64748b;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.tab-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.task-item {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.type-tag {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.type-tag.type-video {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.type-tag.type-image-text {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.type-tag.type-article {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-tag {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.status-tag.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-tag.status-processing {
  background: rgba(251, 146, 60, 0.1);
  color: #fb923c;
}

.status-tag.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.task-content {
  margin-bottom: 20rpx;
}

.task-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12rpx;
  /* 文本省略，最多显示2行 */
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  font-size: 24rpx;
  color: #64748b;
}

.task-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  flex: 1;
  height: 64rpx;
  line-height: 64rpx;
  border-radius: 10rpx;
  font-size: 24rpx;
  font-weight: 600;
  border: none;
}

.action-btn::after {
  border: none;
}

.action-btn.view {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
  color: #3b82f6;
}

.action-btn.publish {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: #667eea;
}

.action-btn.delete {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
  color: #ef4444;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 20rpx;
  opacity: 0.6;
}

.empty-text {
  font-size: 28rpx;
  color: #94a3b8;
  margin-bottom: 40rpx;
}

.empty-btn {
  padding: 0 60rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: 600;
}

.empty-btn::after {
  border: none;
}

/* 响应式设计 */
@media screen and (max-width: 750rpx) {
  .production-tabs {
    flex-wrap: wrap;
    gap: 8rpx;
  }
  
  .tab-item {
    flex: 1 1 calc(50% - 8rpx);
    font-size: 26rpx;
    padding: 16rpx 0;
  }
  
  .task-item {
    padding: 24rpx;
  }
}
'''
    write_file(production_dir / "production.wxss", production_wxss)
    
    log("制作中心页面创建完成", "SUCCESS")
    return True

def update_app_json():
    """更新app.json，添加制作中心页面"""
    log("更新app.json配置...")
    
    app_json_path = MINIAPP_PROJECT_PATH / "app.json"
    if not app_json_path.exists():
        log("app.json不存在", "ERROR")
        return False
    
    content = read_file(app_json_path)
    if not content:
        return False
    
    try:
        config = json.loads(content)
        
        # 添加制作中心页面
        production_page = "pages/production/production"
        if production_page not in config.get("pages", []):
            # 插入到dashboard之后
            pages = config.get("pages", [])
            if "pages/dashboard/dashboard" in pages:
                index = pages.index("pages/dashboard/dashboard") + 1
                pages.insert(index, production_page)
            else:
                pages.append(production_page)
            config["pages"] = pages
            log("已添加制作中心页面到app.json", "SUCCESS")
        else:
            log("制作中心页面已存在", "INFO")
        
        # 更新内容
        new_content = json.dumps(config, ensure_ascii=False, indent=2)
        return write_file(app_json_path, new_content)
        
    except json.JSONDecodeError as e:
        log(f"JSON解析失败: {e}", "ERROR")
        return False

def sync_dashboard_improvements():
    """同步Dashboard改进"""
    log("同步Dashboard改进...")
    
    dashboard_js = MINIAPP_PROJECT_PATH / "pages/dashboard/dashboard.js"
    if not dashboard_js.exists():
        log("Dashboard文件不存在", "WARN")
        return False
    
    content = read_file(dashboard_js)
    if not content:
        return False
    
    # 检查是否需要添加制作中心导航
    if "navigateToProduction" not in content:
        # 添加导航函数
        nav_function = '''
  /**
   * 导航到制作中心
   */
  navigateToProduction() {
    wx.navigateTo({
      url: '/pages/production/production'
    })
  },
'''
        # 在navigateToPublish之后插入
        if "navigateToPublish" in content:
            content = content.replace(
                "  navigateToPublish() {",
                nav_function + "  navigateToPublish() {"
            )
            log("已添加制作中心导航函数", "SUCCESS")
    
    return write_file(dashboard_js, content)

def main():
    """主函数"""
    log("=" * 60)
    log("增强版同步脚本 - 同步PC版功能到小程序")
    log("=" * 60)
    
    # 检查路径
    if not MAIN_PROJECT_PATH.exists():
        log(f"主项目路径不存在: {MAIN_PROJECT_PATH}", "ERROR")
        return False
    
    if not MINIAPP_PROJECT_PATH.exists():
        log(f"小程序项目路径不存在: {MINIAPP_PROJECT_PATH}", "ERROR")
        return False
    
    # 检查功能差异
    differences = check_feature_differences()
    
    if differences["missing_pages"]:
        log(f"发现 {len(differences['missing_pages'])} 个缺失页面", "WARN")
        for page in differences["missing_pages"]:
            log(f"  - {page['name']}: {page['description']}", "WARN")
    
    # 执行同步
    results = {}
    
    # 1. 创建制作中心页面
    if differences["missing_pages"] and any(p["name"] == "制作中心" for p in differences["missing_pages"]):
        results["制作中心页面"] = create_production_center_page()
        if results["制作中心页面"]:
            results["更新app.json"] = update_app_json()
            results["Dashboard改进"] = sync_dashboard_improvements()
    
    # 2. 其他同步功能（从基础脚本）
    # 这里可以调用基础脚本的其他函数
    
    # 生成报告
    report = {
        "sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "differences_found": differences,
        "sync_results": results
    }
    
    report_file = MINIAPP_PROJECT_PATH / "sync_report_enhanced.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 输出结果
    log("=" * 60)
    log("同步完成！")
    log("=" * 60)
    for feature, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        log(f"{feature}: {status}")
    
    log("=" * 60)
    log(f"详细报告已保存: {report_file}")
    log("=" * 60)
    
    return all(results.values()) if results else True

if __name__ == "__main__":
    main()






<template>
  <div class="publish-center">
    <!-- 任务管理工具栏 -->
    <div class="task-toolbar">
      <div class="toolbar-info">
        <span class="task-count">
          <el-icon><Document /></el-icon>
          共 {{ tabs.length }} 个任务
        </span>
      </div>
      <div class="toolbar-actions">
        <el-button 
          class="select-all-btn"
          :disabled="productionRecords.length === 0"
          @click="toggleSelectAllRecords"
        >
          <el-icon><Finished /></el-icon>
          全选
        </el-button>
        <el-button 
          class="delete-selected-btn"
          type="danger"
          plain
          :disabled="selectedRecords.length === 0"
          @click="deleteSelectedRecords"
        >
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
        <div class="panel-header">
              
              <div class="panel-actions">
                <el-button
                  class="refresh-list-btn"
                  :loading="productionListLoading"
                  @click="refreshProductionRecords"
                >
                  <el-icon><RefreshRight /></el-icon>
                  刷新列表
                </el-button>
              </div>
            </div>
      </div>
    </div>

    <!-- 选择内容类型 Modal -->
    <el-dialog
      v-model="contentTypeDialogVisible"
      width="900px"
      class="content-type-dialog"
      :close-on-click-modal="false"
    >
      <template #header>
        <div class="dialog-header-custom">
          <h2>选择发布类型</h2>
          <p>根据您的需求选择合适的内容类型</p>
        </div>
      </template>
      
      <div class="content-type-selection">
        <div class="type-cards">
          <div 
            v-for="type in contentTypes" 
            :key="type.value"
            :class="['type-card', { selected: selectedContentType === type.value }]"
            @click="selectedContentType = type.value"
          >
            <div class="type-card-icon">
              <el-icon :size="56"><component :is="type.icon" /></el-icon>
            </div>
            <div class="type-card-content">
              <h3 class="type-card-title">{{ type.label }}</h3>
              <p class="type-card-desc">{{ type.description }}</p>
              <ul class="type-card-features" v-if="type.features">
                <li v-for="(feature, index) in type.features" :key="index">
                  <el-icon><Check /></el-icon>
                  <span>{{ feature }}</span>
                </li>
              </ul>
            </div>
            <div class="type-card-check" v-if="selectedContentType === type.value">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button @click="contentTypeDialogVisible = false" size="large">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmContentType" 
            size="large"
            :disabled="!selectedContentType"
          >
            <el-icon><Plus /></el-icon>
            确认创建
          </el-button>
        </div>
      </template>
    </el-dialog>

  <!-- 内容区域 -->
    <div class="publish-content">
      <div class="publish-tabs">
        <el-tabs v-model="activeContentTypeTab" class="publish-tabs-nav">
          <el-tab-pane label="全部" name="all">
            <div class="production-list-panel">
  
              <el-table
                ref="recordsTableRef"
                :data="filteredPublishRecords"
                :loading="productionListLoading"
                style="width: 100%;margin-top: 15px;"
                class="task-table"
                empty-text="暂无发布记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
          <el-table-column type="selection" width="30" />
          <el-table-column prop="created_at" label="创建时间" width="150">
            <template #default="scope">
              <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-publish-tooltip'">
                <div class="text-ellipsis">{{ scope.row.created_at }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="content_type" label="制作类型" width="90">
            <template #default="scope">
              <el-tag :type="getContentTypeTagType(scope.row.content_type)">
                <el-icon><component :is="getContentTypeIcon(scope.row.content_type)" /></el-icon>
                {{ getContentTypeLabel(scope.row.content_type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="platform" label="发布平台" width="90" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.platform" type="success">
                {{ scope.row.platform }}
              </el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>

          <el-table-column label="发布状态" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                {{ getPublishStatusLabel(scope.row.publish_status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="title" label="标题" min-width="150" class-name="title-column">
            <template #default="scope">
              <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          
          <el-table-column label="摘要" min-width="150" class-name="summary-column">
            <template #default="scope">
              <el-tooltip :content="scope.row.summary || formatContentPreview(scope.row.content, 60) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) }}</div>
              </el-tooltip>
            </template>
          </el-table-column>

          <el-table-column label="正文" min-width="150" class-name="content-column">
            <template #default="scope">
              <el-tooltip :content="formatContentPreview(scope.row.content) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) }}</div>
              </el-tooltip>
            </template>
          </el-table-column>

          <el-table-column label="图片/媒资链接" min-width="150">
            <template #default="scope">
              <el-tooltip 
                :content="scope.row.content_type === 'video' && scope.row.video ? scope.row.video : (scope.row.media_url || '—')" 
                placement="top" 
                :popper-class="'custom-publish-tooltip'"
              >
                <div>
                  <!-- 视频类型显示 video 字段 -->
                  <el-link
                    v-if="scope.row.content_type === 'video' && scope.row.video"
                    :href="scope.row.video"
                    target="_blank"
                    type="primary"
                  >
                    {{ scope.row.video }}
                  </el-link>
                  <!-- 其他类型显示 media_url -->
                  <el-link
                    v-else-if="scope.row.media_url"
                    :href="scope.row.media_url"
                    target="_blank"
                    type="primary"
                  >
                    查看链接
                  </el-link>
                  <span v-else>—</span>
                </div>
              </el-tooltip>
            </template>
          </el-table-column>

          <el-table-column label="其他配置" min-width="100">
            <template #default="scope">
              <el-tooltip 
                :content="scope.row.media_id ? `媒资ID：${scope.row.media_id}` : '—'" 
                placement="top" 
                :popper-class="'custom-publish-tooltip'"
              >
                <div class="text-ellipsis">
                  <span v-if="scope.row.media_id">
                    媒资ID：{{ scope.row.media_id }}
                  </span>
                  <span v-else>—</span>
                </div>
              </el-tooltip>
            </template>
          </el-table-column>
          
        
          
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="openRecordDetail(scope.row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button 
                size="small"
                type="danger"
                plain
                @click="deleteProductionRecord(scope.row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="图文" name="image-text">
            <div class="production-list-panel">
              <!-- <div class="panel-header">
              
                <div class="panel-actions">
                  <el-button
                    class="refresh-list-btn"
                    :loading="productionListLoading"
                    @click="refreshProductionRecords"
                  >
                    <el-icon><RefreshRight /></el-icon>
                    刷新列表3
                  </el-button>
                </div>
              </div> -->
              <el-table
                ref="recordsTableRef"
                :data="filteredPublishRecords"
                :loading="productionListLoading"
                style="width: 100%;margin-top: 15px;"
                class="task-table"
                empty-text="暂无图文发布记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
                <el-table-column type="selection" width="30" />
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.created_at }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="content_type" label="制作类型" width="90">
                  <template #default="scope">
                    <el-tag :type="getContentTypeTagType(scope.row.content_type)">
                      <el-icon><component :is="getContentTypeIcon(scope.row.content_type)" /></el-icon>
                      {{ getContentTypeLabel(scope.row.content_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="platform" label="发布平台" width="90" align="center">
                  <template #default="scope">
                    <el-tag v-if="scope.row.platform" type="success">
                      {{ scope.row.platform }}
                    </el-tag>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="发布状态" width="90" align="center">
                  <template #default="scope">
                    <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                      {{ getPublishStatusLabel(scope.row.publish_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="title" label="标题" min-width="150" class-name="title-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="摘要" min-width="150" class-name="summary-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.summary || formatContentPreview(scope.row.content, 60) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="正文" min-width="150" class-name="content-column">
                  <template #default="scope">
                    <el-tooltip :content="formatContentPreview(scope.row.content) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="图片/媒资链接" min-width="150">
                  <template #default="scope">
                    <el-tooltip 
                      :content="scope.row.media_url || '—'" 
                      placement="top" 
                      :popper-class="'custom-publish-tooltip'"
                    >
                      <div>
                        <el-link
                          v-if="scope.row.media_url"
                          :href="scope.row.media_url"
                          target="_blank"
                          type="primary"
                        >
                          查看链接
                        </el-link>
                        <span v-else>—</span>
                      </div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="其他配置" min-width="100">
                  <template #default="scope">
                    <el-tooltip 
                      :content="scope.row.media_id ? `媒资ID：${scope.row.media_id}` : '—'" 
                      placement="top" 
                      :popper-class="'custom-publish-tooltip'"
                    >
                      <div class="text-ellipsis">
                        <span v-if="scope.row.media_id">
                          媒资ID：{{ scope.row.media_id }}
                        </span>
                        <span v-else>—</span>
                      </div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" fixed="right">
                  <template #default="scope">
                    <el-button size="small" @click="openRecordDetail(scope.row)">
                      <el-icon><View /></el-icon>
                      详情
                    </el-button>
                    <el-button 
                      size="small"
                      type="danger"
                      plain
                      @click="deleteProductionRecord(scope.row)"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="文章" name="article">
            <div class="production-list-panel">
   
              <el-table
                ref="recordsTableRef"
                :data="filteredPublishRecords"
                :loading="productionListLoading"
                style="width: 100%;margin-top: 15px;"
                class="task-table"
                empty-text="暂无文章发布记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
                <el-table-column type="selection" width="30" />
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.created_at }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="content_type" label="制作类型" width="90">
                  <template #default="scope">
                    <el-tag :type="getContentTypeTagType(scope.row.content_type)">
                      <el-icon><component :is="getContentTypeIcon(scope.row.content_type)" /></el-icon>
                      {{ getContentTypeLabel(scope.row.content_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="platform" label="发布平台" width="90" align="center">
                  <template #default="scope">
                    <el-tag v-if="scope.row.platform" type="success">
                      {{ scope.row.platform }}
                    </el-tag>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="发布状态" width="90" align="center">
                  <template #default="scope">
                    <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                      {{ getPublishStatusLabel(scope.row.publish_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="title" label="标题" min-width="150" class-name="title-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="摘要" min-width="150" class-name="summary-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.summary || formatContentPreview(scope.row.content, 60) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="正文" min-width="150" class-name="content-column">
                  <template #default="scope">
                    <el-tooltip :content="formatContentPreview(scope.row.content) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="图片/媒资链接" min-width="150">
                  <template #default="scope">
                    <el-tooltip 
                      :content="scope.row.media_url || '—'" 
                      placement="top" 
                      :popper-class="'custom-publish-tooltip'"
                    >
                      <div>
                        <el-link
                          v-if="scope.row.media_url"
                          :href="scope.row.media_url"
                          target="_blank"
                          type="primary"
                        >
                          查看链接
                        </el-link>
                        <span v-else>—</span>
                      </div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="其他配置" min-width="100">
                  <template #default="scope">
                    <el-tooltip 
                      :content="scope.row.media_id ? `媒资ID：${scope.row.media_id}` : '—'" 
                      placement="top" 
                      :popper-class="'custom-publish-tooltip'"
                    >
                      <div class="text-ellipsis">
                        <span v-if="scope.row.media_id">
                          媒资ID：{{ scope.row.media_id }}
                        </span>
                        <span v-else>—</span>
                      </div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" fixed="right">
                  <template #default="scope">
                    <el-button size="small" @click="openRecordDetail(scope.row)">
                      <el-icon><View /></el-icon>
                      详情
                    </el-button>
                    <el-button 
                      size="small"
                      type="danger"
                      plain
                      @click="deleteProductionRecord(scope.row)"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="视频" name="video">
            <div class="production-list-panel">
      
              <el-table
                ref="recordsTableRef"
                :data="filteredPublishRecords"
                :loading="productionListLoading"
                style="width: 100%;margin-top: 15px;"
                class="task-table"
                empty-text="暂无视频发布记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
                <el-table-column type="selection" width="30" />
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.created_at }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="content_type" label="制作类型" width="90">
                  <template #default="scope">
                    <el-tag :type="getContentTypeTagType(scope.row.content_type)">
                      <el-icon><component :is="getContentTypeIcon(scope.row.content_type)" /></el-icon>
                      {{ getContentTypeLabel(scope.row.content_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="platform" label="发布平台" width="90" align="center">
                  <template #default="scope">
                    <el-tag v-if="scope.row.platform" type="success">
                      {{ scope.row.platform }}
                    </el-tag>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="发布状态" width="90" align="center">
                  <template #default="scope">
                    <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                      {{ getPublishStatusLabel(scope.row.publish_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="title" label="标题" min-width="150" class-name="title-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="摘要" min-width="150" class-name="summary-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.summary || formatContentPreview(scope.row.content, 60) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="正文" min-width="150" class-name="content-column">
                  <template #default="scope">
                    <el-tooltip :content="formatContentPreview(scope.row.content) || '—'" placement="top" :popper-class="'custom-publish-tooltip'">
                      <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="图片/媒资链接" min-width="150">
                  <template #default="scope">
                    <el-link
                      v-if="scope.row.video"
                      :href="scope.row.video"
                      target="_blank"
                      type="primary"
                    >
                      {{ scope.row.video }}
                    </el-link>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="其他配置" min-width="100" show-overflow-tooltip>
                  <template #default="scope">
                    <span v-if="scope.row.media_id">
                      媒资ID：{{ scope.row.media_id }}
                    </span>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" fixed="right">
                  <template #default="scope">
                    <el-button size="small" @click="openRecordDetail(scope.row)">
                      <el-icon><View /></el-icon>
                      详情
                    </el-button>
                    <el-button 
                      size="small"
                      type="danger"
                      plain
                      @click="deleteProductionRecord(scope.row)"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>



      <div class="tab-content-wrapper">
        <div 
          v-for="tab in tabs" 
          :key="tab.name"
          v-show="activeTab === tab.name"
          class="tab-content"
        >
          <!-- 发布状态提示 -->
          <div v-if="tab.publishStatus" class="publish-status">
            <el-alert
              :title="tab.publishStatus.message"
              :type="tab.publishStatus.type"
              :closable="false"
              show-icon
            />
          </div>

          <!-- 视频类型内容 -->
          <div v-if="currentPublishRecord?.content_type === 'video'" class="video-content">
            <!-- 1. 视频上传 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>视频 <span class="required">*</span></h3>
                <div class="upload-options">
                  <el-button type="primary" @click="showUploadOptions(tab)" class="upload-btn">
                    <el-icon><Upload /></el-icon>
                    上传视频
                  </el-button>
                </div>
                
                <!-- 已上传文件列表 -->
                <div v-if="tab.fileList.length > 0" class="uploaded-files">
                  <div class="file-list">
                    <div v-for="(file, index) in tab.fileList" :key="index" class="file-item">
                      <el-link :href="file.url" target="_blank" type="primary">{{ file.name }}</el-link>
                      <span class="file-size">{{ (file.size / 1024 / 1024).toFixed(2) }}MB</span>
                      <el-button type="danger" size="small" @click="removeFile(tab, index)">删除</el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          <!-- 上传选项弹窗 -->
          <el-dialog
            v-model="uploadOptionsVisible"
            v-if="currentPublishRecord?.content_type === 'video'"
            title="选择上传方式"
            width="400px"
            class="upload-options-dialog"
          >
            <div class="upload-options-content">
              <el-button type="primary" @click="selectLocalUpload" class="option-btn">
                <el-icon><Upload /></el-icon>
                本地上传
              </el-button>
              <el-button type="success" @click="selectMaterialLibrary" class="option-btn">
                <el-icon><Folder /></el-icon>
                素材库
              </el-button>
            </div>
          </el-dialog>

          <!-- 本地上传弹窗 -->
          <el-dialog
            v-model="localUploadVisible"
            v-if="currentPublishRecord?.content_type === 'video'"
            title="本地上传"
            width="600px"
            class="local-upload-dialog"
          >
            <el-upload
              class="video-upload"
              drag
              :auto-upload="true"
              :action="`${apiBaseUrl}/upload`"
              :on-success="(response, file) => handleUploadSuccess(response, file, currentUploadTab)"
              :on-error="handleUploadError"
              multiple
              accept="video/*"
              :headers="authHeaders"
            >
              <el-icon class="el-icon--upload"><Upload /></el-icon>
              <div class="el-upload__text">
                将视频文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持MP4、AVI等视频格式，可上传多个文件
                </div>
              </template>
            </el-upload>
          </el-dialog>

          <!-- 批量发布进度对话框 -->
          <el-dialog
            v-model="batchPublishDialogVisible"
            title="批量发布进度"
            width="500px"
            :close-on-click-modal="false"
            :close-on-press-escape="false"
            :show-close="false"
          >
            <div class="publish-progress">
              <el-progress 
                :percentage="publishProgress"
                :status="publishProgress === 100 ? 'success' : ''"
              />
              <div v-if="currentPublishingTab" class="current-publishing">
                正在发布：{{ currentPublishingTab.label }}
              </div>
              
              <!-- 发布结果列表 -->
              <div class="publish-results" v-if="publishResults.length > 0">
                <div 
                  v-for="(result, index) in publishResults" 
                  :key="index"
                  :class="['result-item', result.status]"
                >
                  <el-icon v-if="result.status === 'success'"><Check /></el-icon>
                  <el-icon v-else-if="result.status === 'error'"><Close /></el-icon>
                  <el-icon v-else><InfoFilled /></el-icon>
                  <span class="label">{{ result.label }}</span>
                  <span class="message">{{ result.message }}</span>
                </div>
              </div>
            </div>
            
            <template #footer>
              <div class="dialog-footer">
                <el-button 
                  @click="cancelBatchPublish" 
                  :disabled="publishProgress === 100"
                >
                  取消发布
                </el-button>
                <el-button 
                  type="primary" 
                  @click="batchPublishDialogVisible = false"
                  v-if="publishProgress === 100"
                >
                  关闭
                </el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 素材库选择弹窗 -->
          <el-dialog
            v-model="materialLibraryVisible"
            title="选择素材"
            width="800px"
            class="material-library-dialog"
          >
            <div class="material-library-content">
              <!-- 筛选选项 -->
              <div class="material-filter" style="margin-bottom: 16px;">
                <el-radio-group v-model="materialSourceFilter" @change="handleMaterialFilterChange">
                  <el-radio-button label="">全部素材</el-radio-button>
                  <el-radio-button label="生成素材">生成素材</el-radio-button>
                  <el-radio-button label="本地上传">原始素材</el-radio-button>
                  <el-radio-button label="谷歌存储上传">谷歌存储</el-radio-button>
                </el-radio-group>
              </div>
              
              <el-checkbox-group v-model="selectedMaterials">
                <div class="material-list">
                  <div
                    v-for="material in filteredMaterials"
                    :key="material.id"
                    class="material-item"
                  >
                    <el-checkbox :label="material.id" class="material-checkbox">
                      <div class="material-info">
                        <div class="material-name">{{ material.filename }}</div>
                        <div class="material-details">
                          <el-tag 
                            :type="material.source === '生成素材' ? 'success' : material.source === '本地上传' ? 'primary' : 'info'"
                            size="small"
                            style="margin-right: 8px;"
                          >
                            {{ material.source || '本地上传' }}
                          </el-tag>
                          <span class="file-size">{{ material.filesize || 0 }}MB</span>
                          <span class="upload-time">{{ material.upload_time }}</span>
                        </div>
                      </div>
                    </el-checkbox>
                  </div>
                </div>
              </el-checkbox-group>
              
              <el-empty v-if="filteredMaterials.length === 0" description="暂无素材" />
            </div>
            <template #footer>
              <div class="dialog-footer">
                <el-button @click="materialLibraryVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmMaterialSelection">确定</el-button>
              </div>
            </template>
          </el-dialog>

            <!-- 2. 账号选择 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>账号 <span class="required">*</span></h3>
                <div class="account-display">
                  <div class="selected-accounts">
                    <el-tag
                      v-for="(account, index) in tab.selectedAccounts"
                      :key="index"
                      closable
                      @close="removeAccount(tab, index)"
                      class="account-tag"
                    >
                      {{ getAccountDisplayName(account) }}
                    </el-tag>
                  </div>
                  <el-button 
                    type="primary" 
                    plain 
                    @click="openAccountDialog(tab)"
                    class="select-account-btn"
                  >
                    选择账号
                  </el-button>
                </div>
              </div>
            </div>

          <!-- 账号选择弹窗 -->
          <el-dialog
            v-model="accountDialogVisible"
            title="选择账号"
            width="600px"
            class="account-dialog"
          >
            <div class="account-dialog-content">
              <el-checkbox-group v-model="tempSelectedAccounts">
                <div class="account-list">
                  <el-checkbox
                    v-for="account in availableAccounts"
                    :key="account.id"
                    :label="account.id"
                    class="account-item"
                  >
                    <div class="account-info">
                      <span class="account-name">{{ account.name }}</span>                      
                    </div>
                  </el-checkbox>
                </div>
              </el-checkbox-group>
            </div>

            <template #footer>
              <div class="dialog-footer">
                <el-button @click="accountDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmAccountSelection">确定</el-button>
              </div>
            </template>
          </el-dialog>

            <!-- 3. 平台选择 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>平台 <span class="required">*</span></h3>
                <el-radio-group v-model="tab.selectedPlatform" class="platform-radios">
                  <el-radio 
                    v-for="platform in platforms" 
                    :key="platform.key"
                    :label="platform.key"
                    class="platform-radio"
                  >
                    {{ platform.name }}
                  </el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 4. 草稿选项 (仅在视频号可见) -->
            <div v-if="tab.selectedPlatform === 2" class="form-grid">
              <div class="form-section form-section-full">
                <h3>草稿选项</h3>
                <el-checkbox
                  v-model="tab.isDraft"
                  label="视频号仅保存草稿(用手机发布)"
                  class="draft-checkbox"
                />
              </div>
            </div>

            <!-- 5. 商品链接 (仅在抖音可见) -->
            <div v-if="tab.selectedPlatform === 3" class="form-grid">
              <div class="form-section">
                <h3>商品名称</h3>
                <el-input
                  v-model="tab.productTitle"
                  type="text"
                  placeholder="请输入商品名称"
                  maxlength="200"
                />
              </div>
              <div class="form-section">
                <h3>商品链接</h3>
                <el-input
                  v-model="tab.productLink"
                  type="text"
                  placeholder="请输入商品链接"
                  maxlength="200"
                />
              </div>
            </div>

            <!-- 6. 标题输入 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>标题</h3>
                <el-input
                  v-model="tab.title"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入标题"
                  maxlength="100"
                  show-word-limit
                />
              </div>
            </div>

            <!-- 7. 话题输入 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>话题</h3>
                <div class="topic-display">
                  <div class="selected-topics">
                    <el-tag
                      v-for="(topic, index) in tab.selectedTopics"
                      :key="index"
                      closable
                      @close="removeTopic(tab, index)"
                      class="topic-tag"
                    >
                      #{{ topic }}
                    </el-tag>
                  </div>
                  <el-button 
                    type="primary" 
                    plain 
                    @click="openTopicDialog(tab)"
                    class="select-topic-btn"
                  >
                    添加话题
                  </el-button>
                </div>
              </div>
            </div>

          <!-- 添加话题弹窗 -->
          <el-dialog
            v-model="topicDialogVisible"
            title="添加话题"
            width="600px"
            class="topic-dialog"
          >
            <div class="topic-dialog-content">
              <!-- 自定义话题输入 -->
              <div class="custom-topic-input">
                <el-input
                  v-model="customTopic"
                  placeholder="输入自定义话题"
                  class="custom-input"
                >
                  <template #prepend>#</template>
                </el-input>
                <el-button type="primary" @click="addCustomTopic">添加</el-button>
              </div>

              <!-- 推荐话题 -->
              <div class="recommended-topics">
                <h4>推荐话题</h4>
                <div class="topic-grid">
                  <el-button
                    v-for="topic in recommendedTopics"
                    :key="topic"
                    :type="currentTab?.selectedTopics?.includes(topic) ? 'primary' : 'default'"
                    @click="toggleRecommendedTopic(topic)"
                    class="topic-btn"
                  >
                    {{ topic }}
                  </el-button>
                </div>
              </div>
            </div>

            <template #footer>
              <div class="dialog-footer">
                <el-button @click="topicDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmTopicSelection">确定</el-button>
              </div>
            </template>
          </el-dialog>

            <!-- 8. 定时发布 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>定时发布</h3>
                <div class="schedule-controls">
                  <el-switch
                    v-model="tab.scheduleEnabled"
                    active-text="定时发布"
                    inactive-text="立即发布"
                  />
                  <div v-if="tab.scheduleEnabled" class="schedule-settings">
                    <div class="schedule-item">
                      <span class="label">每天发布视频数：</span>
                      <el-select v-model="tab.videosPerDay" placeholder="选择发布数量">
                        <el-option
                          v-for="num in 55"
                          :key="num"
                          :label="num"
                          :value="num"
                        />
                      </el-select>
                    </div>
                    <div class="schedule-item">
                      <span class="label">每天发布时间：</span>
                      <el-time-select
                        v-for="(time, index) in tab.dailyTimes"
                        :key="index"
                        v-model="tab.dailyTimes[index]"
                        start="00:00"
                        step="00:30"
                        end="23:30"
                        placeholder="选择时间"
                      />
                      <el-button
                        v-if="tab.dailyTimes.length < tab.videosPerDay"
                        type="primary"
                        size="small"
                        @click="tab.dailyTimes.push('10:00')"
                      >
                        添加时间
                      </el-button>
                    </div>
                    <div class="schedule-item">
                      <span class="label">开始天数：</span>
                      <el-select v-model="tab.startDays" placeholder="选择开始天数">
                        <el-option :label="'明天'" :value="0" />
                        <el-option :label="'后天'" :value="1" />
                      </el-select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button size="small" @click="cancelPublish(tab)">取消</el-button>
              <el-button
                size="small"
                type="primary"
                @click="confirmPublish(tab)"
                :loading="tab.publishing || false"
              >
                {{ tab.publishing ? '发布中...' : '发布' }}
              </el-button>
            </div>
          </div>

          <!-- 图文类型内容 -->
          <div v-else-if="tab.contentType === 'image-text'" class="image-text-content">
            <!-- 1. 内容来源类型 + 10. 生图模型 -->
            <div class="form-grid">
              <div class="form-section">
                <h3>内容来源类型 <span class="required">*</span></h3>
                <el-radio-group v-model="tab.imageText.contentSourceType">
                  <el-radio label="xiaohongshu">小红书链接</el-radio>
                  <el-radio label="other">其他链接</el-radio>
                  <el-radio label="custom">自定义内容</el-radio>
                </el-radio-group>
              </div>

              <div class="form-section">
                <h3>生图模型 <span class="required">*</span></h3>
                <el-radio-group v-model="tab.imageText.imageModel">
                  <el-radio label="qianwen">千问</el-radio>
                  <el-radio label="jimeng">即梦</el-radio>
                  <el-radio label="sora">Sora</el-radio>
                  <el-radio label="nabana">nabana</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 2. 输入内容 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>输入内容 <span class="required">*</span></h3>
                <el-input
                  v-model="tab.imageText.inputContent"
                  type="textarea"
                  :rows="3"
                  placeholder="根据上方来源输入对应的文案主题/文案内容/url链接"
                  maxlength="2000"
                  show-word-limit
                />
              </div>
            </div>

            <!-- 3. 内容排版风格 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>内容排版风格 <span class="required">*</span></h3>
                <el-radio-group v-model="tab.imageText.contentLayoutStyle">
                  <el-radio label="xiaohongshu-hot">小红书爆款风格</el-radio>
                  <el-radio label="builtin-common">内置排版风格-通用风格</el-radio>
                  <el-radio label="builtin-female">内置排版风格-女性成长</el-radio>
                  <el-radio label="builtin-food">内置排版风格-美食探店</el-radio>
                  <el-radio label="builtin-baby">内置排版风格-母婴</el-radio>
                  <el-radio label="builtin-recommend">内置排版风格-好物推荐</el-radio>
                  <el-radio label="builtin-home">内置排版风格-家居</el-radio>
                  <el-radio label="builtin-outdoor">内置排版风格-户外出行</el-radio>
                  <el-radio label="builtin-beauty">内置排版风格-美妆穿搭</el-radio>
                  <el-radio label="builtin-business">内置排版风格-创业创业</el-radio>
                  <el-radio label="builtin-skill">内置排版风格-知识技能</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 4. 内容排版类型-小红书爆款风格 (条件显示) -->
            <div v-if="tab.imageText.contentLayoutStyle === 'xiaohongshu-hot'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>内容排版类型-小红书爆款风格</h3>
                <el-input
                  v-model="tab.imageText.contentLayoutReference"
                  placeholder="输入参考小红书爆款排版的链接"
                />
              </div>
            </div>

            <!-- 5. 配图风格类型选择 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图风格类型选择</h3>
                <el-radio-group v-model="tab.imageText.imageStyleType">
                  <el-radio label="ai-auto">AI智能生成-风格根据文案生成</el-radio>
                  <el-radio label="builtin-notebook">内置配图风格-记事本风格</el-radio>
                  <el-radio label="builtin-common">内置配图风格-普通风格</el-radio>
                  <el-radio label="xhs-bigtext">小红书爆款配图风格-大字报内容</el-radio>
                  <el-radio label="xhs-keyword">小红书爆款配图风格-关键字替换</el-radio>
                  <el-radio label="builtin-ai-yes">内置图片ai处理</el-radio>
                  <el-radio label="builtin-ai-no">内置图片ai不处理</el-radio>
                  <el-radio label="external-ai-yes">外置图片ai处理</el-radio>
                  <el-radio label="external-ai-no">外置图片ai不处理</el-radio>
                  <el-radio label="info-graphic">信息图</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 6. 配图风格选择-小红书爆款参考链接 (条件显示) -->
            <div v-if="['xhs-bigtext', 'xhs-keyword'].includes(tab.imageText.imageStyleType)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图风格选择-小红书爆款参考链接</h3>
                <el-input
                  v-model="tab.imageText.imageStyleReference"
                  placeholder="输入配图参考小红书链接"
                />
              </div>
            </div>

            <!-- 7. 封面图风格类型选择 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图风格类型选择</h3>
                <el-radio-group v-model="tab.imageText.coverStyleType">
                  <el-radio label="ai-auto">AI智能生成-风格根据文案生成</el-radio>
                  <el-radio label="builtin-notebook">内置配图风格-记事本风格</el-radio>
                  <el-radio label="builtin-common">内置配图风格-普通风格</el-radio>
                  <el-radio label="xhs-bigtext">小红书爆款配图风格-大字报内容</el-radio>
                  <el-radio label="xhs-keyword">小红书爆款配图风格-关键字替换</el-radio>
                  <el-radio label="article-image">文章内置图片</el-radio>
                  <el-radio label="info-graphic">信息图</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 13. 封面图-信息图类型 (条件显示 - 紧跟第7项) -->
            <div v-if="tab.imageText.coverStyleType === 'info-graphic'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图-信息图类型</h3>
                <el-radio-group v-model="tab.imageText.infoGraphicType">
                  <el-radio label="minimalist-tech">极简技术风</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 8. 封面图风格选择-小红书爆款风格 (条件显示) -->
            <div v-if="['xhs-bigtext', 'xhs-keyword'].includes(tab.imageText.coverStyleType)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图风格选择-小红书爆款风格</h3>
                <el-input
                  v-model="tab.imageText.coverStyleReference"
                  placeholder="输入封面图参考链接"
                />
              </div>
            </div>

            <!-- 9. 配图张数 + 11. 发布平台 -->
            <div class="form-grid">
              <div class="form-section">
                <h3>配图张数</h3>
                <el-radio-group v-model="tab.imageText.imageCount">
                  <el-radio :label="1">1</el-radio>
                  <el-radio :label="2">2</el-radio>
                  <el-radio :label="3">3</el-radio>
                  <el-radio :label="4">4</el-radio>
                  <el-radio :label="5">5</el-radio>
                  <el-radio :label="6">6</el-radio>
                  <el-radio :label="7">7</el-radio>
                  <el-radio :label="8">8</el-radio>
                  <el-radio :label="9">9</el-radio>
                </el-radio-group>
              </div>

              <div class="form-section">
                <h3>发布平台 <span class="required">*</span></h3>
                <el-radio-group v-model="tab.imageText.publishPlatform">
                  <el-radio label="xiaohongshu">小红书图文</el-radio>
                  <el-radio label="wechat">微信图文</el-radio>
                  <el-radio label="bilibili">B站图文</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 12. 图文内容字数 (全宽) -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>图文内容字数 <span class="required">*</span></h3>
                <el-radio-group v-model="tab.imageText.contentWordCount" class="word-count-group">
                  <el-radio :label="100">100</el-radio>
                  <el-radio :label="200">200</el-radio>
                  <el-radio :label="300">300</el-radio>
                  <el-radio :label="400">400</el-radio>
                  <el-radio :label="500">500</el-radio>
                  <el-radio :label="600">600</el-radio>
                  <el-radio :label="700">700</el-radio>
                  <el-radio :label="800">800</el-radio>
                  <el-radio :label="900">900</el-radio>
                  <el-radio :label="1000">1000</el-radio>
                  <el-radio :label="1100">1100</el-radio>
                  <el-radio :label="1200">1200</el-radio>
                  <el-radio :label="1300">1300</el-radio>
                  <el-radio :label="1400">1400</el-radio>
                  <el-radio :label="1500">1500</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 14. 配图风格类型选择-文章外图片-文章链接 + 15. 文章来源 (条件显示) -->
            <div v-if="['external-ai-yes', 'external-ai-no'].includes(tab.imageText.imageStyleType)" class="form-grid">
              <div class="form-section">
                <h3>配图风格类型选择-文章外图片-文章链接</h3>
                <el-input
                  v-model="tab.imageText.externalArticleLink"
                  placeholder="输入文章链接"
                />
              </div>

              <div class="form-section">
                <h3>配图风格类型选择-文章外图片-文章来源</h3>
                <el-radio-group v-model="tab.imageText.externalArticleSource">
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="zhihu">知乎</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button size="small" @click="cancelPublish(tab)">取消</el-button>
              <el-button
                size="small"
                type="primary"
                @click="confirmPublishImageText(tab)"
                :loading="tab.publishing || false"
              >
                {{ tab.publishing ? '生成中...' : '生成内容' }}
              </el-button>
            </div>
          </div>

          <!-- 文章类型内容 -->
          <div v-else-if="tab.contentType === 'article'" class="article-content">

            <!-- 6. 仿写-主题内容 -->
            <div v-if="tab.article.writingMode === 'imitate'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>仿写-主题内容</h3>
                <el-input
                  v-model="tab.article.imitateTopic"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入你的主题或者片段内容"
                />
              </div>
            </div>

            <!-- 7. 仿写-文章长短 -->
            <div v-if="tab.article.writingMode === 'imitate'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>仿写-文章长短</h3>
                <el-select v-model="tab.article.imitateLength" placeholder="Select an option" style="width: 100%">
                  <el-option label="短篇 (1000-2000字)" value="short" />
                  <el-option label="中篇 (2000-5000字)" value="medium" />
                  <el-option label="长篇 (5000字以上)" value="long" />
                </el-select>
              </div>
            </div>

            <!-- 8. 原创-深度研究领域关键词 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-深度研究领域关键词</h3>
                <el-input
                  v-model="tab.article.originalKeywords"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入深度研究领域关键词"
                />
              </div>
            </div>

            <!-- 9. 原创-当前层次 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-当前层次</h3>
                <el-radio-group v-model="tab.article.originalLevel">
                  <el-radio label="novice">小白 (完全陌生)</el-radio>
                  <el-radio label="beginner">入门 (理论储备)</el-radio>
                  <el-radio label="junior">初级实操者 (有限经验)</el-radio>
                  <el-radio label="senior">资深应用者 (丰富经验)</el-radio>
                  <el-radio label="expert">领域权威 (专家级)</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 10. 原创-学习目的 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-学习目的</h3>
                <el-radio-group v-model="tab.article.originalPurpose">
                  <el-radio label="concept">概念理解</el-radio>
                  <el-radio label="problem">问题解决</el-radio>
                  <el-radio label="practice">应用实践</el-radio>
                  <el-radio label="skill">技能掌握</el-radio>
                  <el-radio label="career">职业发展</el-radio>
                  <el-radio label="knowledge">知识建构</el-radio>
                  <el-radio label="teaching">教学与分享</el-radio>
                  <el-radio label="innovation">创新与研究</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 11. 原创-文章是否需要配图 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-文章是否需要配图</h3>
                <el-radio-group v-model="tab.article.originalNeedImage">
                  <el-radio label="yes">是</el-radio>
                  <el-radio label="no">否</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 12. 原创-是否自动化 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-是否自动化</h3>
                <el-radio-group v-model="tab.article.originalAutomation">
                  <el-radio label="auto">自动化</el-radio>
                  <el-radio label="step">分步骤</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 13. 原创-研究主题探究的深度 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-研究主题探究的深度</h3>
                <el-radio-group v-model="tab.article.originalDepth">
                  <el-radio :label="1">1</el-radio>
                  <el-radio :label="2">2</el-radio>
                  <el-radio :label="3">3</el-radio>
                  <el-radio :label="5">5</el-radio>
                  <el-radio :label="10">10</el-radio>
                  <el-radio :label="20">20</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 14. 原创-报告期望字数 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-报告期望字数</h3>
                <el-radio-group v-model="tab.article.originalWordCount" class="word-count-group">
                  <el-radio :label="1000">1000</el-radio>
                  <el-radio :label="2000">2000</el-radio>
                  <el-radio :label="3000">3000</el-radio>
                  <el-radio :label="4000">4000</el-radio>
                  <el-radio :label="5000">5000</el-radio>
                  <el-radio :label="6000">6000</el-radio>
                  <el-radio :label="7000">7000</el-radio>
                  <el-radio :label="8000">8000</el-radio>
                  <el-radio :label="10000">10000</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 15. 原创-报告期望语言 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-报告期望语言</h3>
                <el-radio-group v-model="tab.article.originalLanguage">
                  <el-radio label="zh-cn">中文简体</el-radio>
                  <el-radio label="zh-tw">中文繁体</el-radio>
                  <el-radio label="en">英语</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 16. 原创-提示词字数 -->
            <div v-if="tab.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-提示词字数</h3>
                <el-radio-group v-model="tab.article.originalPromptCount" class="word-count-group">
                  <el-radio :label="100">100</el-radio>
                  <el-radio :label="200">200</el-radio>
                  <el-radio :label="300">300</el-radio>
                  <el-radio :label="400">400</el-radio>
                  <el-radio :label="500">500</el-radio>
                  <el-radio :label="600">600</el-radio>
                  <el-radio :label="700">700</el-radio>
                  <el-radio :label="800">800</el-radio>
                  <el-radio :label="1000">1000</el-radio>
                </el-radio-group>
              </div>
            </div>


            <!-- 操作按钮 -->
            <!-- <div class="action-buttons">
              <el-button
                size="small"
                type="primary"
                @click="confirmPublishArticle(tab)"
                :loading="tab.publishing || false"
              >
                {{ tab.publishing ? '发送中...' : '发送' }}
              </el-button>
            </div> -->
          </div>

        </div>
      </div>
    </div>

    <el-dialog
      v-model="recordDetailVisible"
      width="720px"
      :title="currentRecordDetail?.title || '制作详情'"
    >
      <div v-if="currentRecordDetail" class="record-detail">
        <div class="detail-meta">
          <p><strong>内容类型：</strong>{{ getContentTypeLabel(currentRecordDetail.content_type) }}</p>
          <p><strong>创建时间：</strong>{{ currentRecordDetail.created_at || '—' }}</p>
        </div>
        <div class="detail-block" v-if="currentRecordDetail.summary">
          <h4>摘要</h4>
          <p>{{ currentRecordDetail.summary }}</p>
        </div>
        <div class="detail-block">
          <h4>正文</h4>
          <MobileArticlePreview
            :title="currentRecordDetail.title"
            :summary="currentRecordDetail.summary"
            :content="currentRecordDetail.content || ''"
            :created-at="currentRecordDetail.created_at"
            :cover-url="currentRecordDetail.media_url"
            :author="currentRecordDetail.author || 'AI创作助手'"
            :source-label="getContentTypeLabel(currentRecordDetail.content_type || 'article')"
          />
        </div>
        <div class="detail-block meta-grid">
          <div>
            <h4>媒资 ID</h4>
            <p>{{ currentRecordDetail.media_id || '—' }}</p>
          </div>
          <div>
            <h4>媒资链接</h4>
            <p>
              <!-- 视频类型显示 video 字段 -->
              <el-link
                v-if="currentRecordDetail.content_type === 'video' && currentRecordDetail.video"
                :href="currentRecordDetail.video"
                target="_blank"
                type="primary"
              >
                {{ currentRecordDetail.video }}
              </el-link>
              <!-- 其他类型显示 media_url -->
              <el-link
                v-else-if="currentRecordDetail.media_url"
                :href="currentRecordDetail.media_url"
                target="_blank"
                type="primary"
              >
                {{ currentRecordDetail.media_url }}
              </el-link>
              <span v-else>—</span>
            </p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="recordDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Upload, Plus, Close, Folder, VideoCamera, Picture, Document, Promotion, Check, CircleCheckFilled, View, RefreshRight, Finished, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { materialApi } from '@/api/material'
import { accountApi } from '@/api/account'
import MobileArticlePreview from '@/components/MobileArticlePreview.vue'
import { formatDateWithOffset, formatLocalDateTime, toBeijingTime } from '@/utils/dateTime'

// API base URL - 使用统一的工具函数
import { resolveApiBaseUrl } from '@/utils/apiConfig'

const apiBaseUrl = resolveApiBaseUrl()

// Authorization headers
const authHeaders = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
}))

// 当前激活的tab
const activeTab = ref('tab1')

// tab计数器
let tabCounter = 1

// 内容类型相关
const contentTypeDialogVisible = ref(false)
const selectedContentType = ref('video')

// 内容类型配置
const contentTypes = [
  {
    value: 'video',
    label: '视频',
    description: '发布视频内容到各大平台',
    icon: VideoCamera,
    features: ['支持多平台发布', '本地上传/素材库', '定时发布功能']
  },
  {
    value: 'image-text',
    label: '图文',
    description: 'AI生成图文内容',
    icon: Picture,
    features: ['AI内容生成', '多种排版风格', '自动配图']
  },
  {
    value: 'article',
    label: '文章',
    description: '发布长文章内容',
    icon: Document,
    features: ['富文本编辑', 'SEO优化', '多平台同步']
  }
]

// Webhook URL 配置
const ARTICLE_WEBHOOK_URL = 'https://aicode.ltd/webhook/publich-article' // 文章类型webhook URL
const VIDEO_WEBHOOK_URL = 'https://aicode.ltd/webhook/c155e570-faf5-4351-b1bd-7b908cf6db36'
const IMAGE_TEXT_WEBHOOK_URL = 'https://aicode.ltd/webhook/publich-images' // 图文类型webhook URL

/**
 * 根据内容类型解析对应的 webhook 发布地址
 * @param {'video'|'image-text'|'article'} contentType
 * @returns {string}
 */
const getRecordWebhookUrl = (contentType) => {
  if (contentType === 'article') {
    return ARTICLE_WEBHOOK_URL
  }
  if (contentType === 'image-text') {
    return IMAGE_TEXT_WEBHOOK_URL
  }
  return VIDEO_WEBHOOK_URL
}

/**
 * 获取发布状态的标签类型
 * @param {string} status - 发布状态: pending, processing, success, failed
 * @returns {string}
 */
const getPublishStatusTagType = (status) => {
  const statusMap = {
    'pending': 'info',
    'processing': 'warning',
    'success': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

/**
 * 获取发布状态的中文标签
 * @param {string} status - 发布状态
 * @returns {string}
 */
const getPublishStatusLabel = (status) => {
  const labelMap = {
    'pending': '待发布',
    'processing': '进行中',
    'success': '成功',
    'failed': '失败'
  }
  return labelMap[status] || '待发布'
}

/**
 * 更新发布中心记录的状态
 * @param {number} recordId - 记录ID
 * @param {string} status - 状态值: pending, processing, success, failed
 */
const updatePublishStatus = async (recordId, status) => {
  try {
    const response = await fetch(`${apiBaseUrl}/publish/records/${recordId}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 更新本地列表中的状态
      const record = productionRecords.value.find(r => r.id === recordId)
      if (record) {
        record.publish_status = status
      }
    }
  } catch (error) {
    console.error('更新发布状态失败:', error)
  }
}

const publishingRecordId = ref(null)

// 发布平台选择弹窗
const publishPlatformDialogVisible = ref(false)
const currentPublishRecord = ref(null)
const publishPlatformForm = reactive({
  platform: '微信图文'
})

// 获取内容类型标签样式
const getContentTypeTagType = (contentType) => {
  const typeMap = {
    'video': 'warning',
    'image-text': '',
    'article': 'info'
  }
  return typeMap[contentType] || ''
}

// 获取内容类型标签文本
const getContentTypeLabel = (contentType) => {
  const type = contentTypes.find(t => t.value === contentType)
  return type ? type.label : '未知类型'
}

// 获取内容类型图标
const getContentTypeIcon = (contentType) => {
  const type = contentTypes.find(t => t.value === contentType)
  return type ? type.icon : Document
}

// 获取应用状态管理
const appStore = useAppStore()

// 上传相关状态
const uploadOptionsVisible = ref(false)
const localUploadVisible = ref(false)
const materialLibraryVisible = ref(false)
const currentUploadTab = ref(null)
const selectedMaterials = ref([])
const materials = computed(() => appStore.materials)
const materialSourceFilter = ref('生成素材') // 默认筛选生成素材
const filteredMaterials = computed(() => {
  if (!materialSourceFilter.value) {
    return materials.value
  }
  return materials.value.filter(m => m.source === materialSourceFilter.value)
})

// 素材筛选变化处理
const handleMaterialFilterChange = async () => {
  selectedMaterials.value = [] // 清空已选择的素材
  
  // 重新获取筛选后的素材
  try {
    const response = await materialApi.getAllMaterials(materialSourceFilter.value)
    if (response.code === 200) {
      appStore.setMaterials(response.data)
    }
  } catch (error) {
    console.error('获取素材列表出错:', error)
  }
}

// 批量发布相关状态
const batchPublishing = ref(false)
const batchPublishMessage = ref('')
const batchPublishType = ref('info')

// 平台列表 - 对应后端type字段
const platforms = [
  { key: 3, name: '抖音' },
  { key: 4, name: '快手' },
  { key: 2, name: '视频号' },
  { key: 1, name: '小红书' }
]

const defaultTabInit = {
  name: 'tab1',
  label: '发布1',
  contentType: 'article', // 内容类型：video, image-text, article
  fileList: [], // 后端返回的文件名列表
  displayFileList: [], // 用于显示的文件列表
  selectedAccounts: [], // 选中的账号ID列表
  selectedPlatform: 1, // 选中的平台（单选）
  title: '',
  productLink: '', // 商品链接
  productTitle: '', // 商品名称
  selectedTopics: [], // 话题列表（不带#号）
  scheduleEnabled: false, // 定时发布开关
  videosPerDay: 1, // 每天发布视频数量
  dailyTimes: ['10:00'], // 每天发布时间点列表
  startDays: 0, // 从今天开始计算的发布天数，0表示明天，1表示后天
  publishStatus: null, // 发布状态，包含message和type
  publishing: false, // 发布状态，用于控制按钮loading效果
  isDraft: false, // 是否保存为草稿，仅视频号平台可见
  // 图文类型配置
  imageText: {
    contentSourceType: 'other', // 内容来源类型
    inputContent: '', // 输入内容
    contentWordCount: 1000, // 图文内容字数
    contentLayoutStyle: 'xiaohongshu-hot', // 内容排版风格
    contentLayoutReference: '', // 内容排版参考链接
    imageCount: 3, // 配图张数
    imageStyleType: 'builtin-ai-no', // 配图风格类型
    imageStyleReference: '', // 配图风格参考链接
    externalArticleLink: '', // 外部文章链接
    externalArticleSource: 'juejin', // 外部文章来源
    coverStyleType: 'ai-auto', // 封面图风格类型
    coverStyleReference: '', // 封面图风格参考链接
    infoGraphicType: 'minimalist-tech', // 信息图类型
    imageModel: 'sora', // 生图模型
    publishPlatform: 'xiaohongshu' // 发布平台
  },
  // 文章类型配置
  article: {
    writingMode: 'polish', // 写作模式：polish(润色), imitate(仿写), original(原创), reprint(搬运排版)
    sourcePlatform: 'wechat', // 文章来源平台：zhihu, juejin, wechat, medium, other
    articleLink: '', // 对标文章链接
    publishPlatform: 'wechat', // 文章发布平台：zhihu, juejin, wechat, medium, other
    layoutStyle: 'rose-purple', // 排版风格
    autoPublish: 'yes', // 是否进行自动化发布：yes, no
    imitateTopic: '', // 仿写主题内容
    imitateLength: '', // 仿写文章长短
    originalKeywords: '', // 原创深度研究领域关键词
    originalLevel: 'beginner', // 原创当前层次：novice, beginner, junior, senior, expert
    originalPurpose: 'knowledge', // 原创学习目的：concept, problem, practice, skill, career, knowledge, teaching, innovation
    originalNeedImage: 'no', // 原创是否需要配图：yes, no
    originalAutomation: 'step', // 原创是否自动化：auto, step
    originalDepth: 3, // 原创研究主题探究深度：1, 2, 3, 5, 10, 20
    originalWordCount: 3000, // 原创报告期望字数：1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 10000
    originalLanguage: 'zh-cn', // 原创报告期望语言：zh-cn, zh-tw, en
    originalPromptCount: 500, // 原创提示词字数：100, 200, 300, 400, 500, 600, 700, 800, 1000
    wechatAccount: 'all' // 微信发布账号配置：react, biscuit, all
  }
}

// helper to create a fresh deep-copied tab from defaultTabInit
const makeNewTab = () => {
  // prefer structuredClone when available (newer browsers/node), fallback to JSON
  try {
    return typeof structuredClone === 'function' ? structuredClone(defaultTabInit) : JSON.parse(JSON.stringify(defaultTabInit))
  } catch (e) {
    return JSON.parse(JSON.stringify(defaultTabInit))
  }
}

// tab页数据 - 默认只有一个tab (use deep copy to avoid shared refs)
const tabs = reactive([
  makeNewTab()
])

// 制作中心记录列表
const productionRecords = ref([])

// 内容类型Tab切换
const activeContentTypeTab = ref('image-text')

// 按内容类型过滤的记录
const filteredPublishRecords = computed(() => {
  if (activeContentTypeTab.value === 'all') {
    return productionRecords.value
  }
  return productionRecords.value.filter(record => record.content_type === activeContentTypeTab.value)
})
const productionListLoading = ref(false)
const recordDetailVisible = ref(false)
const currentRecordDetail = ref(null)
const recordsTableRef = ref(null)
const selectedRecords = ref([])
const listBatchPublishing = ref(false)

// 确保所有 tab 的通用排版风格默认使用蔷薇紫
tabs.forEach(tab => {
  if (tab.article && !tab.article.layoutStyle) {
    tab.article.layoutStyle = 'rose-purple'
  }
})

// 文章发布 payload 格式化相关
const ARTICLE_FORM_MODE = import.meta.env.VITE_FORM_MODE || 'test'

const formatArticlePayload = (tab) => {
  const article = tab.article || {}
  if (!article.layoutStyle) {
    article.layoutStyle = 'rose-purple'
  }
  if (!article.autoPublish) {
    article.autoPublish = 'yes'
  }
  return {
    '写作模式': mapWritingMode(article.writingMode),
    '润色&仿写&搬运排版-文章来源平台': mapSourcePlatform(article.sourcePlatform),
    '润色&仿写&搬运排版-链接': article.articleLink || '',
    '润色&仿写&搬运排版-文章发布平台': mapPublishPlatform(article.publishPlatform),
    '通用-排版风格': mapLayoutStyle(article.layoutStyle),
    '是否进行自动化发布': mapYesNo(article.autoPublish),
    '仿写-主题内容': article.imitateTopic || '',
    '仿写-文章长短': mapImitateLength(article.imitateLength),
    '原创-深度研究领域关键词': article.originalKeywords || '',
    '原创-当前层次': mapOriginalLevel(article.originalLevel),
    '原创-学习目的': mapOriginalPurpose(article.originalPurpose),
    '原创-文章是否需要配图': mapYesNo(article.originalNeedImage),
    '原创-是否自动化': mapAutomation(article.originalAutomation),
    '原创-研究主题探究的深度': safeString(article.originalDepth),
    '原创-报告期望字数': safeString(article.originalWordCount),
    '原创-报告期望语言': mapOriginalLanguage(article.originalLanguage),
    '原创-提示词字数': safeString(article.originalPromptCount),
    '润色&仿写&搬运排版-微信发布账号配置': mapWechatAccount(article.wechatAccount),
    'submittedAt': formatDateWithOffset(),
    'formMode': ARTICLE_FORM_MODE
  }
}

const mapWritingMode = (value) => ({
  polish: '润色',
  imitate: '仿写',
  original: '原创',
  reprint: '搬运排版'
})[value] || value || ''

const mapSourcePlatform = (value) => ({
  zhihu: '知乎',
  juejin: '掘金',
  wechat: '公众号',
  medium: 'Medium',
  other: '其他'
})[value] || value || ''

const mapPublishPlatform = (value) => ({
  zhihu: '知乎',
  juejin: '掘金',
  wechat: '公众号',
  medium: 'Medium',
  other: '其他'
})[value] || value || ''

const mapLayoutStyle = (value) => ({
  'orange-heart': '橙心',
  'yanqi-lake': '雁栖湖',
  'fullstack-blue': '全栈蓝',
  'chazi': '姹紫',
  'dynamic-blue': '灵动蓝',
  'geek-black': '极客黑',
  'rose-purple': '蔷薇紫'
})[value] || (value ? value : '蔷薇紫')

const mapImitateLength = (value) => ({
  short: '短篇',
  medium: '中等',
  long: '长篇'
})[value] || value || ''

const mapOriginalLevel = (value) => ({
  novice: '小白 (完全陌生)',
  beginner: '入门 (理论储备)',
  junior: '初级实操者 (有限经验)',
  senior: '资深应用者 (丰富经验)',
  expert: '领域权威（专家级）'
})[value] || value || ''

const mapOriginalPurpose = (value) => ({
  concept: '概念理解',
  problem: '问题解决',
  practice: '应用实践',
  skill: '技能掌握',
  career: '职业发展',
  knowledge: '知识建构',
  teaching: '教学与分享',
  innovation: '创新与研究'
})[value] || value || ''

const mapYesNo = (value) => value === 'yes' ? '是' : value === 'no' ? '否' : (value || '')

const mapAutomation = (value) => ({
  auto: '自动化',
  step: '分步骤'
})[value] || value || ''

const mapOriginalLanguage = (value) => ({
  'zh-cn': '中文简体',
  'zh-tw': '中文繁体',
  en: '英语'
})[value] || value || ''

const mapWechatAccount = (value) => ({
  react: 'React中文社区',
  biscuit: '程序员饼干',
  all: '全部'
})[value] || value || ''

const safeString = (value) => {
  if (value === undefined || value === null) return ''
  return String(value)
}

const formatContentPreview = (content, length = 120) => {
  const text = safeString(content).trim()
  if (!text) return '—'
  return text.length > length ? `${text.slice(0, length)}...` : text
}

// 使用统一的时间工具函数（已从 @/utils/dateTime 导入）

// 账号相关状态
const accountDialogVisible = ref(false)
const tempSelectedAccounts = ref([])
const currentTab = ref(null)
const isLoadingAccounts = ref(false)

// 获取账号状态管理
const accountStore = useAccountStore()

// 根据选择的平台获取可用账号列表
const availableAccounts = computed(() => {
  const platformMap = {
    3: '抖音',
    2: '视频号',
    1: '小红书',
    4: '快手'
  }
  const currentPlatform = currentTab.value ? platformMap[currentTab.value.selectedPlatform] : null
  return currentPlatform ? accountStore.accounts.filter(acc => acc.platform === currentPlatform) : []
})

// 加载账号数据
const loadAccounts = async () => {
  if (isLoadingAccounts.value || accountStore.accounts.length > 0) {
    return
  }
  isLoadingAccounts.value = true
  try {
    const res = await accountApi.getValidAccounts()
    if (res.code === 200 && res.data) {
      accountStore.setAccounts(res.data)
    } else {
      console.error('获取账号数据失败:', res)
      ElMessage.error('获取账号数据失败，请稍后重试')
    }

  } catch (error) {
    console.error('获取账号数据失败:', error)
    ElMessage.error('获取账号数据失败，请稍后重试')
  } finally {
    isLoadingAccounts.value = false
  }
}

const fetchProductionRecords = async (contentType = '') => {
  const normalized = (contentType || '').toLowerCase()
  const query = normalized && normalized !== 'all' ? `?content_type=${normalized}` : ''
  productionListLoading.value = true
  try {
    // 从发布中心记录表获取数据（发布成功的记录）
    const response = await fetch(`${apiBaseUrl}/publish/records${query}`)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    const result = await response.json()
    if (result.code !== 200) {
      throw new Error(result.msg || '获取发布记录失败')
    }
    productionRecords.value = result.data || []
    clearRecordSelection()
  } catch (error) {
    console.error('获取发布记录失败:', error)
    ElMessage.error(error.message || '获取发布记录失败')
    // 如果获取失败，设置为空数组
    productionRecords.value = []
  } finally {
    productionListLoading.value = false
  }
}

const refreshProductionRecords = () => {
  if (productionListLoading.value) return
  fetchProductionRecords()
}

/**
 * 检查并更新记录的状态（静默刷新，只更新状态字段）
 */
const checkAndUpdateRecordStatuses = async () => {
  if (productionListLoading.value || productionRecords.value.length === 0) {
    return
  }
  
  try {
    // 从发布中心记录表获取数据
    const response = await fetch(`${apiBaseUrl}/publish/records`)
    if (!response.ok) {
      return
    }
    const result = await response.json()
    if (result.code !== 200) {
      return
    }
    
    const serverRecords = result.data || []
    const serverStatusMap = new Map()
    serverRecords.forEach(record => {
      serverStatusMap.set(record.id, record.publish_status)
    })
    
    // 更新本地记录的状态（如果有变化）
    productionRecords.value.forEach(localRecord => {
      const serverStatus = serverStatusMap.get(localRecord.id)
      if (serverStatus && serverStatus !== localRecord.publish_status) {
        localRecord.publish_status = serverStatus
        console.log(`🔄 记录 ${localRecord.id} 状态已更新: ${localRecord.publish_status} -> ${serverStatus}`)
      }
    })
  } catch (error) {
    // 静默失败，不显示错误提示
    console.debug('检查状态更新失败:', error)
  }
}

// 状态轮询相关
let statusPollingInterval = null
const STATUS_POLLING_INTERVAL = 5000 // 每5秒检查一次

/**
 * 启动状态轮询
 */
const startStatusPolling = () => {
  if (statusPollingInterval) {
    return
  }
  statusPollingInterval = setInterval(() => {
    // 只在页面可见时轮询
    if (!document.hidden) {
      checkAndUpdateRecordStatuses()
    }
  }, STATUS_POLLING_INTERVAL)
  console.log('✅ 状态轮询已启动')
}

/**
 * 停止状态轮询
 */
const stopStatusPolling = () => {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval)
    statusPollingInterval = null
    console.log('⏹️ 状态轮询已停止')
  }
}

const clearRecordSelection = () => {
  if (recordsTableRef.value) {
    recordsTableRef.value.clearSelection()
  }
  selectedRecords.value = []
}

const handleRecordSelectionChange = (selection) => {
  selectedRecords.value = selection
}

const toggleSelectAllRecords = () => {
  if (!recordsTableRef.value || productionRecords.value.length === 0) return
  const shouldClear = selectedRecords.value.length === productionRecords.value.length
  recordsTableRef.value.clearSelection()
  if (!shouldClear) {
    productionRecords.value.forEach(record => {
      recordsTableRef.value.toggleRowSelection(record, true)
    })
  }
}

const deleteProductionRecord = async (record) => {
  if (!record?.id) return
  try {
    await ElMessageBox.confirm(`确认删除【${record.title || '未命名内容'}】吗？`, '删除制作记录', {
      type: 'warning'
    })
  } catch {
    return
  }
  try {
    const response = await fetch(`${apiBaseUrl}/production/records/${record.id}`, {
      method: 'DELETE'
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const result = await response.json()
    if (result.code !== 200) throw new Error(result.msg || '删除失败')
    productionRecords.value = productionRecords.value.filter(item => item.id !== record.id)
    selectedRecords.value = selectedRecords.value.filter(item => item.id !== record.id)
    ElMessage.success('制作记录已删除')
  } catch (error) {
    console.error('删除制作记录失败:', error)
    ElMessage.error(error.message || '删除失败，请稍后重试')
  }
}

const deleteSelectedRecords = async () => {
  if (!selectedRecords.value.length) {
    ElMessage.warning('请先选择需要删除的记录')
    return
  }
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRecords.value.length} 条记录吗？`, '批量删除', {
      type: 'warning'
    })
  } catch {
    return
  }
  const ids = selectedRecords.value.map(item => item.id)
  try {
    const response = await fetch(`${apiBaseUrl}/production/records`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids })
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const result = await response.json()
    if (result.code !== 200) throw new Error(result.msg || '删除失败')
    const idsToDelete = new Set(ids)
    productionRecords.value = productionRecords.value.filter(record => !idsToDelete.has(record.id))
    ElMessage.success('批量删除成功')
  } catch (error) {
    console.error('批量删除失败:', error)
    ElMessage.error(error.message || '删除失败，请稍后重试')
  } finally {
    clearRecordSelection()
  }
}

const batchPublishSelectedRecords = async () => {
  if (!selectedRecords.value.length) {
    ElMessage.warning('请先选择需要发布的记录')
    return
  }
  listBatchPublishing.value = true
  try {
    for (const record of selectedRecords.value) {
      await publishRecord(record)
    }
  } finally {
    listBatchPublishing.value = false
  }
}

const openRecordDetail = (record) => {
  currentRecordDetail.value = record
  recordDetailVisible.value = true
}

const createTabByType = (type) => {
  tabCounter++
  const newTab = makeNewTab()
  if (newTab.article && !newTab.article.layoutStyle) {
    newTab.article.layoutStyle = 'rose-purple'
  }
  newTab.name = `tab${tabCounter}`
  newTab.label = `发布${tabCounter}`
  newTab.contentType = type
  tabs.push(newTab)
  activeTab.value = newTab.name
  return newTab
}

const publishRecord = async (record) => {
  if (!record) {
    ElMessage.error('未找到要发布的记录')
    return
  }
  if (publishingRecordId.value && publishingRecordId.value === record.id) {
    ElMessage.warning('当前记录正在发布中')
    return
  }

  // 视频和图文类型显示平台选择弹窗，文章类型直接调用接口
  if (record.content_type === 'image-text' || record.content_type === 'video') {
    // 保存当前要发布的记录，显示平台选择弹窗
    currentPublishRecord.value = record
    // 根据内容类型设置默认平台
    if (record.content_type === 'video') {
      publishPlatformForm.platform = '视频号' // 视频类型默认选择视频号
    } else {
      publishPlatformForm.platform = '微信图文' // 图文类型默认选择微信图文
    }
    publishPlatformDialogVisible.value = true
    return
  }

  // 文章类型直接调用接口（原有逻辑）
  publishingRecordId.value = record.id
  
  // 更新状态为"进行中"（状态更新由用户自己调用接口控制）
  await updatePublishStatus(record.id, 'processing')
  
  const targetWebhookUrl = getRecordWebhookUrl(record.content_type)
  if (!targetWebhookUrl) {
    ElMessage.error('未配置对应的发布链接')
    publishingRecordId.value = null
    return
  }
  
  try {
    // 构建请求体
    let requestBody = { ...record }
    
    console.log('📤 发送发布请求:', {
      url: targetWebhookUrl,
      contentType: record.content_type,
      recordId: record.id
    })
    console.log('📋 请求体:', JSON.stringify(requestBody, null, 2))
    
    const response = await fetch(targetWebhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })

    // 尝试读取响应体中的错误信息
    let errorMessage = null
    let result = null
    
    try {
      const responseText = await response.text()
      if (responseText) {
        try {
          result = JSON.parse(responseText)
          // 如果响应包含错误信息，提取它
          if (result.msg || result.message || result.error) {
            errorMessage = result.msg || result.message || result.error
          }
        } catch (e) {
          // 如果不是JSON格式，使用原始文本
          errorMessage = responseText
        }
      }
    } catch (err) {
      console.error('读取响应失败:', err)
    }

    if (!response.ok) {
      // 如果有错误信息，使用它；否则使用HTTP状态码
      const finalErrorMessage = errorMessage || `HTTP ${response.status}: ${response.statusText}`
      console.error('❌ 发布失败:', {
        status: response.status,
        statusText: response.statusText,
        errorMessage: finalErrorMessage,
        contentType: record.content_type
      })
      throw new Error(finalErrorMessage)
    }

    // 不自动更新状态，状态由用户自己调用接口更新
    const successMsg = result?.message || result?.msg || '发布任务已发送'
    ElMessage.success(successMsg)
    console.log('✅ 发布成功:', result)
  } catch (error) {
    console.error('❌ 发布接口调用失败:', error)
    // 不自动更新状态，状态由用户自己调用接口更新
    const errorMsg = error.message || '发布失败，请稍后重试'
    ElMessage.error({
      message: `发布失败: ${errorMsg}`,
      duration: 5000,
      showClose: true
    })
  } finally {
    publishingRecordId.value = null
  }
}

// 确认发布（带平台选择）
const confirmPublishWithPlatform = async () => {
  if (!publishPlatformForm.platform) {
    ElMessage.warning('请选择发布平台')
    return
  }

  const record = currentPublishRecord.value
  if (!record) {
    ElMessage.error('未找到要发布的记录')
    publishPlatformDialogVisible.value = false
    return
  }

  // 关闭弹窗
  publishPlatformDialogVisible.value = false

  publishingRecordId.value = record.id
  
  // 更新状态为"进行中"（状态更新由用户自己调用接口控制）
  await updatePublishStatus(record.id, 'processing')
  
  const targetWebhookUrl = getRecordWebhookUrl(record.content_type)
  if (!targetWebhookUrl) {
    ElMessage.error('未配置对应的发布链接')
    publishingRecordId.value = null
    return
  }
  
  try {
    // 构建请求体，确保图文类型包含 record_id，并添加 platform 字段
    let requestBody = { ...record }
    if (record.content_type === 'image-text') {
      // 图文类型明确添加 record_id 字段
      requestBody.record_id = record.id
      
      // 处理 media_ids -> urls 转换（与保存接口保持一致）
      let urlsArray = []
      
      console.log('🔍 [图文发布] 开始处理 media_ids:', {
        media_ids: record.media_ids,
        media_ids_type: typeof record.media_ids,
        is_array: Array.isArray(record.media_ids),
        url: record.url,
        media_url: record.media_url
      })
      
      // 优先从 media_ids 字段获取 URLs
      if (record.media_ids !== null && record.media_ids !== undefined) {
        if (Array.isArray(record.media_ids)) {
          // 如果已经是数组，直接使用
          urlsArray = record.media_ids.filter(url => url && typeof url === 'string' && url.trim())
          console.log('✅ [图文发布] media_ids 是数组，提取到', urlsArray.length, '个URL:', urlsArray)
        } else if (typeof record.media_ids === 'string') {
          // 如果是JSON字符串，尝试解析
          try {
            const parsed = JSON.parse(record.media_ids)
            if (Array.isArray(parsed)) {
              urlsArray = parsed.filter(url => url && typeof url === 'string' && url.trim())
              console.log('✅ [图文发布] 解析JSON字符串成功，提取到', urlsArray.length, '个URL:', urlsArray)
            } else if (typeof parsed === 'string' && parsed.trim()) {
              // 如果解析后是单个字符串，转换为数组
              urlsArray = [parsed.trim()]
              console.log('⚠️ [图文发布] 解析后是单个字符串，转换为数组:', urlsArray)
            }
          } catch (e) {
            // 解析失败，检查是否是单个URL字符串
            const trimmed = record.media_ids.trim()
            if (trimmed) {
              urlsArray = [trimmed]
              console.log('⚠️ [图文发布] JSON解析失败，当作单个URL处理:', urlsArray)
            }
          }
        } else {
          console.warn('⚠️ [图文发布] media_ids 类型未知:', typeof record.media_ids, record.media_ids)
        }
      } else {
        console.warn('⚠️ [图文发布] media_ids 为空或未定义')
      }
      
      // 如果 media_ids 没有提供或为空，尝试从其他字段获取（仅作为备用）
      if (urlsArray.length === 0) {
        console.log('⚠️ [图文发布] media_ids 为空，尝试从其他字段获取')
        // 尝试从 url 字段获取
        if (record.url && typeof record.url === 'string' && record.url.trim()) {
          urlsArray = [record.url.trim()]
          console.log('✅ [图文发布] 从 url 字段获取到URL:', urlsArray)
        }
        // 尝试从 media_url 字段获取（兼容旧数据）
        else if (record.media_url && typeof record.media_url === 'string' && record.media_url.trim()) {
          urlsArray = [record.media_url.trim()]
          console.log('✅ [图文发布] 从 media_url 字段获取到URL:', urlsArray)
        }
      }
      
      // 将 media_ids 转换为 urls 数组（与保存接口保持一致）
      // 重要：无论 urlsArray 是否为空，都要设置 urls 字段，确保数据格式一致
      requestBody.urls = urlsArray
      // 删除 media_ids 字段，使用 urls 替代
      delete requestBody.media_ids
      
      if (urlsArray.length === 0) {
        // 如果没有找到任何URL，记录警告
        console.warn('⚠️ [图文发布] 警告：没有找到任何URL，urls 数组为空:', record)
      } else {
        console.log('✅ [图文发布] 最终 urls 数组包含', urlsArray.length, '个URL:', urlsArray)
      }
      
      // 添加 URL 字段作为 POST 参数传给 n8n（用于单图场景的兼容）
      // 优先使用 record.url（从数据库保存的url字段），如果没有则使用 urls 数组的第一个
      let urlValue = null
      if (record.url && typeof record.url === 'string' && record.url.trim()) {
        // 优先使用数据库中保存的 url 字段
        urlValue = record.url.trim()
      } else if (record.media_url && typeof record.media_url === 'string' && record.media_url.trim()) {
        // 兼容旧数据，使用 media_url
        urlValue = record.media_url.trim()
      } else if (requestBody.urls && Array.isArray(requestBody.urls) && requestBody.urls.length > 0) {
        // 如果 urls 数组存在，取第一个作为 url（兼容单图场景）
        urlValue = requestBody.urls[0]
      }
      
      // 如果找到了URL，添加到请求体中（用于兼容）
      if (urlValue) {
        requestBody.url = urlValue
      }
    }
    // 添加 platform 字段
    requestBody.platform = publishPlatformForm.platform
    
    console.log('📤 发送发布请求:', {
      url: targetWebhookUrl,
      platform: publishPlatformForm.platform,
      contentType: record.content_type,
      recordId: record.id,
      recordUrl: record.url,  // 数据库中的 url 字段
      mediaUrl: record.media_url,  // 兼容字段
      mediaIds: record.media_ids,
      mediaIdsType: typeof record.media_ids,  // media_ids 的类型
      mediaIdsIsArray: Array.isArray(record.media_ids),  // 是否是数组
      urlsArray: requestBody.urls,  // 转换后的 urls 数组
      urlsArrayLength: requestBody.urls ? requestBody.urls.length : 0,  // urls 数组长度
      finalUrlParam: requestBody.url  // 最终使用的 url 参数（兼容字段）
    })
    console.log('📋 请求体:', JSON.stringify(requestBody, null, 2))
    
    // 验证 urls 数组是否正确
    if (record.content_type === 'image-text') {
      if (requestBody.urls && Array.isArray(requestBody.urls)) {
        console.log(`✅ 图文类型：urls 数组包含 ${requestBody.urls.length} 个URL:`, requestBody.urls)
      } else {
        console.warn('⚠️ 图文类型：urls 数组不存在或不是数组:', requestBody.urls)
      }
    }
    
    const response = await fetch(targetWebhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })

    // 尝试读取响应体中的错误信息
    let errorMessage = null
    let result = null
    
    try {
      const responseText = await response.text()
      if (responseText) {
        try {
          result = JSON.parse(responseText)
          // 如果响应包含错误信息，提取它
          if (result.msg || result.message || result.error) {
            errorMessage = result.msg || result.message || result.error
          }
        } catch (e) {
          // 如果不是JSON格式，使用原始文本
          errorMessage = responseText
        }
      }
    } catch (err) {
      console.error('读取响应失败:', err)
    }

    if (!response.ok) {
      // 如果有错误信息，使用它；否则使用HTTP状态码
      const finalErrorMessage = errorMessage || `HTTP ${response.status}: ${response.statusText}`
      console.error('❌ 发布失败:', {
        status: response.status,
        statusText: response.statusText,
        errorMessage: finalErrorMessage,
        platform: publishPlatformForm.platform
      })
      throw new Error(finalErrorMessage)
    }

    // 不自动更新状态，状态由用户自己调用接口更新
    const successMsg = result?.message || result?.msg || '发布任务已发送'
    ElMessage.success(successMsg)
    console.log('✅ 发布成功:', result)
  } catch (error) {
    console.error('❌ 发布接口调用失败:', error)
    // 不自动更新状态，状态由用户自己调用接口更新
    const errorMsg = error.message || '发布失败，请稍后重试'
    ElMessage.error({
      message: `发布失败: ${errorMsg}`,
      duration: 5000,
      showClose: true
    })
  } finally {
    publishingRecordId.value = null
    currentPublishRecord.value = null
  }
}

// 页面可见性变化处理函数
let handleVisibilityChange = null

onMounted(() => {
  loadAccounts()
  fetchProductionRecords()
  // 启动状态轮询
  startStatusPolling()
  
  // 监听页面可见性变化
  handleVisibilityChange = () => {
    if (document.hidden) {
      stopStatusPolling()
    } else {
      startStatusPolling()
      // 页面重新可见时立即检查一次
      checkAndUpdateRecordStatuses()
    }
  }
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  stopStatusPolling()
  if (handleVisibilityChange) {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
  }
})

// 话题相关状态
const topicDialogVisible = ref(false)
const customTopic = ref('')

// 推荐话题列表
const recommendedTopics = [
  '游戏', '电影', '音乐', '美食', '旅行', '文化',
  '科技', '生活', '娱乐', '体育', '教育', '艺术',
  '健康', '时尚', '美妆', '摄影', '宠物', '汽车'
]

// 添加新tab - 先显示类型选择 Modal
const addTab = () => {
  console.log('🔔 点击了添加Tab按钮')
  selectedContentType.value = 'video' // 默认选择视频
  contentTypeDialogVisible.value = true
  console.log('📋 Modal 应该显示了，状态:', contentTypeDialogVisible.value)
}

// 确认内容类型并创建 tab
const confirmContentType = () => {
  if (!selectedContentType.value) {
    ElMessage.warning('请选择发布类型')
    return
  }
  
  const newTab = createTabByType(selectedContentType.value)
  contentTypeDialogVisible.value = false
  ElMessage.success(`已添加${getContentTypeLabel(newTab.contentType)}类型的发布Tab`)
}

/**
 * 选项值到中文标签的映射
 */
const valueToLabelMap = {
  // 内容来源类型
  'xiaohongshu': '小红书链接',
  'other': '其他链接',
  'custom': '自定义内容',
  
  // 内容排版风格
  'xiaohongshu-hot': '小红书爆款风格',
  'builtin-common': '内置排版风格-通用风格',
  'builtin-female': '内置排版风格-女性成长',
  'builtin-food': '内置排版风格-美食探店',
  'builtin-baby': '内置排版风格-母婴',
  'builtin-recommend': '内置排版风格-好物推荐',
  'builtin-home': '内置排版风格-家居',
  'builtin-outdoor': '内置排版风格-户外出行',
  'builtin-beauty': '内置排版风格-美妆穿搭',
  'builtin-business': '内置排版风格-创业创业',
  'builtin-skill': '内置排版风格-知识技能',
  
  // 配图风格类型
  'ai-auto': 'AI智能生成-风格根据文案生成',
  'builtin-notebook': '内置配图风格-记事本风格',
  'xhs-bigtext': '小红书爆款配图风格-大字报内容',
  'xhs-keyword': '小红书爆款配图风格-关键字替换',
  'builtin-ai-yes': '内置图片ai处理',
  'builtin-ai-no': '内置图片ai不处理',
  'external-ai-yes': '外置图片ai处理',
  'external-ai-no': '外置图片ai不处理',
  'info-graphic': '信息图',
  'article-image': '文章内置图片',
  
  // 生图模型
  'qianwen': '千问',
  'jimeng': '即梦',
  'sora': 'Sora',
  'nabana': 'nabana',
  
  // 发布平台
  'xiaohongshu': '小红书图文',
  'wechat': '微信图文',
  'bilibili': 'B站图文',
  
  // 文章来源
  'juejin': '掘金',
  'wechat': '公众号',
  'zhihu': '知乎',
  
  // 信息图类型
  'minimalist-tech': '极简技术风'
}

/**
 * 将英文value转换为中文标签
 */
const getChineseLabel = (value) => {
  if (!value) return ""
  return valueToLabelMap[value] || value
}

/**
 * 将图文数据转换为中文key格式
 */
const convertImageTextToChineseKeys = (imageTextData) => {
  return {
    "内容来源类型": getChineseLabel(imageTextData.contentSourceType),
    "输入内容": imageTextData.inputContent || "",
    "内容排版风格": getChineseLabel(imageTextData.contentLayoutStyle),
    "内容排版类型-小红书爆款风格": imageTextData.contentLayoutReference || "",
    "配图风格类型选择": getChineseLabel(imageTextData.imageStyleType),
    "配图风格选择-小红书爆款参考链接": imageTextData.imageStyleReference || "",
    "封面图风格类型选择": getChineseLabel(imageTextData.coverStyleType),
    "封面图风格选择-小红书爆款风格": imageTextData.coverStyleReference || "",
    "配图张数": imageTextData.imageCount ? String(imageTextData.imageCount) : "",
    "生图模型": getChineseLabel(imageTextData.imageModel),
    "发布平台": getChineseLabel(imageTextData.publishPlatform),
    "图文内容字数": imageTextData.contentWordCount ? String(imageTextData.contentWordCount) : "",
    "封面图-信息图类型": getChineseLabel(imageTextData.infoGraphicType),
    "配图风格类型选择-文章外图片-文章链接": imageTextData.externalArticleLink || "",
    "配图风格类型选择-文章外图片-文章来源": getChineseLabel(imageTextData.externalArticleSource),
    "submittedAt": formatDateWithOffset(),
    "formMode": "production"
  }
}

/**
 * 确认生成图文内容
 */
const confirmPublishImageText = async (tab) => {
  // 表单验证
  if (!tab.imageText.inputContent) {
    ElMessage.warning('请输入内容')
    return
  }
  
  if (!tab.imageText.contentWordCount) {
    ElMessage.warning('请选择图文内容字数')
    return
  }
  
  if (!tab.imageText.contentLayoutStyle) {
    ElMessage.warning('请选择内容排版风格')
    return
  }
  
  if (!tab.imageText.imageModel) {
    ElMessage.warning('请选择生图模型')
    return
  }
  
  if (!tab.imageText.publishPlatform) {
    ElMessage.warning('请选择发布平台')
    return
  }
  
  // 设置发布状态
  tab.publishing = true
  tab.publishStatus = null
  
  // 显示处理中的提示
  const loadingMessage = ElMessage({
    message: '🤖 AI正在生成图文内容，预计需要30-60秒，请耐心等待...',
    type: 'info',
    duration: 0,  // 不自动关闭
    showClose: true
  })
  
  try {
    // 转换为中文key格式
    const chineseData = convertImageTextToChineseKeys(tab.imageText)
    
    console.log('📤 发送图文生成请求 (中文格式):', chineseData)
    console.log('📋 JSON格式:', JSON.stringify(chineseData, null, 2))
    
    // 直接调用图文类型的webhook接口
    const startTime = Date.now()
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      controller.abort()
    }, 10 * 60 * 1000)

    let response
    try {
      response = await fetch(IMAGE_TEXT_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chineseData),
        signal: controller.signal
      })
    } finally {
      clearTimeout(timeoutId)
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(1)
    console.log(`⏱️ 请求耗时: ${elapsedTime}秒`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const apiResponse = await response.json()
    
    // 检查业务状态码
    if (apiResponse.code !== 200) {
      throw new Error(apiResponse.msg || '请求失败')
    }
    
    const result = apiResponse.data || {}
    
    // 关闭加载提示
    loadingMessage.close()
    
    // 成功提示
    tab.publishStatus = {
      message: `图文内容生成成功！(耗时 ${elapsedTime}秒)`,
      type: 'success'
    }
    ElMessage.success({
      message: `✅ 图文内容生成成功！(耗时 ${elapsedTime}秒)`,
      duration: 5000
    })
    
    console.log('✅ 图文生成成功，响应:', result)
    console.log('📊 完整数据:', JSON.stringify(result, null, 2))
    
  } catch (error) {
    console.error('❌ 图文生成失败:', error)
    
    // 关闭加载提示
    loadingMessage.close()
    
    tab.publishStatus = {
      message: error.message || '生成失败，请重试',
      type: 'error'
    }
    ElMessage.error({
      message: `❌ ${error.message || '生成失败，请重试'}`,
      duration: 5000
    })
  } finally {
    tab.publishing = false
  }
}

/**
 * 确认生成文章内容
 */
const confirmPublishArticle = async (tab) => {
  // 表单验证
  if (!tab.article.writingMode) {
    ElMessage.warning('请选择写作模式')
    return
  }
  
  // 根据写作模式进行不同的验证
  if (['polish', 'imitate', 'reprint'].includes(tab.article.writingMode)) {
    if (!tab.article.articleLink) {
      ElMessage.warning('请输入对标文章链接')
      return
    }
  }
  
  if (tab.article.writingMode === 'imitate') {
    if (!tab.article.imitateTopic) {
      ElMessage.warning('请输入仿写主题内容')
      return
    }
  }
  
  if (tab.article.writingMode === 'original') {
    if (!tab.article.originalKeywords) {
      ElMessage.warning('请输入深度研究领域关键词')
      return
    }
  }
  
  // 设置发布状态
  tab.publishing = true
  tab.publishStatus = null
  
  // 显示处理中的提示
  const loadingMessage = ElMessage({
    message: '📤 正在发送文章发布请求，请稍候...',
    type: 'info',
    duration: 0,  // 不自动关闭
    showClose: true
  })
  
  try {
    // 构造文章数据
    const articleData = formatArticlePayload(tab)
    
    console.log('📤 发送文章发布请求:', articleData)
    console.log('📋 JSON格式:', JSON.stringify(articleData, null, 2))
    
    // 调用指定的webhook接口
    const startTime = Date.now()
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      controller.abort()
    }, 10 * 60 * 1000)

    let response
    try {
      response = await fetch(ARTICLE_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(articleData),
        signal: controller.signal
      })
    } finally {
      clearTimeout(timeoutId)
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(1)
    console.log(`⏱️ 请求耗时: ${elapsedTime}秒`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const result = await response.json()
    
    // 关闭加载提示
    loadingMessage.close()
    
    // 成功提示
    tab.publishStatus = {
      message: `文章发布成功！(耗时 ${elapsedTime}秒)`,
      type: 'success'
    }
    ElMessage.success({
      message: `✅ 文章发布成功！(耗时 ${elapsedTime}秒)`,
      duration: 5000
    })
    
    console.log('✅ 文章发布成功，响应:', result)
    console.log('📊 完整数据:', JSON.stringify(result, null, 2))
    
  } catch (error) {
    console.error('❌ 文章生成失败:', error)
    
    // 关闭加载提示
    loadingMessage.close()
    
    tab.publishStatus = {
      message: error.message || '生成失败，请重试',
      type: 'error'
    }
    ElMessage.error({
      message: `❌ ${error.message || '生成失败，请重试'}`,
      duration: 5000
    })
  } finally {
    tab.publishing = false
  }
}

// 删除tab
const removeTab = (tabName) => {
  const index = tabs.findIndex(tab => tab.name === tabName)
  if (index > -1) {
    tabs.splice(index, 1)
    // 如果删除的是当前激活的tab，切换到第一个tab
    if (activeTab.value === tabName && tabs.length > 0) {
      activeTab.value = tabs[0].name
    }
  }
}

// 处理文件上传成功
const handleUploadSuccess = (response, file, tab) => {
  if (response.code === 200) {
    // 获取文件路径
    const filePath = response.data.path || response.data
    // 从路径中提取文件名
    const filename = filePath.split('/').pop()
    
    // 保存文件信息到fileList，包含文件路径和其他信息
    const fileInfo = {
      name: file.name,
      url: materialApi.getMaterialPreviewUrl(filename), // 使用getMaterialPreviewUrl生成预览URL
      path: filePath,
      size: file.size,
      type: file.type
    }
    
    // 添加到文件列表
    tab.fileList.push(fileInfo)
    
    // 更新显示列表
    tab.displayFileList = [...tab.fileList.map(item => ({
      name: item.name,
      url: item.url
    }))]
    
    ElMessage.success('文件上传成功')
    console.log('上传成功:', fileInfo)
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

// 处理文件上传失败
const handleUploadError = (error) => {
  ElMessage.error('文件上传失败')
  console.error('上传错误:', error)
}

// 删除已上传文件
const removeFile = (tab, index) => {
  // 从文件列表中删除
  tab.fileList.splice(index, 1)
  
  // 更新显示列表
  tab.displayFileList = [...tab.fileList.map(item => ({
    name: item.name,
    url: item.url
  }))]
  
  ElMessage.success('文件删除成功')
}

// 话题相关方法
// 打开添加话题弹窗
const openTopicDialog = (tab) => {
  currentTab.value = tab
  topicDialogVisible.value = true
}

// 添加自定义话题
const addCustomTopic = () => {
  if (!customTopic.value.trim()) {
    ElMessage.warning('请输入话题内容')
    return
  }
  if (currentTab.value && !currentTab.value.selectedTopics.includes(customTopic.value.trim())) {
    currentTab.value.selectedTopics.push(customTopic.value.trim())
    customTopic.value = ''
    ElMessage.success('话题添加成功')
  } else {
    ElMessage.warning('话题已存在')
  }
}

// 切换推荐话题
const toggleRecommendedTopic = (topic) => {
  if (!currentTab.value) return
  
  const index = currentTab.value.selectedTopics.indexOf(topic)
  if (index > -1) {
    currentTab.value.selectedTopics.splice(index, 1)
  } else {
    currentTab.value.selectedTopics.push(topic)
  }
}

// 删除话题
const removeTopic = (tab, index) => {
  tab.selectedTopics.splice(index, 1)
}

// 确认添加话题
const confirmTopicSelection = () => {
  topicDialogVisible.value = false
  customTopic.value = ''
  currentTab.value = null
  ElMessage.success('添加话题完成')
}

// 账号选择相关方法
// 打开账号选择弹窗
const openAccountDialog = async (tab) => {
  currentTab.value = tab
  tempSelectedAccounts.value = [...tab.selectedAccounts]
  if (accountStore.accounts.length === 0) {
    await loadAccounts()
  }
  accountDialogVisible.value = true
}

// 确认账号选择
const confirmAccountSelection = () => {
  if (currentTab.value) {
    currentTab.value.selectedAccounts = [...tempSelectedAccounts.value]
  }
  accountDialogVisible.value = false
  currentTab.value = null
  ElMessage.success('账号选择完成')
}

// 删除选中的账号
const removeAccount = (tab, index) => {
  tab.selectedAccounts.splice(index, 1)
}

// 获取账号显示名称
const getAccountDisplayName = (accountId) => {
  const account = accountStore.accounts.find(acc => acc.id === accountId)
  return account ? account.name : accountId
}

// 取消发布
const cancelPublish = (tab) => {
  ElMessage.info('已取消发布')
}

// 确认发布
const confirmPublish = async (tab) => {
  // 防止重复点击
  if (tab.publishing) {
    return Promise.reject(new Error('正在发布中，请稍候...'))
  }

  tab.publishing = true // 设置发布状态为进行中

  return new Promise((resolve, reject) => {
    // 数据验证
    if (tab.fileList.length === 0) {
      ElMessage.error('请先上传视频文件')
      tab.publishing = false // 重置发布状态
      reject(new Error('请先上传视频文件'))
      return
    }
    if (!tab.title.trim()) {
      ElMessage.error('请输入标题')
      tab.publishing = false // 重置发布状态
      reject(new Error('请输入标题'))
      return
    }
    if (!tab.selectedPlatform) {
      ElMessage.error('请选择发布平台')
      tab.publishing = false // 重置发布状态
      reject(new Error('请选择发布平台'))
      return
    }
    if (tab.selectedAccounts.length === 0) {
      ElMessage.error('请选择发布账号')
      tab.publishing = false // 重置发布状态
      reject(new Error('请选择发布账号'))
      return
    }

    // 构造发布数据，符合后端API格式
    const publishData = {
      type: tab.selectedPlatform,
      title: tab.title,
      tags: tab.selectedTopics, // 不带#号的话题列表
      fileList: tab.fileList.map(file => file.path), // 只发送文件路径
      accountList: tab.selectedAccounts.map(accountId => {
        const account = accountStore.accounts.find(acc => acc.id === accountId)
        return account ? account.filePath : accountId
      }), // 发送账号的文件路径
      enableTimer: tab.scheduleEnabled ? 1 : 0, // 是否启用定时发布，开启传1，不开启传0
      videosPerDay: tab.scheduleEnabled ? tab.videosPerDay || 1 : 1, // 每天发布视频数量，1-55
      dailyTimes: tab.scheduleEnabled ? tab.dailyTimes || ['10:00'] : ['10:00'], // 每天发布时间点
      startDays: tab.scheduleEnabled ? tab.startDays || 0 : 0, // 从今天开始计算的发布天数，0表示明天，1表示后天
      category: 0, //表示非原创
      productLink: tab.productLink.trim() || '', // 商品链接
      productTitle: tab.productTitle.trim() || '', // 商品名称
      isDraft: tab.isDraft // 是否保存为草稿，仅视频号平台使用
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      controller.abort()
    }, 10 * 60 * 1000)

    // 调用指定 webhook
    fetch(VIDEO_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(publishData),
      signal: controller.signal
    })
    .then(response => response.json())
    .then(data => {
      if (data.code === 200) {
        tab.publishStatus = {
          message: '发布成功',
          type: 'success'
        }
        // 清空当前tab的数据
        tab.fileList = []
        tab.displayFileList = []
        tab.title = ''
        tab.selectedTopics = []
        tab.selectedAccounts = []
        tab.scheduleEnabled = false
        resolve()
      } else {
        tab.publishStatus = {
          message: `发布失败：${data.msg || '发布失败'}`,
          type: 'error'
        }
        reject(new Error(data.msg || '发布失败'))
      }
    })
    .catch(error => {
      console.error('发布错误:', error)
      tab.publishStatus = {
        message: '发布失败，请检查网络连接',
        type: 'error'
      }
      reject(error)
    })
    .finally(() => {
      clearTimeout(timeoutId)
      tab.publishing = false // 重置发布状态
    })
  })
}

// 显示上传选项
const showUploadOptions = (tab) => {
  currentUploadTab.value = tab
  uploadOptionsVisible.value = true
}

// 选择本地上传
const selectLocalUpload = () => {
  uploadOptionsVisible.value = false
  localUploadVisible.value = true
}

// 选择素材库
const selectMaterialLibrary = async () => {
  uploadOptionsVisible.value = false
  
  // 默认筛选生成素材
  materialSourceFilter.value = '生成素材'
  
  // 获取素材数据（支持筛选）
  try {
    const response = await materialApi.getAllMaterials(materialSourceFilter.value)
    if (response.code === 200) {
      appStore.setMaterials(response.data)
    } else {
      ElMessage.error('获取素材列表失败')
      return
    }
  } catch (error) {
    console.error('获取素材列表出错:', error)
    ElMessage.error('获取素材列表失败')
    return
  }
  
  selectedMaterials.value = []
  materialLibraryVisible.value = true
}

// 确认素材选择
const confirmMaterialSelection = () => {
  if (selectedMaterials.value.length === 0) {
    ElMessage.warning('请选择至少一个素材')
    return
  }
  
  if (currentUploadTab.value) {
    // 将选中的素材添加到当前tab的文件列表
    selectedMaterials.value.forEach(materialId => {
      const material = materials.value.find(m => m.id === materialId)
      if (material) {
        // 如果是生成素材（有uri字段），使用uri作为URL；否则使用预览URL
        const materialUrl = material.uri || materialApi.getMaterialPreviewUrl(material.file_path.split('/').pop())
        const fileInfo = {
          name: material.filename,
          url: materialUrl,
          path: material.uri || material.file_path, // 生成素材使用uri，其他使用file_path
          size: (material.filesize || 0) * 1024 * 1024, // 转换为字节
          type: 'video/mp4'
        }
        
        // 检查是否已存在相同文件
        const exists = currentUploadTab.value.fileList.some(file => file.path === fileInfo.path)
        if (!exists) {
          currentUploadTab.value.fileList.push(fileInfo)
        }
      }
    })
    
    // 更新显示列表
    currentUploadTab.value.displayFileList = [...currentUploadTab.value.fileList.map(item => ({
      name: item.name,
      url: item.url
    }))]
  }
  
  const addedCount = selectedMaterials.value.length
  materialLibraryVisible.value = false
  selectedMaterials.value = []
  currentUploadTab.value = null
  ElMessage.success(`已添加 ${addedCount} 个素材`)
}

// 批量发布对话框状态
const batchPublishDialogVisible = ref(false)
const currentPublishingTab = ref(null)
const publishProgress = ref(0)
const publishResults = ref([])
const isCancelled = ref(false)

// 取消批量发布
const cancelBatchPublish = () => {
  isCancelled.value = true
  ElMessage.info('正在取消发布...')
}

// 批量发布方法
const batchPublish = async () => {
  if (batchPublishing.value) return
  
  batchPublishing.value = true
  currentPublishingTab.value = null
  publishProgress.value = 0
  publishResults.value = []
  isCancelled.value = false
  batchPublishDialogVisible.value = true
  
  try {
    for (let i = 0; i < tabs.length; i++) {
      if (isCancelled.value) {
        publishResults.value.push({
          label: tabs[i].label,
          status: 'cancelled',
          message: '已取消'
        })
        continue
      }

      const tab = tabs[i]
      currentPublishingTab.value = tab
      publishProgress.value = Math.floor((i / tabs.length) * 100)
      
      try {
        await confirmPublish(tab)
        publishResults.value.push({
          label: tab.label,
          status: 'success',
          message: '发布成功'
        })
      } catch (error) {
        publishResults.value.push({
          label: tab.label,
          status: 'error',
          message: error.message
        })
        // 不立即返回，继续显示发布结果
      }
    }
    
    publishProgress.value = 100
    
    // 统计发布结果
    const successCount = publishResults.value.filter(r => r.status === 'success').length
    const failCount = publishResults.value.filter(r => r.status === 'error').length
    const cancelCount = publishResults.value.filter(r => r.status === 'cancelled').length
    
    if (isCancelled.value) {
      ElMessage.warning(`发布已取消：${successCount}个成功，${failCount}个失败，${cancelCount}个未执行`)
    } else if (failCount > 0) {
      ElMessage.error(`发布完成：${successCount}个成功，${failCount}个失败`)
    } else {
      ElMessage.success('所有Tab发布成功')
      setTimeout(() => {
        batchPublishDialogVisible.value = false
      }, 1000)
    }
    
  } catch (error) {
    console.error('批量发布出错:', error)
    ElMessage.error('批量发布出错，请重试')
  } finally {
    batchPublishing.value = false
    isCancelled.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.publish-center {
  min-height: 100%;
  animation: fadeIn 0.6s ease-out;
  
  // 任务工具栏 - 高级扁平设计
  .task-toolbar {
    background: #ffffff;
    padding: 14px 20px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: -1px;
    margin-bottom: 12px;
    
    .toolbar-info {
      .task-count {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #475569;
        
        .el-icon {
          color: #6366f1;
          font-size: 16px;
        }
      }
    }
    
    .toolbar-actions {
      display: flex;
      gap: 10px;
      
      .el-button {
        border-radius: 6px;
        font-weight: 500;
        height: 36px;
        padding: 0 18px;
        font-size: 14px;
        border: none;
        
        .el-icon {
          font-size: 16px;
        }
        
        &.create-task-btn {
          background: #6366f1;
          color: white;
          
          &:hover {
            background: #4f46e5;
          }
        }
        
        &.batch-publish-btn {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f1f5f9;
            border-color: #cbd5e1;
            color: #334155;
          }
          
          .el-icon {
            margin-right: 6px;
          }
        }

        &.select-all-btn,
        &.refresh-list-btn {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #334155;
          }
          
          .el-icon {
            margin-right: 6px;
          }
        }

        &.delete-selected-btn {
          background: #fff1f1;
          border: 1px solid #fecaca;
          color: #dc2626;
          
          &:hover {
            background: #fee2e2;
            border-color: #fca5a5;
            color: #b91c1c;
          }
        }
      }
    }
  }
  
  // 任务卡片容器 - 高级扁平设计
  .task-cards-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 10px;
    margin-top: 0;
    
    .task-card {
      background: #ffffff;
      border-radius: 6px;
      padding: 8px 14px;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid #e2e8f0;
      min-height: 40px;
      display: flex;
      align-items: center;
      position: relative;
      
      &:hover {
        border-color: #cbd5e1;
        background: #f8fafc;
      }
      
      &.active {
        border-color: #6366f1;
        background: #f0f4ff;
        border-width: 2px;
        
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 0;
          bottom: 0;
          width: 3px;
          background: #6366f1;
          border-radius: 6px 0 0 6px;
        }
      }
      
      .task-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        gap: 12px;
        
        .task-info {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 10px;
          flex: 1;
          
          .task-type-tag {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            border-radius: 4px;
            font-weight: 500;
            padding: 4px 10px;
            font-size: 12px;
            white-space: nowrap;
            border: none;
            
            &.el-tag {
              border: none;
            }
            
            &.el-tag--warning {
              background: #fff7ed;
              color: #ea580c;
            }
            
            &.el-tag--info {
              background: #eff6ff;
              color: #2563eb;
            }
            
            .el-icon {
              font-size: 14px;
            }
          }
          
          .task-title {
            font-size: 14px;
            font-weight: 500;
            color: #0f172a;
            line-height: 1.4;
            white-space: nowrap;
          }
        }
        
        .task-actions {
          .remove-icon {
            font-size: 16px;
            color: #94a3b8;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.15s ease;
            
            &:hover {
              background: #fee2e2;
              color: #dc2626;
            }
          }
        }
      }
    }
  }
  
  // Tab管理区域（保留用于向后兼容）
  .tab-management {
    background-color: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    margin-bottom: 20px;
    padding: 15px 20px;
    
    .tab-header {
      display: flex;
      align-items: flex-start;
      gap: 15px;
      
      .tab-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        flex: 1;
        min-width: 0;
        
        .tab-item {
           display: flex;
           align-items: center;
           gap: 6px;
           padding: 6px 12px;
           background-color: #f5f7fa;
           border: 1px solid #dcdfe6;
           border-radius: 4px;
           cursor: pointer;
           transition: all 0.3s;
           font-size: 14px;
           height: 32px;
           
           &:hover {
             background-color: #ecf5ff;
             border-color: #b3d8ff;
           }
           
           &.active {
             background-color: #409eff;
             border-color: #409eff;
             color: #fff;
             
             .close-icon {
               color: #fff;
               
               &:hover {
                 background-color: rgba(255, 255, 255, 0.2);
               }
             }
           }
           
           .close-icon {
             padding: 2px;
             border-radius: 2px;
             cursor: pointer;
             transition: background-color 0.3s;
             font-size: 12px;
             
             &:hover {
               background-color: rgba(0, 0, 0, 0.1);
             }
           }
         }
       }
       
      .tab-actions {
        display: flex;
        gap: 10px;
        flex-shrink: 0;
        
        .add-tab-btn,
        .batch-publish-btn {
          display: flex;
          align-items: center;
          gap: 4px;
          height: 32px;
          padding: 6px 12px;
          font-size: 14px;
          white-space: nowrap;
        }
      }
    }
  }
  
  // 批量发布进度对话框样式
  .publish-progress {
    padding: 20px;
    
    .current-publishing {
      margin: 15px 0;
      text-align: center;
      color: #606266;
    }

    .publish-results {
      margin-top: 15px;
      border-top: 1px solid #EBEEF5;
      padding-top: 15px;
      max-height: 300px;
      overflow-y: auto;

      .result-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        color: #606266;

        .el-icon {
          margin-right: 8px;
        }

        .label {
          margin-right: 10px;
          font-weight: 500;
        }

        .message {
          color: #909399;
        }

        &.success {
          color: #67C23A;
        }

        &.error {
          color: #F56C6C;
        }

        &.cancelled {
          color: #909399;
        }
      }
    }
  }

  .dialog-footer {
    text-align: right;
  }
  
  // 内容区域
  .publish-content {
    flex: 1;
    
    .publish-tabs {
      background-color: #fff;
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      
      .publish-tabs-nav {
        padding: 20px;
      }
    }
    
    .production-list-panel {
      padding: 0 0px 20px 0px;
      background: #ffffff;
      
      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 16px;
        
        .panel-title {
          h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #0f172a;
          }
          
          p {
            margin: 4px 0 0;
            font-size: 13px;
            color: #64748b;
          }
        }
      }
      
      .panel-actions {
        display: flex;
        align-items: center;
        
        .refresh-list-btn {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #334155;
          }
          
          .el-icon {
            margin-right: 6px;
          }
        }
      }
      
      .task-table {
        // 标题、摘要、正文列：最多显示3行，超出省略
        :deep(.title-column),
        :deep(.summary-column),
        :deep(.content-column) {
          .cell {
            padding: 12px 16px !important;
            
            .text-ellipsis-3 {
              display: -webkit-box !important;
              -webkit-box-orient: vertical !important;
              -webkit-line-clamp: 3 !important;
              line-clamp: 3 !important;
              overflow: hidden !important;
              text-overflow: ellipsis !important;
              word-break: break-word !important;
              word-wrap: break-word !important;
              line-height: 1.5 !important;
              max-height: calc(1.5em * 3) !important; // 3行的高度
            }
          }
        }
        
        // 标题列特殊处理（没有text-ellipsis-3包装）
        :deep(.title-column) {
          .cell {
            display: -webkit-box !important;
            -webkit-box-orient: vertical !important;
            -webkit-line-clamp: 3 !important;
            line-clamp: 3 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            word-break: break-word !important;
            word-wrap: break-word !important;
            line-height: 1.5 !important;
            max-height: calc(1.5em * 3) !important;
            padding: 12px 16px !important;
            white-space: normal !important;
          }
        }
        
        // 摘要和正文列的特殊处理
        :deep(.summary-column),
        :deep(.content-column) {
          .cell {
            white-space: normal !important;
            
            .text-ellipsis-3 {
              white-space: normal !important;
            }
          }
        }
        
        :deep(.el-table__header) {
          th {
            background-color: #f8fafc;
            color: #1e293b;
            font-weight: 600;
            font-size: 14px;
            padding: 14px 0;
            height: auto;
            line-height: 1.5;
          }
        }
        
        :deep(.el-table__body) {
          td {
            padding: 16px 0;
            font-size: 13px;
            color: #334155;
            height: auto;
            line-height: 1.5;
            vertical-align: middle;
            
            // 确保标题、摘要、正文列可以换行
            &.title-column,
            &.summary-column,
            &.content-column {
              .cell {
                white-space: normal !important;
              }
            }
          }
          
          tr {
            height: auto;
            min-height: 56px;
          }
        }
        
        :deep(.el-table__row) {
          height: auto;
          min-height: 56px;
        }
        
        :deep(.el-table__cell) {
          padding: 16px 0;
          vertical-align: middle;
        }
        
        // 确保按钮和标签在同一行高度对齐
        :deep(.el-button) {
          height: 28px;
          padding: 5px 12px;
          line-height: 1;
          vertical-align: middle;
        }
        
        :deep(.el-tag) {
          height: 24px;
          line-height: 22px;
          padding: 0 8px;
          vertical-align: middle;
        }
        
        .content-cell {
          max-width: 300px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          color: #64748b;
          font-size: 13px;
          line-height: 1.5;
        }
      }
      
      // 表格tooltip样式：宽度与列宽保持一致，高级样式
      :deep(.el-tooltip__popper) {
        padding: 10px 14px !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 252, 255, 0.98) 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        backdrop-filter: blur(8px) !important;
        color: #303133 !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        word-break: break-word !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
        
        .el-tooltip__arrow {
          &::before {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 252, 255, 0.98) 100%) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
          }
        }
      }
      
      // 固定宽度列的tooltip：宽度与列宽一致
      // 创建时间列 (width="150")
      :deep(.el-table__body) {
        tr {
          td:nth-child(2) { // 创建时间列（第2列，第1列是checkbox）
            .cell {
              .el-tooltip__popper {
                width: 150px !important;
                max-width: 150px !important;
              }
            }
          }
        }
      }
      
      // 制作类型列 (width="140")
      :deep(.el-table__body) {
        tr {
          td:nth-child(3) { // 制作类型列
            .cell {
              .el-tooltip__popper {
                width: 140px !important;
                max-width: 140px !important;
              }
            }
          }
        }
      }
      
      // 发布平台列 (width="120")
      :deep(.el-table__body) {
        tr {
          td:nth-child(4) { // 发布平台列
            .cell {
              .el-tooltip__popper {
                width: 120px !important;
                max-width: 120px !important;
              }
            }
          }
        }
      }
      
      // 发布状态列 (width="120")
      :deep(.el-table__body) {
        tr {
          td:nth-child(5) { // 发布状态列
            .cell {
              .el-tooltip__popper {
                width: 120px !important;
                max-width: 120px !important;
              }
            }
          }
        }
      }
      
      // 标题列 (min-width="150") - 使用class-name定位
      :deep(.title-column) {
        .cell {
          .el-tooltip__popper {
            min-width: 150px !important;
            max-width: 300px !important; // 允许tooltip稍宽一些以显示完整内容
          }
        }
      }
      
      // 摘要列 (min-width="150") - 使用class-name定位
      :deep(.summary-column) {
        .cell {
          .el-tooltip__popper {
            min-width: 150px !important;
            max-width: 300px !important;
          }
        }
      }
      
      // 正文列 (min-width="150") - 使用class-name定位
      :deep(.content-column) {
        .cell {
          .el-tooltip__popper {
            min-width: 150px !important;
            max-width: 400px !important; // 正文可能较长，允许更宽
          }
        }
      }
      
      // 图片/媒资链接列 (min-width="150") - 通过列位置定位
      :deep(.el-table__body) {
        tr {
          td:nth-child(9) { // 图片/媒资链接列（根据列顺序，通常是第9列）
            .cell {
              .el-tooltip__popper {
                min-width: 150px !important;
                max-width: 300px !important;
              }
            }
          }
        }
      }
      
      // 其他配置列 (min-width="100") - 通过列位置定位
      :deep(.el-table__body) {
        tr {
          td:nth-child(10) { // 其他配置列
            .cell {
              .el-tooltip__popper {
                min-width: 100px !important;
                max-width: 200px !important;
              }
            }
          }
        }
      }
      
      // 操作列 (width="160") - 最后一列
      :deep(.el-table__body) {
        tr {
          td:last-child { // 操作列（最后一列）
            .cell {
              .el-tooltip__popper {
                width: 160px !important;
                max-width: 160px !important;
              }
            }
          }
        }
      }
    }
    
    .tab-content-wrapper {
      display: flex;
      justify-content: flex-start;
      
      .tab-content {
        width: 100%;
        
        h3 {
          font-size: 14px;
          font-weight: 600;
          color: #1e293b;
          margin: 0 0 8px 0;
        }
        
        // 全局表单控件紧凑优化
        :deep(.el-input__wrapper) {
          border-radius: 6px;
          box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.08) inset;
          
          &:hover {
            box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.2) inset;
          }
          
          &.is-focus {
            box-shadow: 0 0 0 1px #667eea inset;
          }
        }
        
        :deep(.el-input),
        :deep(.el-textarea) {
          font-size: 13px;
          
          .el-input__inner,
          .el-textarea__inner {
            font-size: 13px;
          }
        }
        
        :deep(.el-button) {
          font-size: 13px;
          border-radius: 6px;
          height: 32px;
          padding: 0 15px;
          
          &.el-button--primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
            
            &:hover {
              opacity: 0.92;
              box-shadow: 0 4px 10px rgba(102, 126, 234, 0.35);
            }
          }

  }
        }
        
        :deep(.el-checkbox),
        :deep(.el-radio) {
          font-size: 13px;
          
          .el-checkbox__label,
          .el-radio__label {
            font-size: 13px;
          }
        }
        
        :deep(.el-select) {
          font-size: 13px;
          
          .el-input__wrapper {
            height: 32px;
          }
        }
        
        :deep(.el-switch) {
          height: 20px;
          
          .el-switch__core {
            height: 20px;
          }
        }
        
        .upload-section,
        .account-section,
        .platform-section,
        .title-section,
        .product-section,
        .topic-section,
        .schedule-section {
          margin-bottom: 16px;
          
          h3 {
            font-size: 13px !important;
            font-weight: 600;
            margin-bottom: 8px !important;
          }
        }

        .product-section {
          .product-name-input,
          .product-link-input {
            margin-bottom: 5px;
          }
        }
        
        .video-upload {
          width: 100%;
          
          :deep(.el-upload-dragger) {
            width: 100%;
            height: 180px;
          }
        }
        
        .account-input {
          max-width: 400px;
        }
        
        .platform-buttons {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          
          .platform-btn {
            min-width: 70px;
            height: 32px;
            font-size: 13px;
            padding: 0 12px;
            border-radius: 6px;
          }
        }
        
        .title-input {
          max-width: 600px;
        }
        
        .topic-display {
          display: flex;
          flex-direction: column;
          gap: 12px;
          
          .selected-topics {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 32px;
            
            .topic-tag {
              font-size: 14px;
            }
          }
          
          .select-topic-btn {
            align-self: flex-start;
          }
        }
        
        .schedule-controls {
          display: flex;
          flex-direction: column;
          gap: 12px;

          .schedule-settings {
            margin-top: 10px;
            padding: 12px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.02) 100%);
            border-radius: 8px;
            border: 1px solid rgba(102, 126, 234, 0.08);

            .schedule-item {
              display: flex;
              align-items: center;
              margin-bottom: 15px;

              &:last-child {
                margin-bottom: 0;
              }

              .label {
                min-width: 120px;
                margin-right: 10px;
              }

              .el-time-select {
                margin-right: 10px;
              }

              .el-button {
                margin-left: 10px;
              }
            }
          }
        }
        
        .action-buttons {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #ebeef5;
        }

        .draft-section {
          margin: 20px 0;

          .draft-checkbox {
            display: block;
            margin: 10px 0;
          }
        }
      }
    }
  }
  
  .record-detail {
    .detail-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px 24px;
      font-size: 13px;
      color: #475569;
      margin-bottom: 16px;
    }

    .detail-block {
      margin-bottom: 20px;

      h4 {
        margin: 0 0 8px;
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
      }

      p {
        margin: 0;
        color: #475569;
        line-height: 1.6;
        word-break: break-word;
      }
    }

    .detail-content {
      background: #f8fafc;
      border-radius: 6px;
      padding: 16px;
      white-space: pre-wrap;
      font-size: 13px;
      line-height: 1.8;
      color: #0f172a;
      border: 1px solid #e2e8f0;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;

      p {
        font-size: 13px;
      }
    }
  }

  // 已上传文件列表样式
  .uploaded-files {
    margin-top: 15px;
    
    h4 {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 12px;
      color: #303133;
    }
    
    .file-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      
      .file-item {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        background-color: #f5f7fa;
        border-radius: 4px;
        
        .el-link {
          margin-right: 10px;
          max-width: 300px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .file-size {
          color: #909399;
          font-size: 13px;
          margin-right: auto;
        }
      }
    }
  }
  
  // 添加话题弹窗样式
  .topic-dialog {
    .topic-dialog-content {
      .custom-topic-input {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        
        .custom-input {
          flex: 1;
        }
      }
      
      .recommended-topics {
        h4 {
          margin: 0 0 16px 0;
          font-size: 16px;
          font-weight: 500;
          color: #303133;
        }
        
        .topic-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
          gap: 12px;
          
          .topic-btn {
            height: 36px;
            font-size: 14px;
            border-radius: 6px;
            min-width: 100px;
            padding: 0 12px;
            white-space: nowrap;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            
            &.el-button--primary {
              background-color: #409eff;
              border-color: #409eff;
              color: white;
            }
          }
        }
      }
    }
    
    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }

  // 内容类型选择 Modal 样式 - 高级扁平设计
  .content-type-dialog {
    :deep(.el-dialog) {
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      
      .el-dialog__header {
        padding: 0;
        border-bottom: none;
      }
      
      .el-dialog__body {
        padding: 0 24px 24px;
      }
      
      .el-dialog__footer {
        padding: 16px 24px;
        border-top: 1px solid #e2e8f0;
      }
    }
    
    .dialog-header-custom {
      padding: 20px 24px 16px;
      background: #ffffff;
      
      h2 {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 6px 0;
      }
      
      p {
        font-size: 13px;
        color: #64748b;
        margin: 0;
      }
    }
    
    .content-type-selection {
      padding: 0;
      
      .type-cards {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        
        .type-card {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 20px 16px;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
          
          &:hover {
            border-color: #cbd5e1;
            background: #f8fafc;
          }
          
          &.selected {
            border-color: #6366f1;
            background: #f0f4ff;
            border-width: 2px;
            
            &::before {
              content: '';
              position: absolute;
              left: 0;
              top: 0;
              bottom: 0;
              width: 3px;
              background: #6366f1;
              border-radius: 8px 0 0 8px;
            }
            
            .type-card-icon {
              background: #f0f4ff;
              
              .el-icon {
                color: #6366f1;
              }
            }
            
            .type-card-check {
              opacity: 1;
            }
          }
          
          .type-card-icon {
            width: 56px;
            height: 56px;
            margin: 0 auto 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8fafc;
            border-radius: 8px;
            
            .el-icon {
              color: #475569;
              transition: all 0.2s ease;
              font-size: 28px;
            }
          }
          
          .type-card-content {
            text-align: center;
            
            .type-card-title {
              font-size: 14px;
              font-weight: 600;
              color: #1e293b;
              margin: 0 0 8px 0;
            }
            
            .type-card-desc {
              font-size: 12px;
              color: #64748b;
              margin: 0 0 12px 0;
              line-height: 1.5;
            }
            
            .type-card-features {
              list-style: none;
              padding: 0;
              margin: 0;
              text-align: left;
              
              li {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 12px;
                color: #475569;
                margin-bottom: 6px;
                
                &:last-child {
                  margin-bottom: 0;
                }
                
                .el-icon {
                  color: #10b981;
                  font-size: 14px;
                  flex-shrink: 0;
                }
              }
            }
          }
          
          .type-card-check {
            position: absolute;
            top: 12px;
            right: 12px;
            width: 20px;
            height: 20px;
            background: #6366f1;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
            
            .el-icon {
              color: white;
              font-size: 12px;
            }
          }
        }
      }
    }
    
    .dialog-footer-custom {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      
      .el-button {
        border-radius: 6px;
        font-size: 13px;
        height: 36px;
        padding: 0 20px;
        
        &.el-button--primary {
          background: #6366f1;
          border: none;
          
          &:hover {
            background: #4f46e5;
          }
        }
        
        &.el-button--default {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
          }
        }
      }
    }
  }

  // 视频内容区域样式（与文章和图文模块保持一致）
  .video-content {
    max-width: 100%;
    width: 100%;
    margin: 0 auto;
    padding: 0;
    
    // 使用网格布局实现两列
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }
    
    // 全宽表单项
    .form-section-full {
      grid-column: 1 / -1;
    }
    
    .form-section {
      background: #ffffff;
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 0;
      border: 1px solid #e2e8f0;
      
      h3 {
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 16px 0;
        letter-spacing: -0.01em;
        
        .required {
          color: #ef4444;
          margin-left: 4px;
          font-size: 14px;
        }
      }
      
      :deep(.el-radio-group) {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .el-radio {
          margin: 0;
          padding: 8px 16px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          transition: all 0.15s ease;
          white-space: nowrap;
          
          &:hover {
            background: #f1f5f9;
            border-color: #cbd5e1;
          }
          
          &.is-checked {
            background: #6366f1;
            border-color: #6366f1;
            
            .el-radio__label {
              color: #ffffff;
              font-weight: 500;
            }
            
            .el-radio__input {
              .el-radio__inner {
                background: #ffffff;
                border-color: #ffffff;
                
                &::after {
                  background: #6366f1;
                }
              }
            }
          }
          
          .el-radio__input {
            .el-radio__inner {
              width: 16px;
              height: 16px;
              border-width: 1.5px;
              border-color: #cbd5e1;
              
              &::after {
                width: 6px;
                height: 6px;
              }
            }
          }
          
          .el-radio__label {
            font-size: 14px;
            color: #475569;
            padding-left: 8px;
            line-height: 1.5;
          }
        }
      }
      
      :deep(.el-input),
      :deep(.el-textarea) {
        .el-input__wrapper,
        .el-textarea__inner {
          background: #ffffff;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
          transition: all 0.15s ease;
          padding: 10px 14px;
          font-size: 14px;
          
          &:hover {
            border-color: #cbd5e1;
          }
          
          &:focus,
          &.is-focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
          }
        }
        
        .el-input__count {
          background: transparent;
          color: #94a3b8;
          font-size: 12px;
        }
      }
      
      :deep(.el-select) {
        width: 100%;
        
        .el-input__wrapper {
          background: #ffffff;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
          transition: all 0.15s ease;
          
          &:hover {
            border-color: #cbd5e1;
          }
          
          &.is-focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
          }
        }
      }
      
      :deep(.el-switch) {
        .el-switch__label {
          font-size: 14px;
          color: #475569;
        }
      }
      
      // 上传按钮样式
      .upload-options {
        margin-bottom: 16px;
        
        .upload-btn {
          min-width: 120px;
          height: 40px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
        }
      }
      
      // 已上传文件列表样式
      .uploaded-files {
        margin-top: 16px;
        
        .file-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          
          .file-item {
            display: flex;
            align-items: center;
            padding: 10px 14px;
            background-color: #f8fafc;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            
            .el-link {
              margin-right: 10px;
              max-width: 300px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              font-size: 14px;
            }
            
            .file-size {
              color: #64748b;
              font-size: 13px;
              margin-right: auto;
            }
            
            .el-button {
              font-size: 12px;
              height: 28px;
              padding: 0 12px;
            }
          }
        }
      }
      
      // 账号显示样式
      .account-display {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .selected-accounts {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          min-height: 32px;
          
          .account-tag {
            font-size: 14px;
          }
        }
        
        .select-account-btn {
          align-self: flex-start;
        }
      }
      
      // 话题显示样式
      .topic-display {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .selected-topics {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          min-height: 32px;
          
          .topic-tag {
            font-size: 14px;
          }
        }
        
        .select-topic-btn {
          align-self: flex-start;
        }
      }
      
      // 定时发布样式
      .schedule-controls {
        display: flex;
        flex-direction: column;
        gap: 16px;
        
        .schedule-settings {
          margin-top: 12px;
          padding: 16px;
          background: #f8fafc;
          border-radius: 8px;
          border: 1px solid #e2e8f0;
          
          .schedule-item {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .label {
              min-width: 120px;
              margin-right: 12px;
              font-size: 14px;
              color: #475569;
            }
            
            .el-time-select {
              margin-right: 10px;
            }
            
            .el-button {
              margin-left: 10px;
            }
          }
        }
      }
      
      // 草稿选项样式
      .draft-checkbox {
        :deep(.el-checkbox__label) {
          font-size: 14px;
          color: #475569;
        }
      }
    }
    
    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid #e2e8f0;
      
      .el-button {
        min-width: 100px;
        height: 40px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.15s ease;
        border: none;
        
        &:not(.el-button--primary) {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #334155;
          }
        }
        
        &.el-button--primary {
          background: #6366f1;
          color: #ffffff;
          
          &:hover {
            background: #4f46e5;
          }
          
          &.is-loading {
            background: #6366f1;
          }
        }
      }
    }
  }

  // 文章内容区域样式 - 高级扁平设计
  .article-content {
    max-width: 100%;
    width: 100%;
    margin: 0 auto;
    padding: 0;
    
    // 使用网格布局实现两列
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }
    
    // 全宽表单项
    .form-section-full {
      grid-column: 1 / -1;
    }
    
    .form-section {
      background: #ffffff;
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 0;
      border: 1px solid #e2e8f0;
      
      h3 {
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 16px 0;
        letter-spacing: -0.01em;
        
        .required {
          color: #ef4444;
          margin-left: 4px;
          font-size: 14px;
        }
      }
      
      :deep(.el-radio-group) {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .el-radio {
          margin: 0;
          padding: 8px 16px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          transition: all 0.15s ease;
          white-space: nowrap;
          
          &:hover {
            background: #f1f5f9;
            border-color: #cbd5e1;
          }
          
          &.is-checked {
            background: #6366f1;
            border-color: #6366f1;
            
            .el-radio__label {
              color: #ffffff;
              font-weight: 500;
            }
            
            .el-radio__input {
              .el-radio__inner {
                background: #ffffff;
                border-color: #ffffff;
                
                &::after {
                  background: #6366f1;
                }
              }
            }
          }
          
          .el-radio__input {
            .el-radio__inner {
              width: 16px;
              height: 16px;
              border-width: 1.5px;
              border-color: #cbd5e1;
              
              &::after {
                width: 6px;
                height: 6px;
              }
            }
          }
          
          .el-radio__label {
            font-size: 14px;
            color: #475569;
            padding-left: 8px;
            line-height: 1.5;
          }
        }
      }
      
      // 字数选择特殊样式
      &:has(.word-count-group) {
        :deep(.el-radio-group) {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
          gap: 10px;
          
          .el-radio {
            padding: 10px 8px;
            text-align: center;
            justify-content: center;
            
            .el-radio__input {
              display: none;
            }
            
            .el-radio__label {
              padding: 0;
              font-weight: 500;
              color: #64748b;
            }
            
            &.is-checked {
              background: #6366f1;
              border-color: #6366f1;
              
              .el-radio__label {
                color: #ffffff;
              }
            }
          }
        }
      }
      
      :deep(.el-input),
      :deep(.el-textarea) {
        .el-input__wrapper,
        .el-textarea__inner {
          background: #ffffff;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
          transition: all 0.15s ease;
          padding: 10px 14px;
          font-size: 14px;
          
          &:hover {
            border-color: #cbd5e1;
          }
          
          &:focus,
          &.is-focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
          }
        }
        
        .el-input__count {
          background: transparent;
          color: #94a3b8;
          font-size: 12px;
        }
      }
      
      :deep(.el-select) {
        width: 100%;
        
        .el-input__wrapper {
          background: #ffffff;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
          transition: all 0.15s ease;
          
          &:hover {
            border-color: #cbd5e1;
          }
          
          &.is-focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
          }
        }
      }
    }
    
    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid #e2e8f0;
      
      .el-button {
        min-width: 100px;
        height: 40px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.15s ease;
        border: none;
        
        &:not(.el-button--primary) {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #334155;
          }
        }
        
        &.el-button--primary {
          background: #6366f1;
          color: #ffffff;
          
          &:hover {
            background: #4f46e5;
          }
          
          &.is-loading {
            background: #6366f1;
          }
        }
      }
    }
  }

  // 图文内容区域样式（与文章模块保持一致）
  .image-text-content {
    max-width: 100%;
    width: 100%;
    margin: 0 auto;
    padding: 0;
    
    // 使用网格布局实现两列
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }
    
    // 全宽表单项
    .form-section-full {
      grid-column: 1 / -1;
    }
    
    .form-section {
      background: #ffffff;
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 0;
      border: 1px solid #e2e8f0;
      
      h3 {
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 16px 0;
        letter-spacing: -0.01em;
        
        .required {
          color: #ef4444;
          margin-left: 4px;
          font-size: 14px;
        }
      }
      
      :deep(.el-radio-group) {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .el-radio {
          margin: 0;
          padding: 8px 16px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          transition: all 0.15s ease;
          white-space: nowrap;
          
          &:hover {
            background: #f1f5f9;
            border-color: #cbd5e1;
          }
          
          &.is-checked {
            background: #6366f1;
            border-color: #6366f1;
            
            .el-radio__label {
              color: #ffffff;
              font-weight: 500;
            }
            
            .el-radio__input {
              .el-radio__inner {
                background: #ffffff;
                border-color: #ffffff;
                
                &::after {
                  background: #6366f1;
                }
              }
            }
          }
          
          .el-radio__input {
            .el-radio__inner {
              width: 16px;
              height: 16px;
              border-width: 1.5px;
              border-color: #cbd5e1;
              
              &::after {
                width: 6px;
                height: 6px;
              }
            }
          }
          
          .el-radio__label {
            font-size: 14px;
            color: #475569;
            padding-left: 8px;
            line-height: 1.5;
          }
        }
      }
      
      // 字数选择特殊样式
      &:has(.word-count-group) {
        :deep(.el-radio-group) {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
          gap: 10px;
          
          .el-radio {
            padding: 10px 8px;
            text-align: center;
            justify-content: center;
            
            .el-radio__input {
              display: none;
            }
            
            .el-radio__label {
              padding: 0;
              font-weight: 500;
              color: #64748b;
            }
            
            &.is-checked {
              background: #6366f1;
              border-color: #6366f1;
              
              .el-radio__label {
                color: #ffffff;
              }
            }
          }
        }
      }
      
      :deep(.el-input),
      :deep(.el-textarea) {
        .el-input__wrapper,
        .el-textarea__inner {
          background: #ffffff;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
          transition: all 0.15s ease;
          padding: 10px 14px;
          font-size: 14px;
          
          &:hover {
            border-color: #cbd5e1;
          }
          
          &:focus,
          &.is-focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
          }
        }
        
        .el-input__count {
          background: transparent;
          color: #94a3b8;
          font-size: 12px;
        }
      }
      
      :deep(.el-select) {
        width: 100%;
        
        .el-input__wrapper {
          background: #ffffff;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
          transition: all 0.15s ease;
          
          &:hover {
            border-color: #cbd5e1;
          }
          
          &.is-focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
          }
        }
      }
    }
    
    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid #e2e8f0;
      
      .el-button {
        min-width: 100px;
        height: 40px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.15s ease;
        border: none;
        
        &:not(.el-button--primary) {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #475569;
          
          &:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #334155;
          }
        }
        
        &.el-button--primary {
          background: #6366f1;
          color: #ffffff;
          
          &:hover {
            background: #4f46e5;
          }
          
          &.is-loading {
            background: #6366f1;
          }
        }
    }
  }
}

// 发布平台选择弹窗样式（与制作中心图文配置弹窗样式一致）
.publish-platform-dialog {
  :deep(.el-dialog) {
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    
    .el-dialog__header {
      padding: 0;
      border-bottom: none;
    }
    
    .el-dialog__body {
      padding: 0;
    }
    
    .el-dialog__footer {
      padding: 0;
      border-top: none;
    }
  }
  
  .dialog-header-custom {
    padding: 12px 28px;
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    
    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #1e293b;
      margin: 0;
    }
  }
  
  .dialog-footer-custom {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 28px;
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    
    .el-button {
      border-radius: 6px;
      font-size: 13px;
      height: 36px;
      padding: 0 20px;
      
      &.el-button--default {
        background: #ffffff;
        border-color: #e2e8f0;
        color: #64748b;
        
        &:hover {
          background: #f8fafc;
          border-color: #cbd5e1;
          color: #475569;
        }
      }
      
      &.el-button--primary {
        background: #6366f1;
        border-color: #6366f1;
        color: #ffffff;
        
        &:hover {
          background: #4f46e5;
          border-color: #4f46e5;
        }
      }
    }
  }
  

  
  .action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #e2e8f0;
    
    .el-button {
      min-width: 100px;
      height: 40px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.15s ease;
      border: none;
      
      &:not(.el-button--primary) {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #475569;
        
        &:hover {
          background: #f8fafc;
          border-color: #cbd5e1;
          color: #334155;
        }
      }
      
      &.el-button--primary {
        background: #6366f1;
        color: #ffffff;
        
        &:hover {
          background: #4f46e5;
        }
        
        &.is-loading {
          background: #6366f1;
        }
      }
    }
  }
}

// 全局动画
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

// 设置所有 el-tooltip 的最大宽度
:deep(.el-tooltip__popper) {
  max-width: 200px !important;
  word-break: break-word !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  white-space: normal !important;
}
</style>

<style lang="scss">
// 自定义发布中心 tooltip 样式（最大宽度 200px，黑色背景）
.custom-publish-tooltip {
  max-width: 200px !important;
  min-width: 100px !important;
  word-break: break-word !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  white-space: normal !important;
  padding: 8px 12px !important;
  font-size: 13px !important;
  line-height: 1.5 !important;
  background: rgba(0, 0, 0, 0.75) !important;
  border: none !important;
  border-radius: 4px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
  color: #ffffff !important;
  
  // 箭头样式
  .el-tooltip__arrow {
    &::before {
      background: rgba(0, 0, 0, 0.75) !important;
      border: none !important;
    }
  }
}
</style>

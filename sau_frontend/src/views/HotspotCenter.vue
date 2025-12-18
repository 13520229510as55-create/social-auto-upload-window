<template>
  <div class="hotspot-center">
    <div class="hotspot-tabs">
      <el-tabs v-model="activeTab" class="hotspot-tabs-nav">
        <el-tab-pane label="公众号" name="wechat">
          <div class="hotspot-list-container">
            <!-- 公众号文章列表 -->
            <div class="wechat-articles-section">
            
              
              <!-- 筛选区域 -->
              <div class="filter-section">
                <div class="filter-container">
                  <!-- 第一行：筛选项（水平布局） -->
                  <div class="filter-row">
                    <div class="filter-item filter-item-checkbox">
                      <label class="filter-label">公众号</label>
                      <el-checkbox-group 
                        v-model="filterForm.selectedAccounts"
                        class="account-checkbox-group"
                      >
                        <el-checkbox 
                          v-for="rss in rssListFromStorage" 
                          :key="rss.accountName"
                          :label="rss.accountName"
                          class="account-checkbox"
                        >
                          {{ rss.accountName }}
                        </el-checkbox>
                      </el-checkbox-group>
                      <div v-if="rssListFromStorage.length === 0" class="no-rss-tip">
                        暂无RSS配置，请先在"RSS管理的页面"中添加
                      </div>
                    </div>
                    
                    <div class="filter-item">
                      <label class="filter-label">标题</label>
                      <el-input
                        v-model="filterForm.title"
                        placeholder="请输入标题关键词"
                        clearable
                        class="filter-input"
                      />
                    </div>
                    
                    <div class="filter-item">
                      <label class="filter-label">发布时间</label>
                      <el-date-picker
                        v-model="filterForm.pubtimeRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        class="filter-date-picker"
                      />
                    </div>
                    <div class="filter-item ">
                      <label class="filter-label">选择类型</label>
                      <el-select
                        v-model="refreshMonitorType"
                        placeholder="选择类型"
                        style="width: 120px; margin-right: 8px;"
                      >
                        <el-option label="前端" value="前端" />
                        <el-option label="Ai博主" value="Ai博主" />
                      </el-select>
                    
                    </div>
                  </div>
                  
                  <!-- 第二行：按钮（水平布局） -->
                  <div class="filter-row filter-row-buttons">
                    <div class="filter-item filter-item-button">
                      <el-button 
                        type="primary" 
                        @click="handleFilterSearch"
                        :loading="articlesLoading"
                        class="filter-action-btn"
                      >
                        <el-icon><Search /></el-icon>
                        查询
                      </el-button>
                    </div>
                    
                    <div class="filter-item filter-item-button">
                      <el-button 
                        @click="handleFilterReset"
                        class="filter-action-btn"
                      >
                        <el-icon><RefreshLeft /></el-icon>
                        重置
                      </el-button>
                    </div>
                    <div class="filter-item filter-item-button">
                      <el-button 
                        @click="handleRefreshMonitor"
                        class="refresh-monitor-btn"
                        type="primary"
                        :loading="refreshing"
                        :disabled="!canRefreshMonitor"
                      >
                        <el-icon><RefreshRight /></el-icon>
                        刷新监测
                      </el-button>
                    </div>
                    <div class="filter-item filter-item-button">
                      <el-button 
           @click="showRssManageDialog"
            class="filter-action-btn"
             type="primary"
 
         >
           <el-icon><Link /></el-icon>
           RSS管理的页面
         </el-button>
                  </div>
                    <div class="filter-item filter-item-button">
                      <el-button 
           @click="loadWechatArticles"
           :loading="articlesLoading"
           class="filter-action-btn"
             type="primary"
         >
           <el-icon><RefreshRight /></el-icon>
           刷新
         </el-button>
                    </div>

                  </div>
                </div>
              </div>
              
              <div class="articles-table-container">
                <el-table
                  :data="wechatArticles"
                  :loading="articlesLoading"
                  style="width: 100%"
                  class="task-table"
                  empty-text="暂无文章数据"
                  v-loading="articlesLoading"
                >
                <el-table-column label="发布时间" width="150">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.pubtime || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.pubtime || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  <!-- <el-table-column prop="created_at" label="创建时间" width="150">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.created_at || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.created_at || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column> -->
                  
                  <el-table-column prop="nick_name" label="公众号名称" width="120">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.nick_name || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.nick_name || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="title" label="标题" min-width="200" class-name="title-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="摘要" min-width="200" class-name="summary-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.summary || scope.row.headline || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis-3">{{ scope.row.summary || scope.row.headline || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="正文" min-width="200" class-name="content-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.content || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis-3">{{ scope.row.content || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="链接" min-width="200">
                    <template #default="scope">
                      <el-link
                        v-if="scope.row.url"
                        :href="scope.row.url"
                        target="_blank"
                        type="primary"
                      >
                        {{ scope.row.url }}
                      </el-link>
                      <span v-else>—</span>
                    </template>
                  </el-table-column>
                  
                 
                  
                  <el-table-column label="数据统计" width="200">
                    <template #default="scope">
                      <div class="stats-info">
                        <div v-if="scope.row.read !== null && scope.row.read !== undefined">
                          <span class="stat-label">阅读:</span>
                          <span class="stat-value">{{ scope.row.read }}</span>
                        </div>
                        <div v-if="scope.row.zan !== null && scope.row.zan !== undefined">
                          <span class="stat-label">点赞:</span>
                          <span class="stat-value">{{ scope.row.zan }}</span>
                        </div>
                        <div v-if="scope.row.share_num !== null && scope.row.share_num !== undefined">
                          <span class="stat-label">分享:</span>
                          <span class="stat-value">{{ scope.row.share_num }}</span>
                        </div>
                      </div>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="博主类型" min-width="150">
                    <template #default="scope">
                      <div v-if="scope.row.keywords && Array.isArray(scope.row.keywords) && scope.row.keywords.length > 0">
                        <el-tag
                          v-for="(keyword, idx) in scope.row.keywords.slice(0, 3)"
                          :key="idx"
                          size="small"
                          :type="keyword === '前端' ? 'primary' : keyword === 'Ai博主' ? 'success' : ''"
                          style="margin-right: 4px; margin-bottom: 4px;"
                        >
                          {{ keyword }}
                        </el-tag>
                        <span v-if="scope.row.keywords.length > 3" class="more-keywords">+{{ scope.row.keywords.length - 3 }}</span>
                      </div>
                      <span v-else>—</span>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="操作" width="200" fixed="right">
                    <template #default="scope">
                      <el-button 
                        size="small" 
                        @click="viewArticleDetail(scope.row)"
                      >
                        <el-icon><View /></el-icon>
                        详情
                      </el-button>
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click="startProduction(scope.row)"
                        style="margin-left: 8px;"
                      >
                        <el-icon><Plus /></el-icon>
                        开始制作
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                
                <!-- 分页 -->
                <div class="pagination-container" v-if="articlesTotal > 0">
                  <el-pagination
                    v-model:current-page="articlesPage"
                    v-model:page-size="articlesPageSize"
                    :page-sizes="[10, 20, 50, 100]"
                    :total="articlesTotal"
                    layout="total, sizes, prev, pager, next, jumper"
                    @size-change="handleArticlesPageSizeChange"
                    @current-change="handleArticlesPageChange"
                  />
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="全部" name="all">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="快手" name="kuaishou">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="抖音" name="douyin">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="视频号" name="channels">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="小红书" name="xiaohongshu">
          <div class="hotspot-list-container">
            <!-- 小红书爬取配置区域 -->
            <div class="xhs-crawl-section">
              <!-- 筛选区域 - 扁平清爽设计 -->
              <div class="filter-section xhs-filter-section">
                <div class="filter-container">
                  <!-- 第一行：配置项 -->
                  <div class="filter-row xhs-filter-row">
                    <div class="filter-item xhs-filter-item">
                      <label class="filter-label xhs-filter-label">选择账号</label>
                      <el-select
                        v-model="xhsCrawlForm.accountId"
                        placeholder="选择账号（可选）"
                        clearable
                        class="xhs-filter-input"
                      >
                        <el-option
                          v-for="account in xhsAccounts"
                          :key="account.id"
                          :label="account.name"
                          :value="account.id"
                        >
                          <div class="xhs-account-option">
                            <span>{{ account.name }}</span>
                            <el-tag size="small" :type="account.status === '正常' ? 'success' : 'danger'">
                              {{ account.status }}
                            </el-tag>
                          </div>
                        </el-option>
                      </el-select>
                      <div class="form-hint xhs-form-hint">选择账号后，将使用该账号的Cookie进行爬取</div>
                    </div>
                    
                    <div class="filter-item xhs-filter-item">
                      <label class="filter-label xhs-filter-label">爬取类型</label>
                      <el-select
                        v-model="xhsCrawlForm.crawlType"
                        placeholder="选择爬取类型"
                        class="xhs-filter-input"
                      >
                        <el-option label="搜索关键词" value="search" />
                        <el-option label="指定笔记ID" value="detail" />
                      </el-select>
                    </div>
                    
                    <div class="filter-item xhs-filter-item" v-if="xhsCrawlForm.crawlType === 'search'">
                      <label class="filter-label xhs-filter-label">搜索关键词</label>
                      <el-input
                        v-model="xhsCrawlForm.keywords"
                        placeholder="每行一个关键词"
                        type="textarea"
                        :rows="3"
                        class="xhs-filter-input xhs-textarea"
                      />
                      <div class="form-hint xhs-form-hint">每行输入一个关键词，支持多个关键词同时搜索</div>
                    </div>
                    
                    <div class="filter-item xhs-filter-item" v-if="xhsCrawlForm.crawlType === 'detail'">
                      <label class="filter-label xhs-filter-label">笔记ID列表</label>
                      <el-input
                        v-model="xhsCrawlForm.noteIds"
                        placeholder="每行一个笔记ID"
                        type="textarea"
                        :rows="3"
                        class="xhs-filter-input xhs-textarea"
                      />
                      <div class="form-hint xhs-form-hint">每行输入一个笔记ID</div>
                    </div>
                    
                    <div class="filter-item xhs-filter-item">
                      <label class="filter-label xhs-filter-label">爬取页数</label>
                      <el-input-number
                        v-model="xhsCrawlForm.pages"
                        :min="1"
                        :max="10"
                        class="xhs-filter-input"
                      />
                      <div class="form-hint xhs-form-hint">设置要爬取的页数（1-10页）</div>
                    </div>
                  </div>
                  
                  <!-- 第二行：按钮 -->
                  <div class="filter-row filter-row-buttons xhs-filter-buttons">
                    <el-button 
                      type="primary" 
                      @click="handleXhsCrawl"
                      :loading="xhsCrawling"
                      class="xhs-action-btn xhs-primary-btn"
                      size="default"
                    >
                      <el-icon><RefreshRight /></el-icon>
                      开始爬取
                    </el-button>
                    
                    <el-button 
                      @click="loadXhsContentList"
                      :loading="xhsContentLoading"
                      class="xhs-action-btn"
                      size="default"
                    >
                      <el-icon><RefreshRight /></el-icon>
                      刷新列表
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- 内容列表 - 扁平清爽设计 -->
              <div class="articles-table-container xhs-table-container">
                <el-table
                  :data="xhsContentList"
                  :loading="xhsContentLoading"
                  style="width: 100%"
                  class="task-table xhs-table"
                  empty-text="暂无内容数据"
                  v-loading="xhsContentLoading"
                >
                  <el-table-column label="发布时间" width="150">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.published_at || scope.row.created_at || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.published_at || scope.row.created_at || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="author" label="作者" width="120">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.author || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.author || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="title" label="标题" min-width="200" class-name="title-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="内容" min-width="200" class-name="content-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.content || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis-3">{{ scope.row.content || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="链接" min-width="200">
                    <template #default="scope">
                      <el-link
                        v-if="scope.row.url"
                        :href="scope.row.url"
                        target="_blank"
                        type="primary"
                      >
                        {{ scope.row.url }}
                      </el-link>
                      <span v-else>—</span>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="标签" min-width="150">
                    <template #default="scope">
                      <div v-if="scope.row.tags && Array.isArray(scope.row.tags) && scope.row.tags.length > 0">
                        <el-tag
                          v-for="(tag, idx) in scope.row.tags.slice(0, 3)"
                          :key="idx"
                          size="small"
                          style="margin-right: 4px; margin-bottom: 4px;"
                        >
                          {{ tag }}
                        </el-tag>
                        <span v-if="scope.row.tags.length > 3" class="more-keywords">+{{ scope.row.tags.length - 3 }}</span>
                      </div>
                      <span v-else>—</span>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="操作" width="100" fixed="right">
                    <template #default="scope">
                      <el-button 
                        type="primary" 
                        size="small"
                        @click="viewXhsContentDetail(scope.row)"
                      >
                        查看详情
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                
                <!-- 分页 -->
                <div class="pagination-container" v-if="xhsContentTotal > 0">
                  <el-pagination
                    v-model:current-page="xhsContentPage"
                    v-model:page-size="xhsContentPageSize"
                    :page-sizes="[10, 20, 50, 100]"
                    :total="xhsContentTotal"
                    layout="total, sizes, prev, pager, next, jumper"
                    @size-change="handleXhsContentPageSizeChange"
                    @current-change="handleXhsContentPageChange"
                  />
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="X" name="x">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Facebook" name="facebook">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Instagram" name="instagram">
          <div class="hotspot-list-container">
            <!-- Tab内容清空 -->
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Reddit" name="reddit">
          <div class="hotspot-list-container">
            <!-- Reddit内容区域 -->
            <div class="reddit-section">
              <!-- 筛选区域 -->
              <div class="filter-section">
                <div class="filter-container">
                  <!-- 第一行：筛选项（水平布局） -->
                  <div class="filter-row">
                    <div class="filter-item filter-item-checkbox">
                      <label class="filter-label">频道名称</label>
                      <el-checkbox-group 
                        v-model="redditFilterForm.selectedChannels"
                        class="account-checkbox-group"
                      >
                        <el-checkbox 
                          v-for="rss in redditRssListFromStorage" 
                          :key="rss.channelName"
                          :label="rss.channelName"
                          class="account-checkbox"
                        >
                          {{ rss.channelName }}
                        </el-checkbox>
                      </el-checkbox-group>
                      <div v-if="redditRssListFromStorage.length === 0" class="no-rss-tip">
                        暂无RSS配置，请点击"RSS配置"按钮添加
                      </div>
                    </div>
                    
                    <div class="filter-item">
                      <label class="filter-label">标题</label>
                      <el-input
                        v-model="redditFilterForm.title"
                        placeholder="请输入标题关键词"
                        clearable
                        class="filter-input"
                      />
                    </div>
                    
                    <div class="filter-item">
                      <label class="filter-label">发布时间</label>
                      <el-date-picker
                        v-model="redditFilterForm.pubtimeRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        class="filter-date-picker"
                      />
                    </div>
                  </div>
                  
                  <!-- 第二行：按钮（水平布局） -->
                  <div class="filter-row filter-row-buttons">
                    <div class="filter-item filter-item-button">
                      <el-button 
                        type="primary" 
                        @click="handleRedditFilterSearch"
                        :loading="redditArticlesLoading"
                        class="filter-action-btn"
                      >
                        <el-icon><Search /></el-icon>
                        查询
                      </el-button>
                    </div>
                    
                    <div class="filter-item filter-item-button">
                      <el-button 
                        @click="handleRedditFilterReset"
                        class="filter-action-btn"
                      >
                        <el-icon><RefreshLeft /></el-icon>
                        重置
                      </el-button>
                    </div>
                    
                    <div class="filter-item filter-item-button">
                      <el-button 
                        @click="showRedditRssManageDialog"
                        class="filter-action-btn"
                        type="primary"
                      >
                        <el-icon><Link /></el-icon>
                        RSS配置
                      </el-button>
                    </div>
                    
                    <div class="filter-item filter-item-button">
                      <el-button 
                        @click="loadRedditArticles"
                        :loading="redditArticlesLoading"
                        class="filter-action-btn"
                        type="primary"
                      >
                        <el-icon><RefreshRight /></el-icon>
                        刷新
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Reddit文章列表 -->
              <div class="articles-table-container">
                <el-table
                  :data="redditArticles"
                  :loading="redditArticlesLoading"
                  style="width: 100%"
                  class="task-table"
                  empty-text="暂无文章数据"
                  v-loading="redditArticlesLoading"
                >
                  <el-table-column label="发布时间" width="150">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.pubtime || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.pubtime || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="channel_name" label="频道名称" width="120">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.channel_name || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.channel_name || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="title" label="标题" min-width="200" class-name="title-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="摘要" min-width="200" class-name="summary-column">
                    <template #default="scope">
                      <el-tooltip :content="scope.row.summary || scope.row.content || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                        <div class="text-ellipsis-3">{{ scope.row.summary || scope.row.content || '—' }}</div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="链接" min-width="200">
                    <template #default="scope">
                      <el-link
                        v-if="scope.row.url"
                        :href="scope.row.url"
                        target="_blank"
                        type="primary"
                      >
                        {{ scope.row.url }}
                      </el-link>
                      <span v-else>—</span>
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="操作" width="100" fixed="right">
                    <template #default="scope">
                      <el-button 
                        type="primary" 
                        size="small"
                        @click="handleViewRedditArticleDetail(scope.row)"
                      >
                        查看详情
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 刷新监测配置弹框（包含添加监测号主功能） -->
    <el-dialog
      v-model="refreshMonitorDialogVisible"
      title="刷新监测配置"
      width="700px"
      :close-on-click-modal="false"
      append-to-body
    >
      <div class="refresh-monitor-form">
        <!-- 添加监测号主区域 -->
        <div class="add-account-section">
          <h4 class="section-title">
            <el-icon><Plus /></el-icon>
            添加监测号主
          </h4>
          <el-form :model="accountForm" label-width="100px" class="add-account-form-inline">
            <div class="form-row">
              <el-form-item label="Name" required class="form-item-inline">
                <el-input
                  v-model="accountForm.name"
                  placeholder="请输入号主名称"
                  clearable
                  style="width: 200px"
                />
              </el-form-item>
              <el-form-item label="Biz" required class="form-item-inline">
                <el-input
                  v-model="accountForm.biz"
                  placeholder="请输入号主的biz"
                  clearable
                  style="width: 200px"
                />
              </el-form-item>
              <el-form-item class="form-item-inline">
                <el-button 
                  type="primary" 
                  @click="confirmAddAccount"
                  :loading="addingAccount"
                  size="default"
                >
                  <el-icon><Plus /></el-icon>
                  添加
                </el-button>
              </el-form-item>
            </div>
            <div class="form-tip">
              填写Name和Biz后点击"添加"按钮添加监测号主
            </div>
          </el-form>
        </div>
        
        <el-divider />
        
        <!-- 刷新监测配置区域 -->
        <div class="refresh-config-section">
          <h4 class="section-title">
            <el-icon><RefreshRight /></el-icon>
            刷新监测配置
          </h4>
          <el-form :model="refreshMonitorForm" label-width="120px">
            <!-- 选项一：监控的公众号（多选） -->
            <el-form-item label="监控的公众号" required>
            <el-checkbox-group v-model="refreshMonitorForm.selectedAccounts">
              <div class="account-checkbox-list">
                <el-checkbox 
                  v-for="account in monitorAccounts" 
                  :key="account.id"
                  :label="account.id"
                  class="account-checkbox-item"
                >
                  <div class="checkbox-account-info">
                    <span class="account-name">{{ account.account_name || account.media_id }}</span>
                    <span class="account-media-id">({{ account.media_id }})</span>
                  </div>
                </el-checkbox>
              </div>
            </el-checkbox-group>
            <div class="form-tip">
              请选择要监控的公众号号主（可多选）
            </div>
          </el-form-item>
          
          <!-- 选项二：生成文章的个数 -->
          <el-form-item label="生成文章的个数" required>
            <el-input-number
              v-model="refreshMonitorForm.articleCount"
              :min="1"
              :max="100"
              :precision="0"
              placeholder="请输入生成文章的个数"
              style="width: 100%"
            />
            <div class="form-tip">
              请输入要生成的文章数量（1-100）
            </div>
          </el-form-item>
          
          <!-- 选项三：开始日期 -->
          <el-form-item label="开始日期" required>
            <el-date-picker
              v-model="refreshMonitorForm.startDate"
              type="date"
              placeholder="请选择开始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
            <div class="form-tip">
              请选择监测的开始日期
            </div>
          </el-form-item>
        </el-form>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="refreshMonitorDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmRefreshMonitor"
            :loading="refreshing"
            :disabled="!canSubmitRefreshMonitor"
          >
            确定并刷新监测
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- RSS管理弹框 -->
    <el-dialog
      v-model="rssManageDialogVisible"
      title="RSS管理"
      width="800px"
      :close-on-click-modal="false"
      append-to-body
    >
      <div class="rss-manage-content">
        <!-- 添加区域 -->
        <div class="rss-add-section">
          <div class="add-form-row">
            <div class="form-item">
              <label class="form-label">公众号名称</label>
          <el-input
                v-model="rssManageForm.accountName"
                placeholder="请输入公众号名称"
                clearable
                class="form-input"
          />
        </div>
            <div class="form-item">
              <label class="form-label">RSS链接</label>
              <el-input
                v-model="rssManageForm.rssLink"
                placeholder="请输入RSS链接"
                clearable
                class="form-input"
              />
      </div>
            <div class="form-item">
              <label class="form-label">公众号类型</label>
              <el-select
                v-model="rssManageForm.accountType"
                placeholder="请选择类型"
                class="form-input"
                clearable
              >
                <el-option label="前端" value="前端" />
                <el-option label="Ai博主" value="Ai博主" />
              </el-select>
            </div>
            <div class="form-item form-item-button">
          <el-button 
                type="primary" 
                @click="handleAddRssItem"
                :disabled="!canAddRssItem"
          >
                <el-icon><Plus /></el-icon>
                添加
          </el-button>
            </div>
          </div>
        </div>
        
        <!-- 恢复功能 -->
        <div class="rss-recover-section">
          <el-button 
            type="success" 
            plain
            @click="recoverRssFromArticles"
            :loading="recoveringRss"
          >
            <el-icon><RefreshLeft /></el-icon>
            从已保存的文章恢复公众号列表
          </el-button>
          <div class="recover-tip">
            从数据库中已保存的文章提取公众号名称和类型，自动填充到列表中（需要手动补充RSS链接）
          </div>
        </div>
        
        <!-- 列表区域 -->
        <div class="rss-list-section">
          <el-table
            :data="rssList"
            style="width: 100%"
            empty-text="暂无RSS数据"
          >
            <el-table-column prop="accountName" label="公众号名称" min-width="200" />
            <el-table-column prop="rssLink" label="RSS链接" min-width="400">
              <template #default="scope">
                <el-link
                  :href="scope.row.rssLink"
                  target="_blank"
            type="primary" 
                >
                  {{ scope.row.rssLink }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="accountType" label="公众号类型" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.accountType" :type="scope.row.accountType === '前端' ? 'primary' : 'success'">
                  {{ scope.row.accountType }}
                </el-tag>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button 
                  type="danger" 
                  size="small"
                  @click="handleDeleteRssItem(scope.$index)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
          </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="rssManageDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- Reddit RSS管理弹框 -->
    <el-dialog
      v-model="redditRssManageDialogVisible"
      title="Reddit RSS管理"
      width="800px"
      :close-on-click-modal="false"
      append-to-body
    >
      <div class="rss-manage-content">
        <!-- 添加区域 -->
        <div class="rss-add-section">
          <div class="add-form-row">
            <div class="form-item">
              <label class="form-label">频道名称</label>
              <el-input
                v-model="redditRssManageForm.channelName"
                placeholder="请输入频道名称"
                clearable
                class="form-input"
              />
            </div>
            <div class="form-item">
              <label class="form-label">RSS链接</label>
              <el-input
                v-model="redditRssManageForm.rssLink"
                placeholder="请输入RSS链接"
                clearable
                class="form-input"
              />
            </div>
            <div class="form-item form-item-button">
          <el-button 
                type="primary" 
                @click="handleAddRedditRssItem"
                :disabled="!canAddRedditRssItem"
          >
                <el-icon><Plus /></el-icon>
                添加
          </el-button>
            </div>
          </div>
        </div>
        
        <!-- 列表区域 -->
        <div class="rss-list-section">
          <el-table
            :data="redditRssList"
            style="width: 100%"
            empty-text="暂无RSS数据"
          >
            <el-table-column prop="channelName" label="频道名称" min-width="200" />
            <el-table-column prop="rssLink" label="RSS链接" min-width="400">
              <template #default="scope">
                <el-link
                  :href="scope.row.rssLink"
                  target="_blank"
            type="primary" 
                >
                  {{ scope.row.rssLink }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button 
                  type="danger" 
                  size="small"
                  @click="handleDeleteRedditRssItem(scope.$index)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
          </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="redditRssManageDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 文章详情弹框 -->
    <el-dialog
      v-model="articleDetailDialogVisible"
      title="文章详情"
      width="800px"
      :close-on-click-modal="false"
      append-to-body
    >
      <div v-if="currentArticle" class="article-detail">
        <div class="detail-meta">
          <div><strong>name:</strong> {{ currentArticle.nick_name || '—' }}</div>
          <div><strong>pubDate:</strong> {{ currentArticle.pubtime || '—' }}</div>
          <div><strong>创建时间:</strong> {{ currentArticle.created_at || '—' }}</div>
        </div>
        
        <div class="detail-block">
          <h4>title</h4>
          <p>{{ currentArticle.title || '—' }}</p>
        </div>
        
        <div class="detail-block" v-if="currentArticle.headline">
          <h4>标题</h4>
          <p>{{ currentArticle.headline }}</p>
        </div>
        
        <div class="detail-block" v-if="currentArticle.summary">
          <h4>摘要</h4>
          <p>{{ currentArticle.summary }}</p>
        </div>
        
        <div class="detail-block" v-if="currentArticle.content">
          <h4>正文</h4>
          <div class="detail-content">{{ currentArticle.content }}</div>
        </div>
        
        <div class="detail-block" v-if="currentArticle.keywords && Array.isArray(currentArticle.keywords) && currentArticle.keywords.length > 0">
          <h4>关键词</h4>
          <div class="keywords-list">
            <el-tag
              v-for="(keyword, idx) in currentArticle.keywords"
              :key="idx"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ keyword }}
            </el-tag>
          </div>
        </div>
        
        <div class="detail-block">
          <h4>数据统计</h4>
          <div class="stats-grid">
            <div v-if="currentArticle.read !== null && currentArticle.read !== undefined">
              <span class="stat-label">阅读:</span>
              <span class="stat-value">{{ currentArticle.read }}</span>
            </div>
            <div v-if="currentArticle.zan !== null && currentArticle.zan !== undefined">
              <span class="stat-label">点赞:</span>
              <span class="stat-value">{{ currentArticle.zan }}</span>
            </div>
            <div v-if="currentArticle.looking !== null && currentArticle.looking !== undefined">
              <span class="stat-label">在看:</span>
              <span class="stat-value">{{ currentArticle.looking }}</span>
            </div>
            <div v-if="currentArticle.share_num !== null && currentArticle.share_num !== undefined">
              <span class="stat-label">分享:</span>
              <span class="stat-value">{{ currentArticle.share_num }}</span>
            </div>
            <div v-if="currentArticle.collect_num !== null && currentArticle.collect_num !== undefined">
              <span class="stat-label">收藏:</span>
              <span class="stat-value">{{ currentArticle.collect_num }}</span>
            </div>
            <div v-if="currentArticle.comment_count !== null && currentArticle.comment_count !== undefined">
              <span class="stat-label">评论:</span>
              <span class="stat-value">{{ currentArticle.comment_count }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-block" v-if="currentArticle.url">
          <h4>link</h4>
          <el-link :href="currentArticle.url" target="_blank" type="primary">
            {{ currentArticle.url }}
          </el-link>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="articleDetailDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 制作类型选择弹窗 -->
    <el-dialog
      v-model="productionTypeDialogVisible"
      width="1200px"
      class="content-type-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <template #header>
        <div class="dialog-header-custom">
          <h2 v-if="productionDialogStep === 'select'">选择制作类型</h2>
          <h2 v-else>配置{{ getProductionContentTypeLabel(selectedProductionType) }}任务</h2>
        </div>
      </template>
      
      <!-- 步骤1: 选择内容类型 -->
      <div v-if="productionDialogStep === 'select'" class="content-type-selection">
        <div class="type-cards">
          <div 
            v-for="type in productionContentTypes" 
            :key="type.value"
            :class="['type-card', { selected: selectedProductionType === type.value }]"
            @click="selectedProductionType = type.value"
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
            <div class="type-card-check" v-if="selectedProductionType === type.value">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 步骤2: 跳转到制作中心提示（已移除，直接跳转） -->
      
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button @click="handleProductionDialogCancel" size="large">取消</el-button>
          <el-button 
            v-if="productionDialogStep === 'select'"
            type="primary" 
            @click="goToProductionConfigStep" 
            size="large"
            :disabled="!selectedProductionType"
          >
            下一步&gt;
          </el-button>
          <el-button 
            v-else
            type="primary" 
            @click="goToProductionCenter" 
            size="large"
          >
            跳转到制作中心
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, RefreshRight, User, Delete, View, Search, RefreshLeft, Link, VideoCamera, Picture, Document, Check, CircleCheckFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/account'
import { accountApi } from '@/api/account'

// API base URL - 使用统一的工具函数
import { resolveApiBaseUrl } from '@/utils/apiConfig'

// RSS Content Aggregator API URL
const RSS_AGGREGATOR_API_URL = 'http://150.107.38.113:5410'

const router = useRouter()
const accountStore = useAccountStore()

const apiBaseUrl = resolveApiBaseUrl()
console.log('[HotspotCenter] 初始化完成，apiBaseUrl =', apiBaseUrl)

/**
 * 当前激活的标签页（默认显示公众号）
 */
const activeTab = ref('wechat')

/**
 * 监测号主列表
 */
const monitorAccounts = ref([])


/**
 * 添加号主表单数据
 */
const accountForm = ref({
  name: '',
  biz: ''
})

/**
 * 添加号主加载状态
 */
const addingAccount = ref(false)

/**
 * 刷新监测加载状态
 */
const refreshing = ref(false)

/**
 * 刷新监测配置弹框显示状态
 */
const refreshMonitorDialogVisible = ref(false)

/**
 * 刷新监测配置表单数据
 */
const refreshMonitorForm = ref({
  selectedAccounts: [], // 选中的公众号ID列表
  articleCount: 1, // 生成文章的个数
  startDate: '' // 开始日期
})

/**
 * 刷新监测的n8n webhook URL
 */
const REFRESH_MONITOR_WEBHOOK_URL = 'https://aicode.ltd/webhook/3278f17d-be63-4489-a0ce-769723bd7c15'

/**
 * RSS列表刷新监测的webhook URL
 */
const RSS_LIST_WEBHOOK_URL = 'https://aicode.ltd/webhook/rss-list'

/**
 * 公众号文章列表相关
 */
const wechatArticles = ref([])
const articlesLoading = ref(false)
const articlesPage = ref(1)
const articlesPageSize = ref(20)
const articlesTotal = ref(0)
const articleDetailDialogVisible = ref(false)
const currentArticle = ref(null)

/**
 * RSS管理相关
 */
const rssManageDialogVisible = ref(false)
const rssManageForm = ref({
  accountName: '',
  rssLink: '',
  accountType: '' // 公众号类型：前端 或 Ai博主
})
const rssList = ref([])

/**
 * Reddit相关
 */
const redditArticles = ref([])
const redditArticlesLoading = ref(false)
const redditFilterForm = ref({
  selectedChannels: [], // 选中的频道名称列表
  title: '',
  pubtimeRange: null
})

/**
 * Reddit RSS管理相关
 */
const redditRssManageDialogVisible = ref(false)
const redditRssManageForm = ref({
  channelName: '',
  rssLink: ''
})
const redditRssList = ref([])

/**
 * 检查是否可以添加RSS项
 */
const canAddRssItem = computed(() => {
  return rssManageForm.value.accountName?.trim() && 
         rssManageForm.value.rssLink?.trim() && 
         rssManageForm.value.accountType
})

/**
 * 检查是否可以添加Reddit RSS项
 */
const canAddRedditRssItem = computed(() => {
  return redditRssManageForm.value.channelName?.trim() && 
         redditRssManageForm.value.rssLink?.trim()
})

/**
 * 显示RSS管理弹框
 */
const showRssManageDialog = () => {
  // 从localStorage加载数据
  loadRssListFromStorage()
  // 重置表单
  rssManageForm.value.accountName = ''
  rssManageForm.value.rssLink = ''
  rssManageForm.value.accountType = ''
  rssManageDialogVisible.value = true
}

/**
 * Reddit RSS列表（从localStorage计算）
 */
const redditRssListFromStorage = computed(() => {
  try {
    const saved = localStorage.getItem('reddit_rss_list')
    if (saved) {
      return JSON.parse(saved)
    }
    return []
  } catch (error) {
    console.error('加载Reddit RSS列表失败:', error)
    return []
  }
})

/**
 * 从localStorage加载RSS列表
 */
const loadRssListFromStorage = () => {
  try {
    const saved = localStorage.getItem('wechat_rss_list')
    if (saved) {
      rssList.value = JSON.parse(saved)
    } else {
      rssList.value = []
    }
  } catch (error) {
    console.error('加载RSS列表失败:', error)
    rssList.value = []
  }
}

/**
 * 保存RSS列表到localStorage
 */
const saveRssListToStorage = () => {
  try {
    localStorage.setItem('wechat_rss_list', JSON.stringify(rssList.value))
  } catch (error) {
    console.error('保存RSS列表失败:', error)
  }
}

/**
 * 处理添加RSS项
 */
const handleAddRssItem = () => {
  const accountName = rssManageForm.value.accountName?.trim()
  const rssLink = rssManageForm.value.rssLink?.trim()
  const accountType = rssManageForm.value.accountType
  
  if (!accountName) {
    ElMessage.warning('请输入公众号名称')
    return
  }
  
  if (!rssLink) {
    ElMessage.warning('请输入RSS链接')
    return
  }
  
  if (!accountType) {
    ElMessage.warning('请选择公众号类型')
    return
  }
  
  // 简单验证URL格式
  try {
    new URL(rssLink)
  } catch (e) {
    ElMessage.warning('请输入有效的RSS链接')
    return
  }
  
  // 添加到列表
  rssList.value.push({
    accountName: accountName,
    rssLink: rssLink,
    accountType: accountType
  })
  
  // 保存到localStorage
  saveRssListToStorage()
  
  // 同步更新筛选选项
  loadRssListForFilter()
  
  // 清空表单
  rssManageForm.value.accountName = ''
  rssManageForm.value.rssLink = ''
  rssManageForm.value.accountType = ''
  
  ElMessage.success('添加成功')
}

/**
 * 处理删除RSS项
 */
const handleDeleteRssItem = (index) => {
  rssList.value.splice(index, 1)
  saveRssListToStorage()
  ElMessage.success('删除成功')
}

/**
 * 恢复RSS列表状态
 */
const recoveringRss = ref(false)

/**
 * 从已保存的文章恢复RSS列表
 */
const recoverRssFromArticles = async () => {
  recoveringRss.value = true
  try {
    // 从后端获取所有文章，提取唯一的公众号名称和类型
    const response = await fetch(`${apiBaseUrl}/hotspot/wechat/articles?page=1&page_size=1000`)
    const result = await response.json()
    
    if (result.code === 200 && result.data?.items) {
      const articles = result.data.items
      const accountMap = new Map()
      
      // 提取唯一的公众号名称和类型
      articles.forEach(article => {
        const nickName = article.nick_name
        if (nickName) {
          // 解析keywords获取类型
          let accountType = ''
          if (article.keywords) {
            try {
              const keywords = typeof article.keywords === 'string' 
                ? JSON.parse(article.keywords) 
                : article.keywords
              if (Array.isArray(keywords) && keywords.length > 0) {
                // 优先使用包含"前端"或"Ai博主"的关键词
                if (keywords.includes('前端')) {
                  accountType = '前端'
                } else if (keywords.includes('Ai博主')) {
                  accountType = 'Ai博主'
                } else {
                  accountType = keywords[0] // 使用第一个关键词
                }
              }
            } catch (e) {
              // 如果不是JSON，直接使用字符串
              if (article.keywords.includes('前端')) {
                accountType = '前端'
              } else if (article.keywords.includes('Ai博主')) {
                accountType = 'Ai博主'
              }
            }
          }
          
          // 如果这个公众号还没有在map中，或者新文章的类型更明确，则更新
          if (!accountMap.has(nickName) || (!accountMap.get(nickName).accountType && accountType)) {
            accountMap.set(nickName, {
              accountName: nickName,
              accountType: accountType || '前端', // 默认类型
              rssLink: '' // RSS链接需要用户手动补充
            })
          }
        }
      })
      
      // 将提取的公众号信息添加到现有列表（不重复）
      let newCount = 0
      accountMap.forEach((accountInfo, nickName) => {
        const exists = rssList.value.some(item => item.accountName === nickName)
        if (!exists) {
          rssList.value.push(accountInfo)
          newCount++
        }
      })
      
      // 保存到localStorage
      saveRssListToStorage()
      
      // 同步更新筛选选项
      loadRssListForFilter()
      
      const totalRecovered = Array.from(accountMap.keys()).length
      
      if (newCount > 0) {
        ElMessage.success(`成功恢复 ${newCount} 个公众号信息（共 ${totalRecovered} 个），请手动补充RSS链接`)
      } else {
        ElMessage.info(`找到 ${totalRecovered} 个公众号，但都已存在于列表中`)
      }
    } else {
      ElMessage.warning('未找到已保存的文章数据')
    }
  } catch (error) {
    console.error('恢复RSS列表失败:', error)
    ElMessage.error('恢复失败，请稍后重试')
  } finally {
    recoveringRss.value = false
  }
}

/**
 * Reddit RSS管理相关方法
 */
const showRedditRssManageDialog = () => {
  // 从localStorage加载数据
  loadRedditRssListFromStorage()
  // 重置表单
  redditRssManageForm.value.channelName = ''
  redditRssManageForm.value.rssLink = ''
  redditRssManageDialogVisible.value = true
}

/**
 * 从localStorage加载Reddit RSS列表
 */
const loadRedditRssListFromStorage = () => {
  try {
    const saved = localStorage.getItem('reddit_rss_list')
    if (saved) {
      redditRssList.value = JSON.parse(saved)
    } else {
      redditRssList.value = []
    }
  } catch (error) {
    console.error('加载Reddit RSS列表失败:', error)
    redditRssList.value = []
  }
}

/**
 * 保存Reddit RSS列表到localStorage
 */
const saveRedditRssListToStorage = () => {
  try {
    localStorage.setItem('reddit_rss_list', JSON.stringify(redditRssList.value))
  } catch (error) {
    console.error('保存Reddit RSS列表失败:', error)
  }
}

/**
 * 处理添加Reddit RSS项
 */
const handleAddRedditRssItem = () => {
  const channelName = redditRssManageForm.value.channelName?.trim()
  const rssLink = redditRssManageForm.value.rssLink?.trim()
  
  if (!channelName) {
    ElMessage.warning('请输入频道名称')
    return
  }
  
  if (!rssLink) {
    ElMessage.warning('请输入RSS链接')
    return
  }
  
  // 检查是否已存在
  if (redditRssList.value.some(item => item.channelName === channelName)) {
    ElMessage.warning('该频道名称已存在')
    return
  }
  
  // 添加到列表
  redditRssList.value.push({
    channelName: channelName,
    rssLink: rssLink
  })
  
  // 保存到localStorage
  saveRedditRssListToStorage()
  
  // 清空表单
  redditRssManageForm.value.channelName = ''
  redditRssManageForm.value.rssLink = ''
  
  ElMessage.success('添加成功')
}

/**
 * 处理删除Reddit RSS项
 */
const handleDeleteRedditRssItem = (index) => {
  redditRssList.value.splice(index, 1)
  saveRedditRssListToStorage()
  ElMessage.success('删除成功')
}

/**
 * Reddit文章列表相关方法
 */
const loadRedditArticles = async () => {
  redditArticlesLoading.value = true
  try {
    // TODO: 实现Reddit文章列表加载逻辑
    // 这里暂时使用空数组，后续可以根据实际API实现
    redditArticles.value = []
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('加载Reddit文章列表失败:', error)
    ElMessage.error('加载失败，请稍后重试')
  } finally {
    redditArticlesLoading.value = false
  }
}

/**
 * 处理Reddit筛选查询
 */
const handleRedditFilterSearch = () => {
  loadRedditArticles()
}

/**
 * 处理Reddit筛选重置
 */
const handleRedditFilterReset = () => {
  redditFilterForm.value = {
    selectedChannels: [],
    title: '',
    pubtimeRange: null
  }
  loadRedditArticles()
}

/**
 * 查看Reddit文章详情
 */
const handleViewRedditArticleDetail = (article) => {
  currentArticle.value = article
  articleDetailDialogVisible.value = true
}

/**
 * 筛选表单
 */
const filterForm = ref({
  createTimeRange: [], // 创建时间范围，空数组表示不筛选
  selectedAccounts: [], // 选中的公众号名称（从RSS列表）
  title: '', // 标题关键词
  pubtimeRange: [] // 发布时间范围，空数组表示不筛选
})

/**
 * RSS列表（从localStorage加载，用于筛选选项）
 */
const rssListFromStorage = computed(() => {
  try {
    const saved = localStorage.getItem('wechat_rss_list')
    if (saved) {
      return JSON.parse(saved)
    }
    return []
  } catch (error) {
    console.error('加载RSS列表失败:', error)
    return []
  }
})

/**
 * 刷新监测类型
 */
const refreshMonitorType = ref('前端')

/**
 * 初始化筛选表单（不设置默认日期范围，显示所有数据）
 */
const initFilterForm = () => {
  filterForm.value = {
    createTimeRange: [], // 不设置默认日期范围，显示所有数据
    selectedAccounts: [],
    title: '',
    pubtimeRange: [] // 不设置默认日期范围，显示所有数据
  }
}

/**
 * 显示刷新监测配置弹框（包含添加号主功能）
 */
const showRefreshMonitorDialog = () => {
  // 初始化添加号主表单
  accountForm.value.name = ''
  accountForm.value.biz = ''
  
  // 初始化刷新监测表单
  if (monitorAccounts.value.length === 0) {
    ElMessage.warning('请先添加监测号主')
    // 如果没有号主，仍然打开弹框让用户先添加
  }
  
  // 初始化表单：默认选中所有账号
  refreshMonitorForm.value = {
    selectedAccounts: monitorAccounts.value.map(account => account.id),
    articleCount: 1,
    startDate: ''
  }
  
  refreshMonitorDialogVisible.value = true
}

/**
 * 确认添加号主
 */
const confirmAddAccount = async () => {
  const name = accountForm.value.name?.trim()
  const biz = accountForm.value.biz?.trim()
  
  if (!name) {
    ElMessage.warning('请输入号主名称')
    return
  }
  
  if (!biz) {
    ElMessage.warning('请输入biz')
    return
  }
  
  addingAccount.value = true
  try {
    const requestUrl = `${apiBaseUrl}/hotspot/wechat/accounts`
    console.log('[HotspotCenter] 发送POST请求到:', requestUrl)
    console.log('[HotspotCenter] apiBaseUrl值:', apiBaseUrl)
    console.log('[HotspotCenter] 完整URL:', requestUrl)
    
    const response = await fetch(requestUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: name,
        biz: biz
      })
    })
    
    console.log('[HotspotCenter] 响应状态码:', response.status)
    console.log('[HotspotCenter] 响应URL:', response.url)
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('添加成功')
      // 清空表单
      accountForm.value.name = ''
      accountForm.value.biz = ''
      // 刷新列表
      await loadMonitorAccounts()
      // 更新刷新监测表单中的选中项（包含新添加的账号）
      refreshMonitorForm.value.selectedAccounts = monitorAccounts.value.map(account => account.id)
    } else {
      ElMessage.error(result.msg || '添加失败')
    }
  } catch (error) {
    console.error('添加监测号主失败:', error)
    ElMessage.error('添加失败，请稍后重试')
  } finally {
    addingAccount.value = false
  }
}

/**
 * 删除号主
 */
const deleteAccount = async (accountId) => {
  try {
    await ElMessageBox.confirm('确认删除该监测号主吗？', '删除确认', {
      type: 'warning'
    })
    
    const response = await fetch(`${apiBaseUrl}/hotspot/wechat/accounts/${accountId}`, {
      method: 'DELETE'
    })
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('删除成功')
      // 刷新列表
      await loadMonitorAccounts()
    } else {
      ElMessage.error(result.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除监测号主失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

/**
 * 加载监测号主列表
 */
const loadMonitorAccounts = async () => {
  try {
    const response = await fetch(`${apiBaseUrl}/hotspot/wechat/accounts`)
    const result = await response.json()
    
    if (result.code === 200) {
      monitorAccounts.value = result.data?.items || []
    } else {
      console.error('获取监测号主列表失败:', result.msg)
    }
  } catch (error) {
    console.error('获取监测号主列表失败:', error)
  }
}


/**
 * 计算是否可以提交刷新监测配置
 */
const canSubmitRefreshMonitor = computed(() => {
  return (
    refreshMonitorForm.value.selectedAccounts.length > 0 &&
    refreshMonitorForm.value.articleCount > 0 &&
    refreshMonitorForm.value.startDate !== ''
  )
})

/**
 * 确认刷新监测（旧版本，保留用于兼容）
 */
const confirmRefreshMonitor = async () => {
  // 验证表单
  if (refreshMonitorForm.value.selectedAccounts.length === 0) {
    ElMessage.warning('请至少选择一个监控的公众号')
    return
  }
  
  if (!refreshMonitorForm.value.articleCount || refreshMonitorForm.value.articleCount < 1) {
    ElMessage.warning('请输入有效的文章个数')
    return
  }
  
  if (!refreshMonitorForm.value.startDate) {
    ElMessage.warning('请选择开始日期')
    return
  }
  
  refreshing.value = true
  try {
    // 根据选中的账号ID，获取对应的账号信息，转换为包含name和biz的对象数组
    const selectedAccounts = monitorAccounts.value
      .filter(account => refreshMonitorForm.value.selectedAccounts.includes(account.id))
      .map(account => ({
        name: account.account_name || account.media_id,
        biz: account.media_id
      }))
    
    // 构建请求数据
    const requestData = {
      media_ids: selectedAccounts,
      article_count: refreshMonitorForm.value.articleCount,
      start_date: refreshMonitorForm.value.startDate
    }
    
    console.log('[HotspotCenter] 发送刷新监测请求:', requestData)
    
    const response = await fetch(REFRESH_MONITOR_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const result = await response.json().catch(() => ({}))
    
    ElMessage.success('刷新监测请求已发送')
    console.log('刷新监测响应:', result)
    
    // 关闭弹框
    refreshMonitorDialogVisible.value = false
  } catch (error) {
    console.error('刷新监测失败:', error)
    ElMessage.error('刷新监测失败，请稍后重试')
  } finally {
    refreshing.value = false
  }
}

/**
 * 检查是否可以刷新监测
 */
const canRefreshMonitor = computed(() => {
  return filterForm.value.selectedAccounts.length > 0 && refreshMonitorType.value
})

/**
 * 处理刷新监测（新版本，直接调用RSS列表API）
 */
const handleRefreshMonitor = async () => {
  // 验证表单
  if (filterForm.value.selectedAccounts.length === 0) {
    ElMessage.warning('请至少选择一个公众号')
    return
  }
  
  if (!refreshMonitorType.value) {
    ElMessage.warning('请选择类型')
    return
  }
  
  refreshing.value = true
  try {
    // 根据选中的公众号名称，从RSS列表中查找对应的RSS链接和类型
    const requestData = filterForm.value.selectedAccounts.map(accountName => {
      const rssItem = rssListFromStorage.value.find(item => item.accountName === accountName)
      return {
        name: accountName,
        rss_url: rssItem ? rssItem.rssLink : '',
        type: rssItem && rssItem.accountType ? rssItem.accountType : refreshMonitorType.value
      }
    })
    
    console.log('[HotspotCenter] 发送RSS列表刷新请求:', requestData)
    
    const response = await fetch(RSS_LIST_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`)
    }
    
    const result = await response.json().catch(() => ({}))
    
    ElMessage.success('刷新监测请求已发送')
    console.log('刷新监测响应:', result)
  } catch (error) {
    console.error('刷新监测失败:', error)
    ElMessage.error(error.message || '刷新监测失败，请稍后重试')
  } finally {
    refreshing.value = false
  }
}

/**
 * 加载RSS列表到筛选选项（已废弃，使用computed自动更新）
 */
const loadRssListForFilter = () => {
  // 由于rssListFromStorage已经是computed，这里不需要手动更新
  // 保留此函数用于兼容性
}

/**
 * 小红书爬取相关
 */
const xhsCrawlForm = ref({
  accountId: null, // 选中的账号ID
  crawlType: 'search', // 爬取类型：search 或 detail
  keywords: '', // 关键词（每行一个）
  noteIds: '', // 笔记ID列表（每行一个）
  pages: 1 // 爬取页数
})

const xhsCrawling = ref(false)
const xhsContentList = ref([])
const xhsContentLoading = ref(false)
const xhsContentPage = ref(1)
const xhsContentPageSize = ref(20)
const xhsContentTotal = ref(0)

/**
 * 小红书账号列表（从账号管理获取）
 */
const xhsAccounts = computed(() => {
  return accountStore.accounts.filter(acc => acc.platform === '小红书')
})

/**
 * 加载小红书账号列表
 */
const loadXhsAccounts = async () => {
  try {
    const response = await accountApi.getAccounts()
    if (response.code === 200) {
      accountStore.setAccounts(response.data || [])
    }
  } catch (error) {
    console.error('加载小红书账号失败:', error)
  }
}

/**
 * 处理小红书爬取
 */
const handleXhsCrawl = async () => {
  if (xhsCrawlForm.value.crawlType === 'search' && !xhsCrawlForm.value.keywords?.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  if (xhsCrawlForm.value.crawlType === 'detail' && !xhsCrawlForm.value.noteIds?.trim()) {
    ElMessage.warning('请输入笔记ID')
    return
  }
  
  xhsCrawling.value = true
  
  try {
    // 构建请求数据
    const requestData = {
      type: xhsCrawlForm.value.crawlType,
      pages: xhsCrawlForm.value.pages || 1
    }
    
    // 如果选择了账号，传递账号ID（后端会从账号管理中获取Cookie）
    if (xhsCrawlForm.value.accountId) {
      requestData.account_id = xhsCrawlForm.value.accountId
    }
    
    // 处理关键词或笔记ID
    if (xhsCrawlForm.value.crawlType === 'search') {
      requestData.keywords = xhsCrawlForm.value.keywords
        .split('\n')
        .map(k => k.trim())
        .filter(k => k)
    } else {
      requestData.note_ids = xhsCrawlForm.value.noteIds
        .split('\n')
        .map(id => id.trim())
        .filter(id => id)
    }
    
    // 调用RSS Content Aggregator API
    const response = await fetch(`${RSS_AGGREGATOR_API_URL}/api/xhs/crawl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    
    // 无论HTTP状态码是什么，都尝试读取JSON响应
    let result
    try {
      result = await response.json()
    } catch (e) {
      // 如果无法解析JSON，显示HTTP错误
      ElMessage.error(`请求失败: HTTP ${response.status} ${response.statusText}`)
      return
    }
    
    // 根据业务逻辑的code字段处理响应
    if (result.code === 200) {
      ElMessage.success(`爬取完成！成功保存 ${result.data.saved} 条数据`)
      // 延迟刷新列表
      setTimeout(() => {
        loadXhsContentList()
      }, 1000)
    } else if (result.code === 401) {
      ElMessage.warning(result.msg || '需要先进行扫码登录')
    } else {
      // 显示后端返回的具体错误信息
      ElMessage.error(result.msg || `爬取失败 (错误码: ${result.code})`)
    }
  } catch (error) {
    console.error('爬取失败:', error)
    ElMessage.error('网络错误: ' + error.message)
  } finally {
    xhsCrawling.value = false
  }
}

/**
 * 加载小红书内容列表
 */
const loadXhsContentList = async () => {
  xhsContentLoading.value = true
  try {
    const params = new URLSearchParams({
      source_platform: 'xiaohongshu',
      page: xhsContentPage.value.toString(),
      page_size: xhsContentPageSize.value.toString()
    })
    
    const response = await fetch(`${RSS_AGGREGATOR_API_URL}/api/content/list?${params.toString()}`)
    const result = await response.json()
    
    if (result.code === 200) {
      xhsContentList.value = result.data?.items || []
      xhsContentTotal.value = result.data?.total || 0
    } else {
      console.error('获取小红书内容列表失败:', result.msg)
      ElMessage.error(result.msg || '获取内容列表失败')
    }
  } catch (error) {
    console.error('获取小红书内容列表失败:', error)
    ElMessage.error('获取内容列表失败，请稍后重试')
  } finally {
    xhsContentLoading.value = false
  }
}

/**
 * 查看小红书内容详情
 */
const viewXhsContentDetail = (item) => {
  currentArticle.value = {
    title: item.title,
    content: item.content,
    author: item.author,
    url: item.url,
    published_at: item.published_at,
    tags: item.tags,
    media_urls: item.media_urls
  }
  articleDetailDialogVisible.value = true
}

/**
 * 处理小红书内容分页大小变化
 */
const handleXhsContentPageSizeChange = (size) => {
  xhsContentPageSize.value = size
  xhsContentPage.value = 1
  loadXhsContentList()
}

/**
 * 处理小红书内容页码变化
 */
const handleXhsContentPageChange = (page) => {
  xhsContentPage.value = page
  loadXhsContentList()
}

// 监听Tab切换，如果是公众号Tab则加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'wechat') {
    loadMonitorAccounts()
    loadWechatArticles()
    loadRssListForFilter() // 加载RSS列表用于筛选
  } else if (newTab === 'reddit') {
    loadRedditArticles()
  } else if (newTab === 'xiaohongshu') {
    loadXhsAccounts()
    loadXhsContentList()
  }
})

/**
 * 加载公众号文章列表
 */
const loadWechatArticles = async () => {
  articlesLoading.value = true
  try {
    // 构建查询参数
    const params = new URLSearchParams({
      page: articlesPage.value.toString(),
      page_size: articlesPageSize.value.toString()
    })
    
    // 创建时间范围筛选已移除，不再发送 create_time_start 和 create_time_end 参数
    
    // 支持RSS筛选：如果选择了公众号，支持多选
    if (filterForm.value.selectedAccounts && filterForm.value.selectedAccounts.length > 0) {
      // 将所有选中的公众号名称都作为筛选条件传入
      filterForm.value.selectedAccounts.forEach(accountName => {
        params.append('nick_name', accountName)
      })
    }
    
    if (filterForm.value.title) {
      params.append('title', filterForm.value.title)
    }
    
    // 只有当数组有2个元素时才添加，空数组不添加
    if (filterForm.value.pubtimeRange && Array.isArray(filterForm.value.pubtimeRange) && filterForm.value.pubtimeRange.length === 2 && filterForm.value.pubtimeRange[0] && filterForm.value.pubtimeRange[1]) {
      params.append('pubtime_start', filterForm.value.pubtimeRange[0])
      params.append('pubtime_end', filterForm.value.pubtimeRange[1])
    }
    
    const response = await fetch(`${apiBaseUrl}/hotspot/wechat/articles?${params.toString()}`)
    const result = await response.json()
    
    if (result.code === 200) {
      wechatArticles.value = result.data?.items || []
      articlesTotal.value = result.data?.total || 0
    } else {
      console.error('获取公众号文章列表失败:', result.msg)
      ElMessage.error(result.msg || '获取文章列表失败')
    }
  } catch (error) {
    console.error('获取公众号文章列表失败:', error)
    ElMessage.error('获取文章列表失败，请稍后重试')
  } finally {
    articlesLoading.value = false
  }
}

/**
 * 处理筛选查询
 */
const handleFilterSearch = () => {
  articlesPage.value = 1 // 重置到第一页
  loadWechatArticles()
}

/**
 * 处理筛选时，如果使用了RSS筛选，需要将选中的公众号名称转换为nickName参数
 */
const handleFilterWithRss = () => {
  // 如果选择了RSS公众号，将第一个选中的作为nickName（兼容旧的筛选逻辑）
  if (filterForm.value.selectedAccounts.length > 0) {
    // 这里可以保持原逻辑，或者修改loadWechatArticles来支持多个公众号筛选
    // 暂时保持兼容，使用第一个选中的公众号名称
  }
  handleFilterSearch()
}

/**
 * 处理筛选重置
 */
const handleFilterReset = () => {
  initFilterForm()
  articlesPage.value = 1
  loadWechatArticles()
}

/**
 * 处理分页大小变化
 */
const handleArticlesPageSizeChange = (size) => {
  articlesPageSize.value = size
  articlesPage.value = 1
  loadWechatArticles()
}

/**
 * 处理页码变化
 */
const handleArticlesPageChange = (page) => {
  articlesPage.value = page
  loadWechatArticles()
}

/**
 * 查看文章详情
 */
const viewArticleDetail = (article) => {
  currentArticle.value = article
  articleDetailDialogVisible.value = true
}

/**
 * 制作相关状态
 */
const productionTypeDialogVisible = ref(false)
const productionDialogStep = ref('select') // 'select' 或 'config'
const selectedProductionType = ref('image-text') // 默认选择图文
const pendingArticleLink = ref('') // 待传入的文章链接

/**
 * 制作内容类型配置
 */
const productionContentTypes = [
  {
    value: 'video',
    label: '视频',
    description: '发布视频内容到各大平台',
    icon: VideoCamera,
    features: ['支持多平台发布', '本地上传/素材库', '定时发布功能', '多种剪辑风格', '智能分镜处理']
  },
  {
    value: 'image-text',
    label: '图文',
    description: 'AI生成图文内容',
    icon: Picture,
    features: ['AI内容生成', '多种排版风格', '自动配图', '小红书爆款', '多尺寸适配']
  },
  {
    value: 'article',
    label: '文章',
    description: '发布长文章内容',
    icon: Document,
    features: ['富文本编辑', 'SEO优化', '多平台同步', '原创/仿写', '自动排版']
  }
]

/**
 * 获取内容类型标签文本
 */
const getProductionContentTypeLabel = (contentType) => {
  const type = productionContentTypes.find(t => t.value === contentType)
  return type ? type.label : '未知类型'
}

/**
 * 制作临时配置
 */
const productionTempConfig = ref({
  contentSourceType: 'other',
  inputContent: '',
  contentWordCount: 1000,
  contentLayoutStyle: 'xiaohongshu-hot',
  contentLayoutReference: '',
  imageStyleType: 'ai-auto',
  imageStyleReference: '',
  imageRatio: '1664*928',
  imageCount: 3,
  imageModel: 'qianwen',
  publishPlatform: 'xiaohongshu',
  coverStyleType: 'ai-auto',
  coverStyleReference: '',
  coverImageRatio: '1664*928',
  infoGraphicType: 'minimalist-tech',
  externalArticleLink: '',
  externalArticleSource: 'juejin'
})

/**
 * 重置制作配置
 */
const resetProductionConfig = () => {
  productionTempConfig.value = {
    contentSourceType: 'other',
    inputContent: '',
    contentWordCount: 1000,
    contentLayoutStyle: 'xiaohongshu-hot',
    contentLayoutReference: '',
    imageStyleType: 'ai-auto',
    imageStyleReference: '',
    imageRatio: '1664*928',
    imageCount: 3,
    imageModel: 'qianwen',
    publishPlatform: 'xiaohongshu',
    coverStyleType: 'ai-auto',
    coverStyleReference: '',
    coverImageRatio: '1664*928',
    infoGraphicType: 'minimalist-tech',
    externalArticleLink: '',
    externalArticleSource: 'juejin'
  }
}

/**
 * 开始制作 - 打开弹窗
 */
const startProduction = (article) => {
  pendingArticleLink.value = article.url || article.link || ''
  selectedProductionType.value = 'image-text' // 默认选择图文
  productionDialogStep.value = 'select'
  productionTypeDialogVisible.value = true
  resetProductionConfig()
}

/**
 * 进入配置步骤 - 直接跳转到制作中心并使用制作中心的弹窗
 */
const goToProductionConfigStep = () => {
  if (!selectedProductionType.value) {
    ElMessage.warning('请选择制作类型')
    return
  }
  
  // 保存待传入的配置到sessionStorage
  const pendingConfig = {
    contentType: selectedProductionType.value,
    inputContent: pendingArticleLink.value || '',
    contentSourceType: 'other'
  }
  
  // 根据链接判断内容来源类型
  if (pendingArticleLink.value) {
    if (pendingArticleLink.value.includes('xiaohongshu') || pendingArticleLink.value.includes('xhslink')) {
      pendingConfig.contentSourceType = 'xiaohongshu'
    } else if (pendingArticleLink.value.startsWith('http')) {
      pendingConfig.contentSourceType = 'other'
    }
  }
  
  // 保存到sessionStorage
  sessionStorage.setItem('hotspot_pending_production_config', JSON.stringify(pendingConfig))
  
  // 关闭当前弹窗
  handleProductionDialogCancel()
  
  // 跳转到制作中心（制作中心会自动检测并打开配置弹窗）
  router.push('/production-center')
}

/**
 * 处理弹窗取消
 */
const handleProductionDialogCancel = () => {
  productionTypeDialogVisible.value = false
  productionDialogStep.value = 'select'
  pendingArticleLink.value = ''
  resetProductionConfig()
}

/**
 * 跳转到制作中心（如果已经在config步骤）
 */
const goToProductionCenter = () => {
  goToProductionConfigStep()
}

// 组件挂载时，如果当前是公众号Tab，则加载数据
onMounted(() => {
  // 初始化筛选表单（设置默认值：最近一周）
  initFilterForm()
  
  // 加载RSS列表用于筛选
  loadRssListForFilter()
  
  // 页面初始化时，如果当前Tab是公众号，自动加载数据
  if (activeTab.value === 'wechat') {
    loadMonitorAccounts()
    loadWechatArticles()
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.hotspot-center {
  min-height: 100%;
  animation: fadeIn 0.6s ease-out;
  
  .hotspot-tabs {
    background-color: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .hotspot-tabs-nav {
      padding: 20px;
    }
  }
  
  .hotspot-list-container {
    padding: 24px;
    min-height: 400px;
  }
  
  // 公众号监测区域样式
  .wechat-monitor-section {
    .action-buttons {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      
      .add-account-btn,
      .refresh-monitor-btn {
        display: flex;
        align-items: center;
        gap: 6px;
      }
    }
    
    .monitor-accounts-list {
      .empty-accounts {
        padding: 60px 0;
        text-align: center;
      }
      
      .accounts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
        
        .account-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background-color: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          transition: all 0.3s;
          
          &:hover {
            border-color: #409eff;
            box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
          }
          
          .account-info {
            flex: 1;
            
            .account-name {
              display: flex;
              align-items: center;
              gap: 8px;
              font-size: 16px;
              font-weight: 500;
              color: #303133;
              margin-bottom: 8px;
              
              .el-icon {
                color: #409eff;
              }
            }
            
            .account-media-id {
              display: flex;
              align-items: center;
              gap: 8px;
              font-size: 12px;
              color: #909399;
              
              .label {
                font-weight: 500;
              }
              
              .value {
                font-family: 'Courier New', monospace;
                color: #606266;
              }
            }
          }
          
          .account-actions {
            display: flex;
            gap: 8px;
          }
        }
      }
    }
  }
  
  // 刷新监测配置弹框样式
  .refresh-monitor-form {
    // 添加监测号主区域样式
    .add-account-section {
      margin-bottom: 20px;
      
      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        
        .el-icon {
          color: #409eff;
        }
      }
      
      .add-account-form-inline {
        .form-row {
          display: flex;
          align-items: flex-start;
          gap: 16px;
          flex-wrap: wrap;
          
          .form-item-inline {
            margin-bottom: 0;
            
            :deep(.el-form-item__label) {
              width: auto !important;
              padding-right: 8px;
            }
          }
        }
        
        .form-tip {
          margin-top: 8px;
          font-size: 12px;
          color: #909399;
          line-height: 1.5;
        }
      }
    }
    
    // 刷新监测配置区域样式
    .refresh-config-section {
      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        
        .el-icon {
          color: #409eff;
        }
      }
    }
    
    .form-tip {
      margin-top: 8px;
      font-size: 12px;
      color: #909399;
      line-height: 1.5;
    }
    
    .account-checkbox-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: 300px;
      overflow-y: auto;
      padding: 8px;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      background-color: #fafafa;
      
      .account-checkbox-item {
        display: flex;
        align-items: center;
        padding: 8px;
        border-radius: 4px;
        transition: background-color 0.2s;
        
        &:hover {
          background-color: #f0f2f5;
        }
        
        .checkbox-account-info {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .account-name {
            font-weight: 500;
            color: #303133;
          }
          
          .account-media-id {
            font-size: 12px;
            color: #909399;
            font-family: 'Courier New', monospace;
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

  // RSS管理弹框样式
  .rss-manage-content {
    .rss-add-section {
      margin-bottom: 24px;
      
      .add-form-row {
        display: flex;
        gap: 16px;
        align-items: flex-end;
        
        .form-item {
          flex: 1;
          
          .form-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 8px;
      }
      
          .form-input {
            width: 100%;
          }
          
          &.form-item-button {
            flex: 0 0 auto;
            margin-bottom: 0;
            
            :deep(.el-button) {
              height: 32px;
            }
          }
        }
      }
    }
    
    .rss-recover-section {
      margin-bottom: 24px;
      padding: 16px;
      background-color: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 8px;
      
      .el-button {
        margin-bottom: 8px;
      }
      
      .recover-tip {
        font-size: 12px;
        color: #0369a1;
        line-height: 1.5;
        margin-top: 8px;
      }
    }
    
    .rss-recover-section {
      margin-bottom: 24px;
      padding: 16px;
      background-color: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 8px;
      
      .el-button {
        margin-bottom: 8px;
      }
      
      .recover-tip {
        font-size: 12px;
        color: #0369a1;
        line-height: 1.5;
        margin-top: 8px;
      }
    }
    
    .rss-list-section {
      margin-top: 24px;
      
      :deep(.el-table) {
        .el-table__header {
          th {
            background-color: #f8fafc;
            color: #1e293b;
            font-weight: 600;
          }
        }
        
        .el-table__body {
          td {
            padding: 12px 0;
          }
        }
      }
    }
  }
  
  // 弹窗按钮样式（匹配图片中的样式）
  .dialog-footer {
    .cancel-btn {
      background-color: #fff5f5;
      border-color: #ffcccc;
      color: #333;
      
      &:hover {
        background-color: #ffe6e6;
        border-color: #ffb3b3;
      }
    }
    
    .confirm-btn {
      background-color: #e6f3ff;
      border-color: #99ccff;
      color: #333;
      
      &:hover {
        background-color: #cce6ff;
        border-color: #66b3ff;
      }
    }
  }

  // 小红书爬取区域样式 - 扁平清爽高级设计
  .xhs-crawl-section {
    .xhs-filter-section {
      background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
      border-radius: 16px;
      padding: 28px 32px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
      border: 1px solid #f0f0f0;
      
      .xhs-filter-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 24px;
        margin-bottom: 24px;
        
        .xhs-filter-item {
          display: flex;
          flex-direction: column;
          gap: 10px;
          
          .xhs-filter-label {
            font-size: 13px;
            font-weight: 600;
            color: #1f2937;
            letter-spacing: 0.01em;
            margin: 0;
          }
          
          .xhs-filter-input {
            width: 100%;
            
            :deep(.el-input__wrapper) {
              border-radius: 8px;
              box-shadow: 0 0 0 1px #e5e7eb inset;
              transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
              background: #ffffff;
              
              &:hover {
                box-shadow: 0 0 0 1px #d1d5db inset;
              }
              
              &.is-focus {
                box-shadow: 0 0 0 2px #ff2442 inset;
              }
            }
            
            :deep(.el-textarea__inner) {
              border-radius: 8px;
              border: 1px solid #e5e7eb;
              transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
              font-size: 14px;
              line-height: 1.6;
              
              &:hover {
                border-color: #d1d5db;
              }
              
              &:focus {
                border-color: #ff2442;
                box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
              }
            }
          }
          
          .xhs-textarea {
            :deep(.el-textarea__inner) {
              min-height: 80px;
            }
          }
          
          .xhs-form-hint {
            font-size: 12px;
            color: #6b7280;
            line-height: 1.5;
            margin-top: 4px;
          }
        }
      }
      
      .xhs-filter-buttons {
        display: flex;
        gap: 12px;
        justify-content: flex-end;
        padding-top: 8px;
        border-top: 1px solid #f3f4f6;
        margin-top: 8px;
        
        .xhs-action-btn {
          height: 38px;
          padding: 0 24px;
          border-radius: 8px;
          font-weight: 500;
          font-size: 14px;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          border: none;
          
          &.xhs-primary-btn {
            background: linear-gradient(135deg, #ff2442 0%, #ff6b7a 100%);
            box-shadow: 0 2px 8px rgba(255, 36, 66, 0.25);
            
            &:hover {
              background: linear-gradient(135deg, #ff1a35 0%, #ff5a6b 100%);
              box-shadow: 0 4px 12px rgba(255, 36, 66, 0.35);
              transform: translateY(-1px);
            }
            
            &:active {
              transform: translateY(0);
            }
          }
          
          &:not(.xhs-primary-btn) {
            background: #ffffff;
            color: #374151;
            border: 1px solid #e5e7eb;
            
            &:hover {
              background: #f9fafb;
              border-color: #d1d5db;
              color: #111827;
            }
          }
        }
      }
      
      .xhs-account-option {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
      }
    }
    
    .xhs-table-container {
      background: #ffffff;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
      border: 1px solid #f0f0f0;
      
      .xhs-table {
        :deep(.el-table__header) {
          th {
            background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
            color: #1f2937;
            font-weight: 600;
            font-size: 13px;
            padding: 16px 0;
            border-bottom: 2px solid #e5e7eb;
            letter-spacing: 0.01em;
          }
        }
        
        :deep(.el-table__body) {
          tr {
            transition: all 0.2s ease;
            
            &:hover {
              background: #fafbfc;
              transform: scale(1.001);
            }
          }
          
          td {
            padding: 18px 0;
            font-size: 13px;
            color: #374151;
            border-bottom: 1px solid #f3f4f6;
          }
        }
        
        :deep(.el-button) {
          border-radius: 6px;
          font-weight: 500;
          transition: all 0.2s ease;
          
          &.el-button--primary {
            background: linear-gradient(135deg, #ff2442 0%, #ff6b7a 100%);
            border: none;
            
            &:hover {
              background: linear-gradient(135deg, #ff1a35 0%, #ff5a6b 100%);
              box-shadow: 0 2px 8px rgba(255, 36, 66, 0.3);
            }
          }
        }
        
        :deep(.el-tag) {
          border-radius: 6px;
          border: none;
          font-weight: 500;
          padding: 4px 10px;
        }
      }
    }
  }
  
  // 公众号文章列表区域样式
  .wechat-articles-section {
    margin-top: -26px;
    padding-top: 0px;
    border-top: 1px solid #e9ecef;
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      height: 100px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
      
      .header-buttons-group {
        display: flex;
        gap: 12px;
        align-items: center;
      }
    }
    
    // 筛选区域样式（扁平、高级、自然设计）
    .filter-section {
      margin-bottom: 24px;
      
      .filter-container {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      
      .filter-row {
        display: flex;
        align-items: flex-end;
        gap: 20px;
        flex-wrap: wrap;
        
        &.filter-row-buttons {
          align-items: center;
          justify-content: flex-end;
        }
      }
      
      .filter-item {
        display: flex;
        flex-direction: column;
        gap: 8px;
        flex: 0 0 auto;
        
        .filter-label {
          font-size: 13px;
          font-weight: 500;
          color: #606266;
          line-height: 1.5;
          margin: 0;
          padding: 0;
        }
        
        .filter-date-picker {
          width: 280px;
          
          :deep(.el-input__wrapper) {
            border-radius: 6px;
            box-shadow: 0 0 0 1px #dcdfe6 inset;
            transition: all 0.2s;
            
            &:hover {
              box-shadow: 0 0 0 1px #c0c4cc inset;
            }
            
            &.is-focus {
              box-shadow: 0 0 0 1px #409eff inset;
            }
          }
        }
        
        .filter-input {
          width: 220px;
          
          :deep(.el-input__wrapper) {
            border-radius: 6px;
            box-shadow: 0 0 0 1px #dcdfe6 inset;
            transition: all 0.2s;
            
            &:hover {
              box-shadow: 0 0 0 1px #c0c4cc inset;
            }
            
            &.is-focus {
              box-shadow: 0 0 0 1px #409eff inset;
            }
          }
        }
        
        &.filter-item-checkbox {
          flex: 1 1 100%;
          min-width: 400px;
          
          .account-checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding: 12px;
            border: 1px solid #e4e7ed;
            border-radius: 6px;
            background-color: #fafafa;
            min-height: 50px;
            max-height: 150px;
            overflow-y: auto;
            
            .account-checkbox {
              margin: 0;
              
              :deep(.el-checkbox__label) {
                font-size: 14px;
                color: #303133;
                padding-left: 8px;
              }
            }
          }
          
          .no-rss-tip {
            padding: 12px;
            color: #909399;
            font-size: 13px;
            text-align: center;
            border: 1px solid #e4e7ed;
            border-radius: 6px;
            background-color: #fafafa;
          }
        }
        
        &.filter-item-button {
          .filter-action-btn,
          .refresh-monitor-btn {
            height: 32px;
            padding: 8px 20px;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s;
            min-width: 100px;
          }
          
          .filter-action-btn {
            &:first-child {
              box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
              
              &:hover {
                box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
                transform: translateY(-1px);
              }
            }
            
            &:not(:first-child) {
              &:hover {
                background-color: #f5f7fa;
                border-color: #dcdfe6;
              }
            }
          }
          
          .refresh-monitor-btn {
            box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
            
            &:hover {
              box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
              transform: translateY(-1px);
            }
          }
        }
      }
    }
    
    .articles-table-container {
      .task-table {
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
      }
      
      .pagination-container {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
      
      .stats-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        font-size: 12px;
        
        .stat-label {
          color: #909399;
          margin-right: 4px;
        }
        
        .stat-value {
          color: #303133;
          font-weight: 500;
        }
      }
      
      .more-keywords {
        font-size: 12px;
        color: #909399;
        margin-left: 4px;
      }
    }
  }
  
  // 文章详情弹框样式
  .article-detail {
    .detail-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px 24px;
      font-size: 13px;
      color: #475569;
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid #e9ecef;
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
      max-height: 400px;
      overflow-y: auto;
    }
    
    .keywords-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 12px;
      
      .stat-label {
        color: #909399;
        margin-right: 4px;
      }
      
      .stat-value {
        color: #303133;
        font-weight: 500;
      }
    }
  }
  
  // 文字截断样式（和制作中心一致）
  .text-ellipsis {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  }
  
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
    max-height: calc(1.5em * 3) !important;
  }
  
  // 标题、摘要、正文列的三行省略样式（和制作中心一致）
  :deep(.title-column),
  :deep(.summary-column),
  :deep(.content-column) {
    .cell {
      padding: 12px 16px !important;
      white-space: normal !important;
      
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
        max-height: calc(1.5em * 3) !important;
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

// 制作类型选择弹窗样式（复用制作中心的样式）
.content-type-dialog {
  :deep(.el-dialog) {
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 24px rgba(0, 0, 0, 0.08);
    animation: dialogFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    overflow: hidden;
    
    .el-dialog__header {
      padding: 0;
      border-bottom: none;
    }
    
    .el-dialog__body {
      padding: 0 24px 24px;
    }
    
    .el-dialog__footer {
      padding: 16px 24px;
      border-top: 1px solid #f3f4f6;
    }
  }
  
  @keyframes dialogFadeIn {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(-10px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }
  
  .dialog-header-custom {
    padding: 20px 24px;
    background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
    border-bottom: 1px solid #f3f4f6;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
    }
    
    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #111827;
      margin: 0;
      letter-spacing: -0.02em;
    }
  }
  
  .content-type-selection {
    padding: 24px;
    background: #ffffff;
    
    .type-cards {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      
      .type-card {
        background: #ffffff;
        border: 1.5px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px 18px;
        cursor: pointer;
        position: relative;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
          opacity: 0;
          transform: scaleX(0);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          transform-origin: left;
        }
        
        &:hover {
          border-color: #3b82f6;
          box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12), 0 4px 12px rgba(0, 0, 0, 0.06);
          transform: translateY(-4px) scale(1.01);
          
          &::before {
            opacity: 1;
            transform: scaleX(1);
          }
        }
        
        &.selected {
          border-color: #3b82f6;
          border-width: 2px;
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #f0f9ff 100%);
          box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2), 0 4px 16px rgba(59, 130, 246, 0.1);
          transform: translateY(-2px);
          
          &::before {
            opacity: 1;
            transform: scaleX(1);
          }
        }
        
        .type-card-icon {
          width: 56px;
          height: 56px;
          margin: 0 auto 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
          border-radius: 14px;
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          
          .el-icon {
            color: #3b82f6;
            font-size: 30px;
          }
        }
        
        &.selected .type-card-icon {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
          
          .el-icon {
            color: white;
          }
        }
        
        .type-card-content {
          text-align: center;
          flex: 1;
          
          .type-card-title {
            font-size: 16px;
            font-weight: 600;
            color: #111827;
            margin: 0 0 8px 0;
          }
          
          .type-card-desc {
            font-size: 12px;
            color: #6b7280;
            margin: 0 0 14px 0;
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
              gap: 8px;
              font-size: 11px;
              color: #4b5563;
              margin-bottom: 8px;
              
              .el-icon {
                color: #10b981;
                font-size: 13px;
              }
            }
          }
        }
        
        &.selected .type-card-content {
          .type-card-title {
            color: #3b82f6;
            font-weight: 700;
          }
        }
        
        .type-card-check {
          position: absolute;
          top: 14px;
          right: 14px;
          width: 24px;
          height: 24px;
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transform: scale(0);
          transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
          
          .el-icon {
            color: white;
            font-size: 14px;
          }
        }
        
        &.selected .type-card-check {
          opacity: 1;
          transform: scale(1);
        }
      }
    }
  }
  
  .dialog-footer-custom {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    
    .el-button {
      border-radius: 8px;
      font-size: 14px;
      height: 38px;
      padding: 0 24px;
      font-weight: 500;
    }
  }
  
  .config-form-container {
    padding: 0;
    
    .config-form {
      padding: 20px 0;
      
      .form-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 24px;
      }
      
      .form-section-full {
        grid-column: 1 / -1;
      }
      
      .form-section {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px 24px;
        
        h3 {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
          margin: 0 0 12px 0;
          
          .required {
            color: #ef4444;
          }
        }
      }
    }
  }
}
</style>


<template>
  <div>
    <h2 style="margin-bottom: 24px">数据列表</h2>
    <el-tabs v-model="currentPlatform" @tab-change="handlePlatformChange">
      <el-tab-pane
        v-for="platform in nonWechatPlatforms"
        :key="platform.value"
        :label="platform.label"
        :name="platform.value"
      >
        <el-card style="margin-bottom: 16px">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>数据筛选</span>
            </div>
          </template>
          <el-space style="margin-bottom: 16px" wrap>
            <!-- 小红书和快手显示筛选选项 -->
            <template v-if="platform.value === 'xhs' || platform.value === 'ks'">
              <el-select
                v-model="filterCrawlerType"
                placeholder="爬取类型"
                clearable
                style="width: 150px"
                @change="handleFilterChange"
              >
                <el-option label="关键词搜索" value="search" />
                <el-option label="指定帖子详情" value="detail" />
                <el-option label="创作者主页" value="creator" />
              </el-select>
              <el-select
                v-model="filterKeyword"
                placeholder="关键词"
                clearable
                filterable
                style="width: 150px"
                @change="handleFilterChange"
              >
                <el-option
                  v-for="kw in filterOptions.keywords"
                  :key="kw"
                  :label="kw"
                  :value="kw"
                />
              </el-select>
              <el-select
                v-model="filterNoteType"
                placeholder="内容类型"
                clearable
                style="width: 120px"
                @change="handleFilterChange"
              >
                <el-option label="图文" value="图文" />
                <el-option label="视频" value="视频" />
                <el-option label="文章" value="文章" />
              </el-select>
            </template>
            
            <el-input
              v-model="searchText"
              placeholder="搜索标题或作者"
              style="width: 300px"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
            
            <el-button @click="handleReset">重置</el-button>
            <el-button :icon="Refresh" @click="handleRefresh" :loading="loading">
              刷新
            </el-button>
          </el-space>
        </el-card>
        
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>数据列表</span>
              <span style="color: #909399; font-size: 14px">共 {{ pagination.total }} 条</span>
            </div>
          </template>
          <el-table
            :data="data"
            v-loading="loading"
            style="width: 100%"
            @sort-change="handleSortChange"
          >
            <el-table-column prop="title" label="标题" width="300" show-overflow-tooltip>
              <template #default="{ row }">
                <a :href="row.note_url" target="_blank" rel="noopener noreferrer">
                  {{ row.title || '-' }}
                </a>
              </template>
            </el-table-column>
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="publish_time" label="发布时间" width="180" />
            <el-table-column
              prop="liked_count"
              label="点赞数"
              width="100"
              sortable="custom"
            >
              <template #default="{ row }">
                <el-tag v-if="row.liked_count" type="danger">{{ row.liked_count }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="comment_count"
              label="评论数"
              width="100"
              sortable="custom"
            >
              <template #default="{ row }">
                <el-tag v-if="row.comment_count" type="primary">{{ row.comment_count }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="collected_count"
              label="收藏数"
              width="100"
              sortable="custom"
            >
              <template #default="{ row }">
                <el-tag v-if="row.collected_count" type="success">{{ row.collected_count }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.type === 'video'" type="warning">视频</el-tag>
                <el-tag v-else>图文</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-space>
                  <el-button
                    type="primary"
                    link
                    :icon="ChatLineRound"
                    @click="handleViewComments(row.id)"
                  >
                    查看评论
                  </el-button>
                  <el-button
                    type="success"
                    link
                    @click="handleCreateProduction(row)"
                  >
                    制作
                  </el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
          
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
            style="margin-top: 16px; justify-content: flex-end"
          />
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="公众号" name="wechat">
        <WechatDataList />
      </el-tab-pane>
    </el-tabs>

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
      
      <!-- 步骤2: 配置表单 -->
      <div v-else class="config-form-container">
        <el-scrollbar height="600px">
          <!-- 视频配置 -->
          <div v-if="selectedProductionType === 'video'" class="config-form video-content">
            <!-- 1. 素材网址 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                  <h3 style="margin: 0;">素材网址</h3>
                </div>
                <el-input
                  v-model="productionTempConfig.video.materialUrl"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入素材网址"
                  maxlength="2000"
                  show-word-limit
                />
              </div>
            </div>

            <!-- 2. 剪辑风格 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>剪辑风格</h3>
                <el-radio-group v-model="productionTempConfig.video.editingStyle">
                  <el-radio label="toxic-movie">毒舌电影风格</el-radio>
                  <el-radio label="playful-nature-doc">俏皮自然纪录片风格</el-radio>
                  <el-radio label="deep-film-analysis">深度拉片风格</el-radio>
                  <el-radio label="product-review">商品评测风格</el-radio>
                  <el-radio label="my-movie">顾我电影风格</el-radio>
                  <el-radio label="historical-doc">历史纪录片风格</el-radio>
                  <el-radio label="general-commentary">通用解说风格</el-radio>
                  <el-radio label="children-animation">儿童动画片风格</el-radio>
                  <el-radio label="tiktok-product-intro">TikTok 商品介绍风格</el-radio>
                  <el-radio label="tiktok-text-product-intro">TikTok 文字商品介绍风格</el-radio>
                  <el-radio label="engaging-doc">引人入胜纪录片风格</el-radio>
                  <el-radio label="speech">演讲风格</el-radio>
                  <el-radio label="game-commentary">游戏解说风格</el-radio>
                  <el-radio label="variety-entertainment">综艺娱乐解说风格</el-radio>
                  <el-radio label="long-to-short">长视频剪辑短视频风格</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 3. 分镜数量 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>分镜数量</h3>
                <el-radio-group v-model="productionTempConfig.video.shotCount">
                  <el-radio :label="5">5</el-radio>
                  <el-radio :label="10">10</el-radio>
                  <el-radio :label="20">20</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 4. 语言 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>语言</h3>
                <el-radio-group v-model="productionTempConfig.video.language">
                  <el-radio label="zh-cn">中文</el-radio>
                  <el-radio label="en">英语</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 5. 文案 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>文案</h3>
                <el-input
                  v-model="productionTempConfig.video.copywriting"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入文案"
                  maxlength="2000"
                  show-word-limit
                />
              </div>
            </div>
          </div>

          <!-- 图文配置 -->
          <div v-else-if="selectedProductionType === 'image-text'" class="config-form image-text-content">
            <div class="form-grid">
              <div class="form-section">
                <h3>内容来源类型 <span class="required">*</span></h3>
                <el-radio-group v-model="productionTempConfig.imageText.contentSourceType">
                  <el-radio label="xiaohongshu">小红书链接</el-radio>
                  <el-radio label="other">其他链接</el-radio>
                  <el-radio label="custom">自定义内容</el-radio>
                </el-radio-group>
              </div>

              <div class="form-section">
                <h3>生图模型 <span class="required">*</span></h3>
                <el-radio-group v-model="productionTempConfig.imageText.imageModel">
                  <el-radio label="qianwen">千问</el-radio>
                  <el-radio label="jimeng">即梦</el-radio>
                  <el-radio label="sora">Sora</el-radio>
                  <el-radio label="nabana">nabana</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>输入内容 <span class="required">*</span></h3>
                <el-input
                  v-model="productionTempConfig.imageText.inputContent"
                  type="textarea"
                  :rows="3"
                  placeholder="根据上方来源输入对应的文案主题、文案内容或url链接"
                  maxlength="2000"
                  show-word-limit
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>内容排版风格 <span class="required">*</span></h3>
                <el-radio-group v-model="productionTempConfig.imageText.contentLayoutStyle">
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

            <div v-if="productionTempConfig.imageText.contentLayoutStyle === 'xiaohongshu-hot'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>内容排版类型-小红书爆款风格</h3>
                <el-input
                  v-model="productionTempConfig.imageText.contentLayoutReference"
                  placeholder="输入参考小红书爆款排版的链接"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图风格类型选择</h3>
                <el-radio-group v-model="productionTempConfig.imageText.imageStyleType">
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

            <div v-if="['xhs-bigtext', 'xhs-keyword'].includes(productionTempConfig.imageText.imageStyleType)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图风格选择-小红书爆款参考链接</h3>
                <el-input
                  v-model="productionTempConfig.imageText.imageStyleReference"
                  placeholder="输入配图参考小红书链接"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图-比例</h3>
                <el-radio-group v-model="productionTempConfig.imageText.imageRatio">
                  <el-radio label="1664*928">1664*928</el-radio>
                  <el-radio label="1472*1140">1472*1140</el-radio>
                  <el-radio label="1328*1328">1328*1328</el-radio>
                  <el-radio label="1140*1472">1140*1472</el-radio>
                  <el-radio label="928*1664">928*1664</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图风格类型选择</h3>
                <el-radio-group v-model="productionTempConfig.imageText.coverStyleType">
                  <el-radio label="none">无</el-radio>
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

            <div v-if="productionTempConfig.imageText.coverStyleType === 'info-graphic'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图-信息图类型</h3>
                <el-radio-group v-model="productionTempConfig.imageText.infoGraphicType">
                  <el-radio label="minimalist-tech">极简技术风</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['xhs-bigtext', 'xhs-keyword'].includes(productionTempConfig.imageText.coverStyleType)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图风格选择-小红书爆款风格</h3>
                <el-input
                  v-model="productionTempConfig.imageText.coverStyleReference"
                  placeholder="输入封面图参考链接"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图-比例</h3>
                <el-radio-group v-model="productionTempConfig.imageText.coverImageRatio">
                  <el-radio label="1664*928">1664*928</el-radio>
                  <el-radio label="1472*1140">1472*1140</el-radio>
                  <el-radio label="1328*1328">1328*1328</el-radio>
                  <el-radio label="1140*1472">1140*1472</el-radio>
                  <el-radio label="928*1664">928*1664</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section">
                <h3>配图张数</h3>
                <el-radio-group v-model="productionTempConfig.imageText.imageCount">
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
                <el-radio-group v-model="productionTempConfig.imageText.publishPlatform">
                  <el-radio label="xiaohongshu">小红书图文</el-radio>
                  <el-radio label="wechat">微信图文</el-radio>
                  <el-radio label="bilibili">B站图文</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>图文内容字数 <span class="required">*</span></h3>
                <el-radio-group v-model="productionTempConfig.imageText.contentWordCount" class="word-count-group">
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

            <div v-if="['external-ai-yes', 'external-ai-no'].includes(productionTempConfig.imageText.imageStyleType)" class="form-grid">
              <div class="form-section">
                <h3>配图风格类型选择-文章外图片-文章链接</h3>
                <el-input
                  v-model="productionTempConfig.imageText.externalArticleLink"
                  placeholder="输入文章链接"
                />
              </div>

              <div class="form-section">
                <h3>配图风格类型选择-文章外图片-文章来源</h3>
                <el-radio-group v-model="productionTempConfig.imageText.externalArticleSource">
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="zhihu">知乎</el-radio>
                </el-radio-group>
              </div>
            </div>
          </div>

          <!-- 文章配置 -->
          <div v-else-if="selectedProductionType === 'article'" class="config-form article-content">
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>写作模式 <span class="required">*</span></h3>
                <el-radio-group v-model="productionTempConfig.article.writingMode">
                  <el-radio label="polish">润色</el-radio>
                  <el-radio label="imitate">仿写</el-radio>
                  <el-radio label="original">原创</el-radio>
                  <el-radio label="reprint">搬运排版</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(productionTempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-文章来源平台</h3>
                <el-radio-group v-model="productionTempConfig.article.sourcePlatform">
                  <el-radio label="zhihu">知乎</el-radio>
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="medium">Medium</el-radio>
                  <el-radio label="other">其他</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(productionTempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-链接</h3>
                <el-input
                  v-model="productionTempConfig.article.articleLink"
                  placeholder="请粘贴对标文章链接"
                />
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(productionTempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-文章发布平台</h3>
                <el-radio-group v-model="productionTempConfig.article.publishPlatform">
                  <el-radio label="zhihu">知乎</el-radio>
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="medium">Medium</el-radio>
                  <el-radio label="other">其他</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(productionTempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>通用-排版风格</h3>
                <el-radio-group v-model="productionTempConfig.article.layoutStyle">
                  <el-radio label="orange-heart">橙心</el-radio>
                  <el-radio label="yanqi-lake">雁栖湖</el-radio>
                  <el-radio label="fullstack-blue">全栈蓝</el-radio>
                  <el-radio label="chazi">姹紫</el-radio>
                  <el-radio label="dynamic-blue">灵动蓝</el-radio>
                  <el-radio label="geek-black">极客黑</el-radio>
                  <el-radio label="rose-purple">蔷薇紫</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>是否进行自动化发布</h3>
                <el-radio-group v-model="productionTempConfig.article.autoPublish">
                  <el-radio label="yes">是</el-radio>
                  <el-radio label="no">否</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'imitate'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>仿写-主题内容</h3>
                <el-input
                  v-model="productionTempConfig.article.imitateTopic"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入你的主题或者片段内容"
                />
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'imitate'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>仿写-文章长短</h3>
                <el-select v-model="productionTempConfig.article.imitateLength" placeholder="Select an option" style="width: 100%">
                  <el-option label="短篇 (1000-2000字)" value="short" />
                  <el-option label="中篇 (2000-5000字)" value="medium" />
                  <el-option label="长篇 (5000字以上)" value="long" />
                </el-select>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-深度研究领域关键词</h3>
                <el-input
                  v-model="productionTempConfig.article.originalKeywords"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入深度研究领域关键词"
                />
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-当前层次</h3>
                <el-radio-group v-model="productionTempConfig.article.originalLevel">
                  <el-radio label="novice">小白 (完全陌生)</el-radio>
                  <el-radio label="beginner">入门 (理论储备)</el-radio>
                  <el-radio label="junior">初级实操者 (有限经验)</el-radio>
                  <el-radio label="senior">资深应用者 (丰富经验)</el-radio>
                  <el-radio label="expert">领域权威 (专家级)</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-学习目的</h3>
                <el-radio-group v-model="productionTempConfig.article.originalPurpose">
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

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-文章是否需要配图</h3>
                <el-radio-group v-model="productionTempConfig.article.originalNeedImage">
                  <el-radio label="yes">是</el-radio>
                  <el-radio label="no">否</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-是否自动化</h3>
                <el-radio-group v-model="productionTempConfig.article.originalAutomation">
                  <el-radio label="auto">自动化</el-radio>
                  <el-radio label="step">分步骤</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-研究主题探究的深度</h3>
                <el-radio-group v-model="productionTempConfig.article.originalDepth">
                  <el-radio :label="1">1</el-radio>
                  <el-radio :label="2">2</el-radio>
                  <el-radio :label="3">3</el-radio>
                  <el-radio :label="5">5</el-radio>
                  <el-radio :label="10">10</el-radio>
                  <el-radio :label="20">20</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-报告期望字数</h3>
                <el-radio-group v-model="productionTempConfig.article.originalWordCount" class="word-count-group">
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

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-报告期望语言</h3>
                <el-radio-group v-model="productionTempConfig.article.originalLanguage">
                  <el-radio label="zh-cn">中文简体</el-radio>
                  <el-radio label="zh-tw">中文繁体</el-radio>
                  <el-radio label="en">英语</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="productionTempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-提示词字数</h3>
                <el-radio-group v-model="productionTempConfig.article.originalPromptCount" class="word-count-group">
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

            <div v-if="['polish', 'imitate', 'reprint'].includes(productionTempConfig.article.writingMode) && productionTempConfig.article.publishPlatform === 'wechat'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-微信发布账号配置</h3>
                <el-radio-group v-model="productionTempConfig.article.wechatAccount">
                  <el-radio label="react">React中文社区</el-radio>
                  <el-radio label="biscuit">程序员饼干</el-radio>
                  <el-radio label="all">全部</el-radio>
                </el-radio-group>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
      
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button 
            v-if="productionDialogStep === 'config'"
            @click="productionDialogStep = 'select'" 
            size="large"
          >
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <el-button 
            @click="handleProductionDialogCancel" 
            size="large"
          >
            取消
          </el-button>
          <el-button 
            v-if="productionDialogStep === 'select'"
            type="primary" 
            @click="goToProductionConfigStep" 
            size="large"
            :disabled="!selectedProductionType"
          >
            下一步
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button 
            v-else
            type="primary" 
            @click="handleConfirmCreateProductionTask" 
            size="large"
          >
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 评论弹窗 -->
    <el-dialog
      v-model="commentsModalVisible"
      :title="`评论列表 (共 ${commentsPagination.total} 条)`"
      width="800px"
      @close="handleCommentsModalClose"
    >
      <el-skeleton v-if="commentsLoading" :rows="5" animated />
      <el-list v-else>
        <el-list-item v-for="comment in comments" :key="comment.id">
          <el-avatar :src="comment.avatar">{{ comment.author?.[0] || '?' }}</el-avatar>
          <div style="margin-left: 12px; flex: 1">
            <div style="margin-bottom: 8px">
              <el-space>
                <span>{{ comment.author || '匿名用户' }}</span>
                <el-tag v-if="comment.ip_location" size="small">{{ comment.ip_location }}</el-tag>
                <el-tag v-if="comment.like_count > 0" type="danger" size="small">
                  👍 {{ comment.like_count }}
                </el-tag>
                <el-tag v-if="comment.sub_comment_count > 0" type="primary" size="small">
                  回复 {{ comment.sub_comment_count }}
                </el-tag>
              </el-space>
            </div>
            <div style="margin-bottom: 8px">{{ comment.content || '-' }}</div>
            <div style="font-size: 12px; color: #999">{{ comment.create_time || '-' }}</div>
          </div>
        </el-list-item>
      </el-list>
      
      <el-pagination
        v-model:current-page="commentsPagination.current"
        :page-size="commentsPagination.pageSize"
        :total="commentsPagination.total"
        layout="total, prev, pager, next"
        @current-change="handleCommentsPageChange"
        style="margin-top: 16px"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, Refresh, ChatLineRound, VideoCamera, Picture, Document, Check, CircleCheckFilled, ArrowRight, ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import crawlerApi from '@/api/crawler'
import WechatDataList from './WechatDataList.vue'

const route = useRoute()
const router = useRouter()
const currentPlatform = ref(route.params.platform || 'xhs')
const data = ref([])
const loading = ref(false)
const searchText = ref('')
const filterCrawlerType = ref('')
const filterKeyword = ref('')
const filterNoteType = ref('')
const filterOptions = reactive({ keywords: [], crawler_types: [] })
const sortInfo = reactive({ field: '', order: '' })
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})
const commentsModalVisible = ref(false)
const currentNoteId = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const commentsPagination = reactive({
  current: 1,
  pageSize: 50,
  total: 0
})

const platformNames = {
  xhs: '小红书',
  dy: '抖音',
  ks: '快手',
  bili: 'B站',
  wb: '微博',
  tieba: '百度贴吧',
  zhihu: '知乎',
  juejin: '掘金',
  medium: 'Medium',
  wechat: '公众号'
}

const platforms = ref([])
const nonWechatPlatforms = computed(() => {
  if (platforms.value.length > 0) {
    return platforms.value.filter(p => p.value !== 'wechat')
  }
  // 默认平台列表
  return Object.keys(platformNames)
    .filter(key => key !== 'wechat')
    .map(key => ({ value: key, label: platformNames[key] }))
})

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const response = await crawlerApi.getPlatforms()
    platforms.value = response.platforms || []
  } catch (error) {
    console.error('加载平台列表失败:', error)
    // 使用默认平台列表
    platforms.value = Object.keys(platformNames).map(key => ({
      value: key,
      label: platformNames[key]
    }))
  }
}

// 先定义函数，避免在 watch 中访问未初始化的函数
const loadFilterOptions = async () => {
  try {
    const result = await crawlerApi.getFilterOptions(currentPlatform.value)
    filterOptions.keywords = result.keywords || []
    filterOptions.crawler_types = result.crawler_types || []
  } catch (error) {
    console.error('加载筛选选项失败:', error)
  }
}

const loadData = async (showMessage = false) => {
  try {
    loading.value = true
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: searchText.value
    }
    
    // 小红书和快手添加筛选参数
    if (currentPlatform.value === 'xhs' || currentPlatform.value === 'ks') {
      if (filterCrawlerType.value) {
        params.crawler_type = filterCrawlerType.value
      }
      if (filterKeyword.value) {
        params.source_keyword = filterKeyword.value
      }
      if (filterNoteType.value) {
        params.note_type = filterNoteType.value
      }
      if (sortInfo.field && sortInfo.order) {
        params.sort_field = sortInfo.field
        params.sort_order = sortInfo.order
      }
    }
    
    const result = await crawlerApi.getData(currentPlatform.value, params)
    data.value = result.data || []
    pagination.total = result.total || 0
    
    if (showMessage) {
      ElMessage.success('数据刷新成功')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadPlatforms()
  // 如果有路由参数，设置当前平台
  if (route.params.platform) {
    currentPlatform.value = route.params.platform
  }
})

watch(currentPlatform, (newPlatform) => {
  if (newPlatform !== 'wechat') {
    searchText.value = ''
    filterCrawlerType.value = ''
    filterKeyword.value = ''
    filterNoteType.value = ''
    sortInfo.field = ''
    sortInfo.order = ''
    pagination.current = 1
    pagination.pageSize = 20
    pagination.total = 0
    
    // 加载筛选选项（小红书和快手）
    if (newPlatform === 'xhs' || newPlatform === 'ks') {
      loadFilterOptions()
    }
    // 加载数据
    loadData()
  }
}, { immediate: true })

watch(
  [currentPlatform, () => pagination.current, () => pagination.pageSize, filterCrawlerType, filterKeyword, filterNoteType, () => sortInfo.field, () => sortInfo.order],
  () => {
    if (currentPlatform.value !== 'wechat') {
      loadData()
    }
  }
)

const handleRefresh = () => {
  loadData(true)
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  searchText.value = ''
  if (currentPlatform.value === 'xhs' || currentPlatform.value === 'ks') {
    filterCrawlerType.value = ''
    filterKeyword.value = ''
    filterNoteType.value = ''
    sortInfo.field = ''
    sortInfo.order = ''
  }
  pagination.current = 1
  loadData()
}

const handleFilterChange = () => {
  pagination.current = 1
  loadData()
}

const handleSortChange = ({ prop, order }) => {
  if (order) {
    sortInfo.field = prop
    sortInfo.order = order === 'ascending' ? 'asc' : 'desc'
  } else {
    sortInfo.field = ''
    sortInfo.order = ''
  }
  loadData()
}

const handlePageChange = (page) => {
  pagination.current = page
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.current = 1
}

const loadComments = async (noteId, page = 1) => {
  try {
    commentsLoading.value = true
    const result = await crawlerApi.getComments(currentPlatform.value, noteId, {
      page: page,
      page_size: commentsPagination.pageSize
    })
    comments.value = result.comments || []
    commentsPagination.current = page
    commentsPagination.total = result.total || 0
  } catch (error) {
    console.error('加载评论失败:', error)
    ElMessage.error('加载评论失败: ' + (error.message || '未知错误'))
  } finally {
    commentsLoading.value = false
  }
}

const handleViewComments = (noteId) => {
  currentNoteId.value = noteId
  commentsModalVisible.value = true
  commentsPagination.current = 1
  commentsPagination.total = 0
  loadComments(noteId, 1)
}

const handleCommentsModalClose = () => {
  commentsModalVisible.value = false
  currentNoteId.value = null
  comments.value = []
}

const handleCommentsPageChange = (page) => {
  if (currentNoteId.value) {
    loadComments(currentNoteId.value, page)
  }
}

const handlePlatformChange = (value) => {
  currentPlatform.value = value
  // 更新路由
  if (value === 'wechat') {
    route.params.platform !== 'wechat' && router.replace('/crawler/data/wechat')
  } else {
    route.params.platform !== value && router.replace(`/crawler/data/${value}`)
  }
}

// 制作相关
const productionTypeDialogVisible = ref(false)
const selectedProductionType = ref('')
const productionDialogStep = ref('select') // 'select' 或 'config'
const currentProductionRow = ref(null)

// 临时配置数据（用于弹窗中的配置）
const productionTempConfig = reactive({
  video: {
    materialUrl: '', // 素材网址
    editingStyle: 'toxic-movie', // 剪辑风格，默认毒舌电影风格
    shotCount: 5, // 分镜数量
    language: 'zh-cn', // 语言
    copywriting: '', // 文案
  },
  imageText: {
    contentSourceType: 'other',
    inputContent: '',
    contentWordCount: 1000,
    contentLayoutStyle: 'xiaohongshu-hot',
    contentLayoutReference: '',
    imageCount: 3,
    imageStyleType: 'builtin-ai-no',
    imageStyleReference: '',
    imageRatio: '1664*928',
    externalArticleLink: '',
    externalArticleSource: 'juejin',
    coverStyleType: 'ai-auto',
    coverStyleReference: '',
    coverImageRatio: '1664*928',
    infoGraphicType: 'minimalist-tech',
    imageModel: 'sora',
    publishPlatform: 'xiaohongshu'
  },
  article: {
    writingMode: 'polish',
    sourcePlatform: 'wechat',
    articleLink: '',
    publishPlatform: 'wechat',
    layoutStyle: 'rose-purple',
    autoPublish: 'yes',
    imitateTopic: '',
    imitateLength: '',
    originalKeywords: '',
    originalLevel: 'beginner',
    originalPurpose: 'knowledge',
    originalNeedImage: 'no',
    originalAutomation: 'step',
    originalDepth: 3,
    originalWordCount: 3000,
    originalLanguage: 'zh-cn',
    originalPromptCount: 500,
    wechatAccount: 'all'
  }
})

const productionContentTypes = [
  {
    value: 'video',
    label: '视频',
    description: '发布视频内容到各大平台',
    icon: VideoCamera,
    features: [
      '支持多平台发布',
      '本地上传/素材库',
      '定时发布功能',
      '多种剪辑风格',
      '智能分镜处理'
    ]
  },
  {
    value: 'image-text',
    label: '图文',
    description: 'AI生成图文内容',
    icon: Picture,
    features: [
      'AI内容生成',
      '多种排版风格',
      '自动配图',
      '小红书爆款',
      '多尺寸适配'
    ]
  },
  {
    value: 'article',
    label: '文章',
    description: '发布长文章内容',
    icon: Document,
    features: [
      '富文本编辑',
      'SEO优化',
      '多平台同步',
      '原创/仿写',
      '自动排版'
    ]
  }
]

// 获取内容类型标签
const getProductionContentTypeLabel = (contentType) => {
  const type = productionContentTypes.find(t => t.value === contentType)
  return type ? type.label : '未知类型'
}

// 重置临时配置
const resetProductionTempConfig = () => {
  productionTempConfig.video = {
    materialUrl: '',
    editingStyle: 'toxic-movie',
    shotCount: 5,
    language: 'zh-cn',
    copywriting: '',
  }
  productionTempConfig.imageText = {
    contentSourceType: 'other',
    inputContent: '',
    contentWordCount: 1000,
    contentLayoutStyle: 'xiaohongshu-hot',
    contentLayoutReference: '',
    imageCount: 3,
    imageStyleType: 'builtin-ai-no',
    imageStyleReference: '',
    imageRatio: '1664*928',
    externalArticleLink: '',
    externalArticleSource: 'juejin',
    coverStyleType: 'ai-auto',
    coverStyleReference: '',
    coverImageRatio: '1664*928',
    infoGraphicType: 'minimalist-tech',
    imageModel: 'sora',
    publishPlatform: 'xiaohongshu'
  }
  productionTempConfig.article = {
    writingMode: 'polish',
    sourcePlatform: 'wechat',
    articleLink: '',
    publishPlatform: 'wechat',
    layoutStyle: 'rose-purple',
    autoPublish: 'yes',
    imitateTopic: '',
    imitateLength: '',
    originalKeywords: '',
    originalLevel: 'beginner',
    originalPurpose: 'knowledge',
    originalNeedImage: 'no',
    originalAutomation: 'step',
    originalDepth: 3,
    originalWordCount: 3000,
    originalLanguage: 'zh-cn',
    originalPromptCount: 500,
    wechatAccount: 'all'
  }
}

const handleCreateProduction = (row) => {
  currentProductionRow.value = row
  selectedProductionType.value = ''
  productionDialogStep.value = 'select'
  resetProductionTempConfig()
  
  // 根据爬取的数据自动填充一些字段
  if (row.note_url) {
    // 如果是图文类型，自动填充输入内容为URL
    productionTempConfig.imageText.inputContent = row.note_url
    productionTempConfig.imageText.contentSourceType = 'other'
    
    // 如果是文章类型，自动填充文章链接
    productionTempConfig.article.articleLink = row.note_url
  }
  
  productionTypeDialogVisible.value = true
}

const goToProductionConfigStep = () => {
  if (!selectedProductionType.value) {
    ElMessage.warning('请选择制作类型')
    return
  }
  productionDialogStep.value = 'config'
}

const handleProductionDialogCancel = () => {
  productionTypeDialogVisible.value = false
  productionDialogStep.value = 'select'
  selectedProductionType.value = ''
  resetProductionTempConfig()
  currentProductionRow.value = null
}

const handleConfirmCreateProductionTask = () => {
  // 验证必填项
  if (selectedProductionType.value === 'video') {
    if (!productionTempConfig.video.materialUrl) {
      ElMessage.warning('请输入素材网址')
      return
    }
  } else if (selectedProductionType.value === 'image-text') {
    if (!productionTempConfig.imageText.inputContent) {
      ElMessage.warning('请输入内容')
      return
    }
    if (!productionTempConfig.imageText.contentLayoutStyle) {
      ElMessage.warning('请选择内容排版风格')
      return
    }
  } else if (selectedProductionType.value === 'article') {
    if (!productionTempConfig.article.writingMode) {
      ElMessage.warning('请选择写作模式')
      return
    }
    if (['polish', 'imitate', 'reprint'].includes(productionTempConfig.article.writingMode)) {
      if (!productionTempConfig.article.articleLink) {
        ElMessage.warning('请输入文章链接')
        return
      }
    }
  }
  
  // 关闭弹窗
  productionTypeDialogVisible.value = false
  productionDialogStep.value = 'select'
  
  // 跳转到制作中心，并传递数据
  const row = currentProductionRow.value
  router.push({
    path: '/production',
    query: {
      type: selectedProductionType.value,
      source: 'crawler',
      url: row.note_url || '',
      title: row.title || '',
      desc: row.desc || '',
      platform: currentPlatform.value,
      config: JSON.stringify(productionTempConfig[selectedProductionType.value])
    }
  })
  
  // 重置状态
  selectedProductionType.value = ''
  resetProductionTempConfig()
  currentProductionRow.value = null
}
</script>

<style scoped>
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 500;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  border-radius: 4px;
}

:deep(.el-pagination) {
  display: flex;
}

/* 制作类型选择弹窗样式 */
:deep(.content-type-dialog) {
  .dialog-header-custom {
    text-align: center;
    padding: 0;
    
    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #111827;
    }
  }
  
  .content-type-selection {
    padding: 20px 0;
    
    .type-cards {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 24px;
      max-width: 1100px;
      margin: 0 auto;
      
      .type-card {
        position: relative;
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 28px 24px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        align-items: center;
        min-height: 320px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        
        &:hover {
          border-color: #3b82f6;
          box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
          transform: translateY(-4px);
        }
        
        &.selected {
          border-color: #3b82f6;
          border-width: 2px;
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #f0f9ff 100%);
          box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2), 0 4px 16px rgba(59, 130, 246, 0.1);
          transform: translateY(-2px);
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
          display: flex;
          flex-direction: column;
          
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
            min-height: 36px;
          }
          
          .type-card-features {
            list-style: none;
            padding: 0;
            margin: 0;
            text-align: left;
            flex: 1;
            
            li {
              display: flex;
              align-items: center;
              gap: 8px;
              font-size: 11px;
              color: #4b5563;
              margin-bottom: 8px;
              line-height: 1.5;
              
              .el-icon {
                color: #10b981;
                font-size: 13px;
                flex-shrink: 0;
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
          width: 28px;
          height: 28px;
          background: #3b82f6;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          
          .el-icon {
            color: white;
            font-size: 18px;
          }
        }
      }
    }
  }
  
  .dialog-footer-custom {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px 0 0 0;
    border-top: 1px solid #e5e7eb;
    margin-top: 24px;
  }
  
  .config-form-container {
    padding: 0;
    
    .config-form {
      padding: 20px 0;
      
      &.image-text-content,
      &.video-content,
      &.article-content {
        padding: 0;
      }
    }
  }
  
  /* 配置表单样式（复用制作中心的样式） */
  .config-form {
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }
    
    .form-section-full {
      grid-column: span 2;
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
  }
}
</style>


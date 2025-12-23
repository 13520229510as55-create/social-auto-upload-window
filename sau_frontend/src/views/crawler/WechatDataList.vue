<template>
  <div style="display: flex; gap: 16px">
    <el-card
      title="公众号订阅源"
      style="width: 400px; flex-shrink: 0"
    >
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>公众号订阅源</span>
          <el-space>
            <el-button size="small" @click="loadFeeds">刷新列表</el-button>
            <el-button 
              size="small" 
              :icon="Refresh"
              @click="handleRefreshAll"
              :loading="refreshing"
            >
              刷新全部
            </el-button>
          </el-space>
        </div>
      </template>
      
      <el-table
        :data="feeds"
        v-loading="loading"
        size="small"
        @row-click="(row) => setSelectedFeedId(row.id)"
        :row-style="getRowStyle"
      >
        <el-table-column label="公众号">
          <template #default="{ row }">
            <el-space>
              <el-avatar :src="row.mp_cover" :size="24" />
              <span>{{ row.mp_name }}</span>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后同步" width="180">
          <template #default="{ row }">
            {{ formatTime(row.sync_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-space>
              <el-button
                size="small"
                type="primary"
                link
                @click.stop="setSelectedFeedId(row.id)"
              >
                查看文章
              </el-button>
              <el-button
                size="small"
                :icon="Refresh"
                :loading="refreshing && selectedFeedId === row.id"
                @click.stop="handleRefreshFeed(row.id)"
              >
                刷新
              </el-button>
              <el-button
                v-if="row.has_history === 1"
                size="small"
                :icon="Clock"
                :loading="gettingHistory && historyProgress.id === row.id"
                @click.stop="handleGetHistoryArticles(row.id)"
              >
                {{ historyProgress.id === row.id ? '停止获取' : '获取历史' }}
              </el-button>
              <el-switch
                size="small"
                :model-value="row.status === 1"
                @change="(checked) => handleUpdateFeedStatus(row.id, checked ? 1 : 2)"
                active-text="启用"
                inactive-text="禁用"
              />
              <el-button
                size="small"
                type="danger"
                link
                @click.stop="handleDeleteFeed(row.id)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card
      :title="selectedFeedId ? `文章列表 (${getFeedName(selectedFeedId)})` : '文章列表'"
      style="flex: 1"
    >
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>{{ selectedFeedId ? `文章列表 (${getFeedName(selectedFeedId)})` : '文章列表' }}</span>
          <el-space v-if="selectedFeedId">
            <el-button
              size="small"
              :icon="Refresh"
              :loading="refreshing"
              @click="handleRefreshFeed(selectedFeedId)"
            >
              刷新文章
            </el-button>
            <el-button
              v-if="getFeedById(selectedFeedId)?.has_history === 1"
              size="small"
              :icon="Clock"
              :loading="gettingHistory && historyProgress.id === selectedFeedId"
              @click="handleGetHistoryArticles(selectedFeedId)"
            >
              {{ historyProgress.id === selectedFeedId ? '停止获取' : '获取历史' }}
            </el-button>
          </el-space>
        </div>
      </template>
      
      <div v-if="selectedFeedId">
        <el-table
          :data="articles"
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="title" label="标题" show-overflow-tooltip>
            <template #default="{ row }">
              <a
                :href="`https://mp.weixin.qq.com/s/${row.id}`"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ row.title }}
              </a>
            </template>
          </el-table-column>
          <el-table-column prop="publish_time" label="发布时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.publish_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button
                type="success"
                link
                @click="handleCreateProduction(row)"
              >
                制作
              </el-button>
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
          style="margin-top: 16px"
        />
      </div>
      <div v-else style="text-align: center; padding: 40px; color: #999">
        请选择一个公众号查看文章列表
      </div>
    </el-card>

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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, Clock, VideoCamera, Picture, Document, Check, CircleCheckFilled, ArrowRight, ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import crawlerApi from '@/api/crawler'
import dayjs from 'dayjs'

const router = useRouter()

const feeds = ref([])
const articles = ref([])
const selectedFeedId = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const gettingHistory = ref(false)
const historyProgress = ref({ id: '', page: 1 })
const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0
})

let progressInterval = null

const statusMap = {
  0: { type: 'danger', text: '失效' },
  1: { type: 'success', text: '启用' },
  2: { type: 'info', text: '禁用' }
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
}

const getStatusText = (status) => {
  return statusMap[status]?.text || '未知'
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss')
}

const getFeedName = (feedId) => {
  const feed = feeds.value.find(f => f.id === feedId)
  return feed?.mp_name || ''
}

const getFeedById = (feedId) => {
  return feeds.value.find(f => f.id === feedId)
}

const getRowStyle = ({ row }) => {
  return {
    cursor: 'pointer',
    backgroundColor: selectedFeedId.value === row.id ? '#e6f7ff' : 'transparent'
  }
}

onMounted(() => {
  loadFeeds()
  
  // 轮询获取历史文章进度
  progressInterval = setInterval(async () => {
    try {
      const progress = await crawlerApi.getWechatHistoryProgress()
      historyProgress.value = progress
    } catch (error) {
      // 忽略错误
    }
  }, 2000)
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})

watch(selectedFeedId, (newId) => {
  if (newId !== null) {
    pagination.value.current = 1
    loadArticles()
  }
})

watch([pagination], () => {
  if (selectedFeedId.value) {
    loadArticles()
  }
}, { deep: true })

const loadFeeds = async () => {
  try {
    loading.value = true
    const data = await crawlerApi.getWechatFeeds()
    feeds.value = data.feeds || []
  } catch (error) {
    ElMessage.error('加载订阅源列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadArticles = async () => {
  try {
    loading.value = true
    const params = {
      mp_id: selectedFeedId.value || undefined,
      limit: pagination.value.pageSize,
      offset: (pagination.value.current - 1) * pagination.value.pageSize
    }
    const data = await crawlerApi.getWechatArticles(params)
    articles.value = data.articles || []
    pagination.value.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载文章列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const setSelectedFeedId = (feedId) => {
  selectedFeedId.value = feedId
}

const handleRefreshFeed = async (feedId) => {
  try {
    refreshing.value = true
    await crawlerApi.refreshWechatFeed(feedId)
    ElMessage.success('刷新成功')
    await loadFeeds()
    if (feedId === selectedFeedId.value) {
      await loadArticles()
    }
  } catch (error) {
    ElMessage.error('刷新失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

const handleUpdateFeedStatus = async (feedId, status) => {
  try {
    await crawlerApi.updateWechatFeedStatus(feedId, status)
    ElMessage.success('状态更新成功')
    await loadFeeds()
  } catch (error) {
    ElMessage.error('更新状态失败: ' + error.message)
  }
}

const handleDeleteFeed = async (feedId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个订阅源吗？已获取的文章不会被删除。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await crawlerApi.deleteWechatFeed(feedId)
    ElMessage.success('删除成功')
    if (feedId === selectedFeedId.value) {
      selectedFeedId.value = null
      articles.value = []
    }
    await loadFeeds()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const handleGetHistoryArticles = async (feedId) => {
  try {
    gettingHistory.value = true
    if (historyProgress.value.id === feedId) {
      // 停止获取
      await crawlerApi.getWechatHistoryArticles(feedId)
      ElMessage.info('已停止获取历史文章')
    } else {
      // 开始获取
      await crawlerApi.getWechatHistoryArticles(feedId)
      ElMessage.success('开始获取历史文章，请耐心等待')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  } finally {
    gettingHistory.value = false
  }
}

const handleRefreshAll = async () => {
  try {
    refreshing.value = true
    const feedsData = await crawlerApi.getWechatFeeds()
    for (const feed of feedsData.feeds || []) {
      if (feed.status === 1) {
        try {
          await crawlerApi.refreshWechatFeed(feed.id)
        } catch (error) {
          console.error(`刷新 ${feed.mp_name} 失败:`, error)
        }
      }
    }
    ElMessage.success('批量刷新完成')
    await loadFeeds()
    if (selectedFeedId.value) {
      await loadArticles()
    }
  } catch (error) {
    ElMessage.error('批量刷新失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

const handlePageChange = (page) => {
  pagination.value.current = page
}

const handlePageSizeChange = (size) => {
  pagination.value.pageSize = size
  pagination.value.current = 1
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

/**
 * 获取内容类型标签
 */
const getProductionContentTypeLabel = (contentType) => {
  const type = productionContentTypes.find(t => t.value === contentType)
  return type ? type.label : '未知类型'
}

/**
 * 重置临时配置
 */
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

/**
 * 处理创建制作任务
 */
const handleCreateProduction = (row) => {
  currentProductionRow.value = row
  selectedProductionType.value = ''
  productionDialogStep.value = 'select'
  resetProductionTempConfig()
  
  // 根据公众号文章数据自动填充一些字段
  const articleUrl = `https://mp.weixin.qq.com/s/${row.id}`
  // 如果是图文类型，自动填充输入内容为URL
  productionTempConfig.imageText.inputContent = articleUrl
  productionTempConfig.imageText.contentSourceType = 'other'
  
  // 如果是文章类型，自动填充文章链接
  productionTempConfig.article.articleLink = articleUrl
  productionTempConfig.article.sourcePlatform = 'wechat'
  
  productionTypeDialogVisible.value = true
}

/**
 * 跳转到配置步骤
 */
const goToProductionConfigStep = () => {
  if (!selectedProductionType.value) {
    ElMessage.warning('请选择制作类型')
    return
  }
  productionDialogStep.value = 'config'
}

/**
 * 处理弹窗取消
 */
const handleProductionDialogCancel = () => {
  productionTypeDialogVisible.value = false
  productionDialogStep.value = 'select'
  selectedProductionType.value = ''
  resetProductionTempConfig()
  currentProductionRow.value = null
}

/**
 * 确认创建制作任务
 */
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
  
  // 跳转到制作中心-数据列表，并传递数据
  const row = currentProductionRow.value
  const articleUrl = `https://mp.weixin.qq.com/s/${row.id}`
  router.push({
    path: '/production/data',
    query: {
      type: selectedProductionType.value,
      source: 'crawler',
      url: articleUrl,
      title: row.title || '',
      desc: '',
      platform: 'wechat',
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


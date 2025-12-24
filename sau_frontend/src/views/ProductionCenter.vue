<template>
  <div class="production-center">
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
          type="primary" 
          @click="addTab"
          class="create-task-btn"
        >
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
        <el-button 
          class="select-all-btn"
          :disabled="productionRecords.length === 0"
          @click="toggleSelectAllRecords"
        >
          <el-icon><Finished /></el-icon>
          全选
        </el-button>
        <el-button 
          class="batch-publish-btn"
          :loading="listBatchPublishing"
          :disabled="selectedRecords.length === 0"
          @click="batchPublishSelectedRecords"
        >
          <el-icon><Promotion /></el-icon>
          批量发布
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
        <el-button 
          @click="refreshProductionRecords"
          :loading="productionListLoading"
          class="refresh-list-btn"
        >
          <el-icon><RefreshRight /></el-icon>
          刷新列表
        </el-button>
      </div>
    </div>

    <!-- 任务卡片列表 -->
    <div class="task-cards-container">
      <div 
        v-for="tab in tabs" 
        :key="tab.name"
        :class="['task-card', { active: activeTab === tab.name }]"
        @click="activeTab = tab.name"
      >
        <div class="task-card-header">
          <div class="task-info">
            <el-tag :type="getContentTypeTagType(tab.contentType)" class="task-type-tag">
              <el-icon><component :is="getContentTypeIcon(tab.contentType)" /></el-icon>
              {{ getContentTypeLabel(tab.contentType) }}
            </el-tag>
            <span class="task-title">{{ tab.label }}</span>
          </div>
          <div class="task-actions">
            <el-icon 
              v-if="tabs.length > 1"
              class="remove-icon" 
              @click.stop="removeTab(tab.name)"
            >
              <Close />
            </el-icon>
          </div>
        </div>
        <div class="task-card-indicator" v-if="activeTab === tab.name"></div>
      </div>
    </div>

    <!-- 新建任务 Modal -->
    <el-dialog
      v-model="contentTypeDialogVisible"
      width="1200px"
      class="content-type-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <template #header>
        <div class="dialog-header-custom">
          <h2 v-if="dialogStep === 'select'">选择制作类型</h2>
          <h2 v-else>配置{{ getContentTypeLabel(selectedContentType) }}任务</h2>
        </div>
      </template>
      
      <!-- 步骤1: 选择内容类型 -->
      <div v-if="dialogStep === 'select'" class="content-type-selection">
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
      
      <!-- 步骤2: 配置表单 -->
      <div v-else class="config-form-container">
        <el-scrollbar height="600px">
          <!-- 视频配置 -->
          <div v-if="selectedContentType === 'video'" class="config-form video-content">
            <!-- 1. 素材网址 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                  <h3 style="margin: 0;">素材网址</h3>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="openMaterialSelectionDialog"
                    style="margin-left: 10px;"
                  >
                    <el-icon><FolderOpened /></el-icon>
                    选择素材
                  </el-button>
                </div>
                <el-input
                  v-model="tempConfig.video.materialUrl"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入素材网址，或点击右侧按钮从素材库中选择"
                  maxlength="2000"
                  show-word-limit
                />
              </div>
            </div>

            <!-- 2. 剪辑风格 -->
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>剪辑风格</h3>
                <el-radio-group v-model="tempConfig.video.editingStyle">
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
                <el-radio-group v-model="tempConfig.video.shotCount">
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
                <el-radio-group v-model="tempConfig.video.language">
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
                  v-model="tempConfig.video.copywriting"
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
          <div v-else-if="selectedContentType === 'image-text'" class="config-form image-text-content">
            <div class="form-grid">
              <div class="form-section">
                <h3>内容来源类型 <span class="required">*</span></h3>
                <el-radio-group v-model="tempConfig.imageText.contentSourceType">
                  <el-radio label="xiaohongshu">小红书链接</el-radio>
                  <el-radio label="other">其他链接</el-radio>
                  <el-radio label="custom">自定义内容</el-radio>
                </el-radio-group>
              </div>

              <div class="form-section">
                <h3>生图模型 <span class="required">*</span></h3>
                <el-radio-group v-model="tempConfig.imageText.imageModel">
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
                  v-model="tempConfig.imageText.inputContent"
                  type="textarea"
                  :rows="3"
                  placeholder="根据上方来源输入对应的文案主题/文案内容/url链接"
                  maxlength="2000"
                  show-word-limit
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>内容排版风格 <span class="required">*</span></h3>
                <el-radio-group v-model="tempConfig.imageText.contentLayoutStyle">
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

            <div v-if="tempConfig.imageText.contentLayoutStyle === 'xiaohongshu-hot'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>内容排版类型-小红书爆款风格</h3>
                <el-input
                  v-model="tempConfig.imageText.contentLayoutReference"
                  placeholder="输入参考小红书爆款排版的链接"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图风格类型选择</h3>
                <el-radio-group v-model="tempConfig.imageText.imageStyleType">
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

            <div v-if="['xhs-bigtext', 'xhs-keyword'].includes(tempConfig.imageText.imageStyleType)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图风格选择-小红书爆款参考链接</h3>
                <el-input
                  v-model="tempConfig.imageText.imageStyleReference"
                  placeholder="输入配图参考小红书链接"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>配图-比例</h3>
                <el-radio-group v-model="tempConfig.imageText.imageRatio">
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
                <el-radio-group v-model="tempConfig.imageText.coverStyleType">
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

            <div v-if="tempConfig.imageText.coverStyleType === 'info-graphic'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图-信息图类型</h3>
                <el-radio-group v-model="tempConfig.imageText.infoGraphicType">
                  <el-radio label="minimalist-tech">极简技术风</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['xhs-bigtext', 'xhs-keyword'].includes(tempConfig.imageText.coverStyleType)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图风格选择-小红书爆款风格</h3>
                <el-input
                  v-model="tempConfig.imageText.coverStyleReference"
                  placeholder="输入封面图参考链接"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>封面图-比例</h3>
                <el-radio-group v-model="tempConfig.imageText.coverImageRatio">
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
                <el-radio-group v-model="tempConfig.imageText.imageCount">
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
                <el-radio-group v-model="tempConfig.imageText.publishPlatform">
                  <el-radio label="xiaohongshu">小红书图文</el-radio>
                  <el-radio label="wechat">微信图文</el-radio>
                  <el-radio label="bilibili">B站图文</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>图文内容字数 <span class="required">*</span></h3>
                <el-radio-group v-model="tempConfig.imageText.contentWordCount" class="word-count-group">
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

            <div v-if="['external-ai-yes', 'external-ai-no'].includes(tempConfig.imageText.imageStyleType)" class="form-grid">
              <div class="form-section">
                <h3>配图风格类型选择-文章外图片-文章链接</h3>
                <el-input
                  v-model="tempConfig.imageText.externalArticleLink"
                  placeholder="输入文章链接"
                />
              </div>

              <div class="form-section">
                <h3>配图风格类型选择-文章外图片-文章来源</h3>
                <el-radio-group v-model="tempConfig.imageText.externalArticleSource">
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="zhihu">知乎</el-radio>
                </el-radio-group>
              </div>
            </div>
          </div>

          <!-- 文章配置 -->
          <div v-else-if="selectedContentType === 'article'" class="config-form article-content">
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>写作模式 <span class="required">*</span></h3>
                <el-radio-group v-model="tempConfig.article.writingMode">
                  <el-radio label="polish">润色</el-radio>
                  <el-radio label="imitate">仿写</el-radio>
                  <el-radio label="original">原创</el-radio>
                  <el-radio label="reprint">搬运排版</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(tempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-文章来源平台</h3>
                <el-radio-group v-model="tempConfig.article.sourcePlatform">
                  <el-radio label="zhihu">知乎</el-radio>
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="medium">Medium</el-radio>
                  <el-radio label="other">其他</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(tempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-链接</h3>
                <el-input
                  v-model="tempConfig.article.articleLink"
                  placeholder="请粘贴对标文章链接"
                />
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(tempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-文章发布平台</h3>
                <el-radio-group v-model="tempConfig.article.publishPlatform">
                  <el-radio label="zhihu">知乎</el-radio>
                  <el-radio label="juejin">掘金</el-radio>
                  <el-radio label="wechat">公众号</el-radio>
                  <el-radio label="medium">Medium</el-radio>
                  <el-radio label="other">其他</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="['polish', 'imitate', 'reprint'].includes(tempConfig.article.writingMode)" class="form-grid">
              <div class="form-section form-section-full">
                <h3>通用-排版风格</h3>
                <el-radio-group v-model="tempConfig.article.layoutStyle">
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
                <el-radio-group v-model="tempConfig.article.autoPublish">
                  <el-radio label="yes">是</el-radio>
                  <el-radio label="no">否</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'imitate'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>仿写-主题内容</h3>
                <el-input
                  v-model="tempConfig.article.imitateTopic"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入你的主题或者片段内容"
                />
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'imitate'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>仿写-文章长短</h3>
                <el-select v-model="tempConfig.article.imitateLength" placeholder="Select an option" style="width: 100%">
                  <el-option label="短篇 (1000-2000字)" value="short" />
                  <el-option label="中篇 (2000-5000字)" value="medium" />
                  <el-option label="长篇 (5000字以上)" value="long" />
                </el-select>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-深度研究领域关键词</h3>
                <el-input
                  v-model="tempConfig.article.originalKeywords"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入深度研究领域关键词"
                />
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-当前层次</h3>
                <el-radio-group v-model="tempConfig.article.originalLevel">
                  <el-radio label="novice">小白 (完全陌生)</el-radio>
                  <el-radio label="beginner">入门 (理论储备)</el-radio>
                  <el-radio label="junior">初级实操者 (有限经验)</el-radio>
                  <el-radio label="senior">资深应用者 (丰富经验)</el-radio>
                  <el-radio label="expert">领域权威 (专家级)</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-学习目的</h3>
                <el-radio-group v-model="tempConfig.article.originalPurpose">
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

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-文章是否需要配图</h3>
                <el-radio-group v-model="tempConfig.article.originalNeedImage">
                  <el-radio label="yes">是</el-radio>
                  <el-radio label="no">否</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-是否自动化</h3>
                <el-radio-group v-model="tempConfig.article.originalAutomation">
                  <el-radio label="auto">自动化</el-radio>
                  <el-radio label="step">分步骤</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-研究主题探究的深度</h3>
                <el-radio-group v-model="tempConfig.article.originalDepth">
                  <el-radio :label="1">1</el-radio>
                  <el-radio :label="2">2</el-radio>
                  <el-radio :label="3">3</el-radio>
                  <el-radio :label="5">5</el-radio>
                  <el-radio :label="10">10</el-radio>
                  <el-radio :label="20">20</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-报告期望字数</h3>
                <el-radio-group v-model="tempConfig.article.originalWordCount" class="word-count-group">
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

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-报告期望语言</h3>
                <el-radio-group v-model="tempConfig.article.originalLanguage">
                  <el-radio label="zh-cn">中文简体</el-radio>
                  <el-radio label="zh-tw">中文繁体</el-radio>
                  <el-radio label="en">英语</el-radio>
                </el-radio-group>
              </div>
            </div>

            <div v-if="tempConfig.article.writingMode === 'original'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>原创-提示词字数</h3>
                <el-radio-group v-model="tempConfig.article.originalPromptCount" class="word-count-group">
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

            <div v-if="['polish', 'imitate', 'reprint'].includes(tempConfig.article.writingMode) && tempConfig.article.publishPlatform === 'wechat'" class="form-grid">
              <div class="form-section form-section-full">
                <h3>润色&仿写&搬运排版-微信发布账号配置</h3>
                <el-radio-group v-model="tempConfig.article.wechatAccount">
                  <el-radio label="react">React中文社区</el-radio>
                  <el-radio label="biscuit">程序员饼干</el-radio>
                  <el-radio label="all">全部</el-radio>
                </el-radio-group>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <!-- 账号选择弹窗 -->
      <el-dialog
        v-model="accountDialogVisible"
        title="选择账号"
        width="600px"
        class="account-dialog"
        append-to-body
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

    
      
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button 
            v-if="dialogStep === 'config'"
            @click="dialogStep = 'select'" 
            size="large"
          >
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <el-button 
            @click="handleDialogCancel" 
            size="large"
          >
            取消
          </el-button>
          <el-button 
            v-if="dialogStep === 'select'"
            type="primary" 
            @click="goToConfigStep" 
            size="large"
            :disabled="!selectedContentType"
          >
            下一步
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button 
            v-else
            type="primary" 
            @click="confirmCreateTask" 
            size="large"
          >
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>
    </el-dialog>
  <!-- 话题选择弹窗（用于制作配置） -->
      <el-dialog
        v-model="topicDialogVisible"
        title="添加话题"
        width="600px"
        class="topic-dialog"
        append-to-body
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
            <el-button 
              type="primary" 
              @click="selectedContentType === 'video' ? addCustomTopicForVideo() : (isPublishTopicDialog ? addCustomTopicForPublish() : addCustomTopic())"
            >
              添加
            </el-button>
          </div>

          <!-- 推荐话题 -->
          <div class="recommended-topics">
            <h4>推荐话题</h4>
            <div class="topic-grid">
              <el-button
                v-for="topic in recommendedTopics"
                :key="topic"
                :type="getTopicButtonTypeForDialog(topic) === 'primary' ? 'primary' : 'default'"
                @click="toggleRecommendedTopicForDialog(topic)"
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
            <el-button 
              type="primary" 
              @click="selectedContentType === 'video' ? confirmTopicSelectionForVideo() : (isPublishTopicDialog ? confirmTopicSelectionForPublish() : confirmTopicSelection())"
            >
              确定
            </el-button>
          </div>
        </template>
      </el-dialog>
  <!-- 内容区域 -->
    <div class="production-content">
      <div class="production-tabs">
        <el-tabs v-model="activeContentTypeTab" class="production-tabs-nav">
          <el-tab-pane label="全部" name="all">
      <div class="task-list-container">
        <el-table
          ref="recordsTableRef"
                :data="filteredProductionRecords"
          :loading="productionListLoading"
          style="width: 100%"
          class="task-table"
          empty-text="暂无制作记录"
          :row-key="record => record.id"
          @selection-change="handleRecordSelectionChange"
        >
          <el-table-column type="selection" width="35" />
          <el-table-column prop="created_at" label="创建时间" width="150">
            <template #default="scope">
              <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-table-tooltip'">
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
          <el-table-column label="发布状态" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                {{ getPublishStatusLabel(scope.row.publish_status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="title" label="标题" min-width="150" class-name="title-column">
            <template #default="scope">
              <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          
          <el-table-column label="摘要" min-width="150" class-name="summary-column">
            <template #default="scope">
              <el-tooltip :content="scope.row.summary || formatContentPreview(scope.row.content, 60) || '—'" placement="top" :popper-class="'custom-table-tooltip'">
              <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) || '—' }}</div>
              </el-tooltip>
            </template>
          </el-table-column>

          <el-table-column label="正文" min-width="150" class-name="content-column">
            <template #default="scope">
              <el-tooltip :content="formatContentPreview(scope.row.content) || '—'" placement="top" :popper-class="'custom-table-tooltip'">
              <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) || '—' }}</div>
              </el-tooltip>
            </template>
          </el-table-column>

          <!-- 素材网址列（仅视频类型显示） -->
          <el-table-column label="素材网址" min-width="150" v-if="productionRecords.some(r => r.content_type === 'video')">
            <template #default="scope">
              <el-link
                v-if="scope.row.content_type === 'video' && scope.row.material_url"
                :href="scope.row.material_url"
                target="_blank"
                type="primary"
              >
                {{ scope.row.material_url }}
              </el-link>
              <span v-else-if="scope.row.content_type === 'video'">—</span>
              <span v-else>—</span>
            </template>
          </el-table-column>

          <!-- 生成内容链接列（仅视频类型显示） -->
          <el-table-column label="生成内容链接" min-width="150" v-if="productionRecords.some(r => r.content_type === 'video')">
            <template #default="scope">
              <el-link
                v-if="scope.row.content_type === 'video' && scope.row.video"
                :href="scope.row.video"
                target="_blank"
                type="success"
              >
                {{ scope.row.video }}
              </el-link>
              <span v-else-if="scope.row.content_type === 'video'">—</span>
              <span v-else>—</span>
            </template>
          </el-table-column>

          <!-- 图片/媒资链接列（非视频类型显示） -->
          <el-table-column label="图片/媒资链接" min-width="150" v-if="productionRecords.some(r => r.content_type !== 'video')">
            <template #default="scope">
              <!-- 非视频类型显示 media_url -->
              <div 
                v-if="scope.row.content_type !== 'video' && getImageUrls(scope.row).length > 0"
                class="image-preview-wrapper"
                @mouseenter="showPreview($event, getImageUrls(scope.row))"
                @mouseleave="hidePreview"
              >
                <el-link
                  :href="getFirstImageUrl(scope.row)"
                  target="_blank"
                  type="primary"
                  @click.stop
                >
                  {{ getFirstImageUrl(scope.row) }}
                </el-link>
                <div 
                  v-if="previewVisible && previewImages.length > 0"
                  class="image-preview-popup"
                  :style="previewStyle"
                  @mouseenter="cancelHidePreview"
                  @mouseleave="hidePreview"
                >
                  <div class="preview-images-grid">
                    <div 
                      v-for="(url, index) in previewImages" 
                      :key="index"
                      class="preview-image-item"
                      @click.stop="showImageViewer(url, previewImages)"
                    >
                      <img 
                        :src="url" 
                        class="preview-image"
                        @error="handleImageError"
                        @load="handleImageLoad"
                      />
                      <div class="preview-loading" v-if="!imageLoaded[url]">
                        <el-icon class="loading-icon"><Loading /></el-icon>
                      </div>
                      <div class="preview-click-hint">
                        <el-icon><ZoomIn /></el-icon>
                        <span>点击放大</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div 
                v-else-if="scope.row.content_type !== 'video' && scope.row.media_url"
                class="image-preview-wrapper"
                @mouseenter="showPreview($event, [scope.row.media_url])"
                @mouseleave="hidePreview"
              >
                <el-link
                :href="scope.row.media_url"
                target="_blank"
                type="primary"
              >
                {{ scope.row.media_url }}
              </el-link>
                <div 
                  v-if="previewVisible && currentPreviewUrl === scope.row.media_url"
                  class="image-preview-popup"
                  :style="previewStyle"
                >
                  <div class="preview-images-grid">
                    <div class="preview-image-item">
                      <img 
                        :src="previewImages[0]" 
                        class="preview-image"
                        @error="handleImageError"
                        @load="handleImageLoad"
                      />
                      <div class="preview-loading" v-if="!imageLoaded[previewImages[0]]">
                        <el-icon class="loading-icon"><Loading /></el-icon>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <span v-else>—</span>
            </template>
          </el-table-column>

          <el-table-column label="其他配置" min-width="100">
            <template #default="scope">
              <template v-if="scope.row.content_type === 'article' && scope.row.media_id">
                <el-tooltip :content="`article_media_id：${scope.row.media_id}`" placement="top" :popper-class="'custom-table-tooltip'">
                  <div class="text-ellipsis">article_media_id：{{ scope.row.media_id }}</div>
                </el-tooltip>
              </template>
              <template v-else-if="scope.row.content_type === 'image-text'">
                <div v-if="scope.row.height || scope.row.width" style="line-height: 1.5;">
                  <div v-if="scope.row.height">height：{{ scope.row.height }}</div>
                  <div v-if="scope.row.width">width：{{ scope.row.width }}</div>
                </div>
                <span v-else>—</span>
              </template>
              <span v-else>—</span>
            </template>
          </el-table-column>

        
          
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                :disabled="scope.row.isVirtual"
                @click="publishRecord(scope.row)"
              >
                <el-icon><Promotion /></el-icon>
                发布
              </el-button>
              <el-button 
                size="small" 
                :disabled="scope.row.isVirtual"
                @click="openRecordDetail(scope.row)"
              >
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
            <div class="task-list-container">
              <el-table
                ref="recordsTableRef"
                :data="filteredProductionRecords"
                :loading="productionListLoading"
                style="width: 100%"
                class="task-table"
                empty-text="暂无图文记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
                <el-table-column type="selection" width="20" />
          <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-table-tooltip'">
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
                <el-table-column prop="title" label="标题" min-width="150" class-name="title-column" show-overflow-tooltip />
                <el-table-column label="摘要" min-width="150" class-name="summary-column" show-overflow-tooltip>
                  <template #default="scope">
                    <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) || '—' }}</div>
                  </template>
                </el-table-column>
                <el-table-column label="正文" min-width="150" class-name="content-column" show-overflow-tooltip>
                  <template #default="scope">
                    <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) || '—' }}</div>
                  </template>
                </el-table-column>
                <el-table-column label="图片/媒资链接" min-width="150" class-name="media-link-column">
                  <template #default="scope">
                    <div class="media-links-container">
                      <template v-if="getImageUrls(scope.row).length > 0">
                        <div 
                          v-for="(url, index) in getImageUrls(scope.row)" 
                          :key="index"
                          class="media-link-item"
                        >
                          <div 
                            class="image-preview-wrapper"
                            @mouseenter="showPreview($event, [url])"
                            @mouseleave="hidePreview"
                          >
                            <el-link
                              :href="url"
                              target="_blank"
                              class="media-link"
                              @click.stop
                            >
                              <el-icon class="link-icon"><Link /></el-icon>
                              <span class="link-text">{{ url }}</span>
                            </el-link>
                            <div 
                              v-if="previewVisible && currentPreviewUrl === url"
                              class="image-preview-popup"
                              :style="previewStyle"
                              @mouseenter="cancelHidePreview"
                              @mouseleave="hidePreview"
                            >
                              <div class="preview-images-grid">
                                <div 
                                  class="preview-image-item"
                                  @click.stop="showImageViewer(url, [url])"
                                >
                                  <img 
                                    :src="url" 
                                    class="preview-image"
                                    @error="handleImageError"
                                    @load="handleImageLoad"
                                  />
                                  <div class="preview-loading" v-if="!imageLoaded[url]">
                                    <el-icon class="loading-icon"><Loading /></el-icon>
                                  </div>
                                  <div class="preview-click-hint">
                                    <el-icon><ZoomIn /></el-icon>
                                    <span>点击放大</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>
                      <template v-else-if="scope.row.media_url">
                        <div class="media-link-item">
                          <div 
                            class="image-preview-wrapper"
                            @mouseenter="showPreview($event, [scope.row.media_url])"
                            @mouseleave="hidePreview"
                          >
                          <el-link
                            :href="scope.row.media_url"
                            target="_blank"
                            class="media-link"
                          >
                            <el-icon class="link-icon"><Link /></el-icon>
                            <span class="link-text">{{ scope.row.media_url }}</span>
                          </el-link>
                            <div 
                              v-if="previewVisible && currentPreviewUrl === scope.row.media_url"
                              class="image-preview-popup"
                              :style="previewStyle"
                              @mouseenter="cancelHidePreview"
                              @mouseleave="hidePreview"
                            >
                              <div class="preview-images-grid">
                                <div 
                                  class="preview-image-item"
                                  @click.stop="showImageViewer(scope.row.media_url, [scope.row.media_url])"
                                >
                                  <img 
                                    :src="scope.row.media_url" 
                                    class="preview-image"
                                    @error="handleImageError"
                                    @load="handleImageLoad"
                                  />
                                  <div class="preview-loading" v-if="!imageLoaded[scope.row.media_url]">
                                    <el-icon class="loading-icon"><Loading /></el-icon>
                                  </div>
                                  <div class="preview-click-hint">
                                    <el-icon><ZoomIn /></el-icon>
                                    <span>点击放大</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>
                      <span v-else class="empty-placeholder">—</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="其他配置" min-width="100">
                  <template #default="scope">
                    <el-tooltip 
                      :content="scope.row.height || scope.row.width ? `height：${scope.row.height || '—'}\nwidth：${scope.row.width || '—'}` : '—'" 
                      placement="top" 
                      :popper-class="'custom-table-tooltip'"
                    >
                    <div v-if="scope.row.height || scope.row.width" style="line-height: 1.5;">
                      <div v-if="scope.row.height">height：{{ scope.row.height }}</div>
                      <div v-if="scope.row.width">width：{{ scope.row.width }}</div>
                    </div>
                    <span v-else>—</span>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="发布状态" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                {{ getPublishStatusLabel(scope.row.publish_status) }}
              </el-tag>
            </template>
          </el-table-column>
                <el-table-column label="操作" width="250" fixed="right">
                  <template #default="scope">
                    <el-button
                      type="primary"
                      size="small"
                      :disabled="scope.row.isVirtual"
                      @click="publishRecord(scope.row)"
                    >
                      <el-icon><Promotion /></el-icon>
                      发布
                    </el-button>
                    <el-button 
                      size="small" 
                      :disabled="scope.row.isVirtual"
                      @click="openRecordDetail(scope.row)"
                    >
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
            <div class="task-list-container">
              <el-table
                ref="recordsTableRef"
                :data="filteredProductionRecords"
                :loading="productionListLoading"
                style="width: 100%"
                class="task-table"
                empty-text="暂无文章记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
                <el-table-column type="selection" width="30" />
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-table-tooltip'">
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
                <el-table-column prop="title" label="标题" min-width="150" class-name="title-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.title || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                      <div class="text-ellipsis">{{ scope.row.title || '—' }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="content" label="内容" min-width="150" class-name="content-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.content || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                      <div class="text-ellipsis-3">{{ scope.row.content || '—' }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="desc" label="描述" min-width="150" class-name="summary-column">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.desc || '—'" placement="top" :popper-class="'custom-table-tooltip'">
                      <div class="text-ellipsis-3">{{ scope.row.desc || '—' }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="url" label="图片链接" min-width="150">
                  <template #default="scope">
                    <div 
                      v-if="scope.row.url"
                      class="image-preview-wrapper"
                      @mouseenter="showPreview($event, [scope.row.url])"
                      @mouseleave="hidePreview"
                    >
                      <el-link
                        :href="scope.row.url"
                        target="_blank"
                        type="primary"
                        @click.stop
                      >
                        {{ scope.row.url }}
                      </el-link>
                      <div 
                        v-if="previewVisible && currentPreviewUrl === scope.row.url"
                        class="image-preview-popup"
                        :style="previewStyle"
                        @mouseenter="cancelHidePreview"
                        @mouseleave="hidePreview"
                      >
                        <div class="preview-images-grid">
                          <div 
                            class="preview-image-item"
                            @click.stop="showImageViewer(scope.row.url, [scope.row.url])"
                          >
                            <img 
                              :src="scope.row.url" 
                              class="preview-image"
                              @error="handleImageError"
                              @load="handleImageLoad"
                            />
                            <div class="preview-loading" v-if="!imageLoaded[scope.row.url]">
                              <el-icon class="loading-icon"><Loading /></el-icon>
                            </div>
                            <div class="preview-click-hint">
                              <el-icon><ZoomIn /></el-icon>
                              <span>点击放大</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column prop="html" label="富文本" min-width="150">
                  <template #default="scope">
                    <el-tooltip 
                      :content="scope.row.html ? scope.row.html.replace(/<[^>]*>/g, '').slice(0, 200) : '—'" 
                      placement="top" 
                      :popper-class="'custom-table-tooltip'"
                      raw-content
                    >
                    <div v-if="scope.row.html" v-html="scope.row.html.slice(0, 200)" style="max-height: 100px; overflow: hidden; text-overflow: ellipsis;"></div>
                    <span v-else>—</span>
                    </el-tooltip>
                  </template>
                </el-table-column>
          <el-table-column label="发布状态" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                {{ getPublishStatusLabel(scope.row.publish_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                :disabled="scope.row.isVirtual"
                @click="publishRecord(scope.row)"
              >
                <el-icon><Promotion /></el-icon>
                发布
              </el-button>
              <el-button 
                size="small" 
                :disabled="scope.row.isVirtual"
                @click="openRecordDetail(scope.row)"
              >
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
            <div class="task-list-container">
              <el-table
                ref="recordsTableRef"
                :data="filteredProductionRecords"
                :loading="productionListLoading"
                style="width: 100%"
                class="task-table"
                empty-text="暂无视频记录"
                :row-key="record => record.id"
                @selection-change="handleRecordSelectionChange"
              >
                <el-table-column type="selection" width="30" />
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.created_at" placement="top" :popper-class="'custom-table-tooltip'">
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
                <el-table-column label="发布状态" width="90" align="center">
                  <template #default="scope">
                    <el-tag :type="getPublishStatusTagType(scope.row.publish_status)">
                      {{ getPublishStatusLabel(scope.row.publish_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="title" label="标题" min-width="150" class-name="title-column" show-overflow-tooltip />
                <el-table-column label="摘要" min-width="150" class-name="summary-column" show-overflow-tooltip>
                  <template #default="scope">
                    <div class="text-ellipsis-3">{{ scope.row.summary || formatContentPreview(scope.row.content, 60) || '—' }}</div>
                  </template>
                </el-table-column>
                <el-table-column label="正文" min-width="150" class-name="content-column" show-overflow-tooltip>
                  <template #default="scope">
                    <div class="text-ellipsis-3">{{ formatContentPreview(scope.row.content) || '—' }}</div>
                  </template>
                </el-table-column>
                <el-table-column label="素材网址" min-width="150">
                  <template #default="scope">
                    <el-link
                      v-if="scope.row.material_url"
                      :href="scope.row.material_url"
                      target="_blank"
                      type="primary"
                    >
                      {{ scope.row.material_url }}
                    </el-link>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="生成内容链接" min-width="150">
                  <template #default="scope">
                    <el-link
                      v-if="scope.row.video"
                      :href="scope.row.video"
                      target="_blank"
                      type="success"
                    >
                      {{ scope.row.video }}
                    </el-link>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
             
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                :disabled="scope.row.isVirtual"
                @click="publishRecord(scope.row)"
              >
                <el-icon><Promotion /></el-icon>
                发布
              </el-button>
              <el-button 
                size="small" 
                :disabled="scope.row.isVirtual"
                @click="openRecordDetail(scope.row)"
              >
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
    </div>
    <el-dialog
      v-model="recordDetailVisible"
      :width="currentRecordDetail?.content_type === 'image-text' ? '400px' : '720px'"
      :title="currentRecordDetail?.title || '制作详情'"
    >
      <div v-if="currentRecordDetail" class="record-detail">
        <!-- 图文类型：显示手机预览 -->
        <div v-if="currentRecordDetail.content_type === 'image-text'" class="preview-container">
          <MobileImageTextPreview
            :title="currentRecordDetail.title"
            :summary="currentRecordDetail.summary"
            :content="currentRecordDetail.content || ''"
            :images="parsedImageUrls"
            :author="currentRecordDetail.author || 'AI创作助手'"
            :created-at="currentRecordDetail.created_at"
            :source-label="getContentTypeLabel(currentRecordDetail.content_type)"
          />
        </div>
        
        <!-- 文章类型：显示手机预览 -->
        <div v-else-if="currentRecordDetail.content_type === 'article'" class="preview-container">
          <MobileArticlePreview
            :title="currentRecordDetail.title"
            :summary="currentRecordDetail.summary"
            :content="currentRecordDetail.content || ''"
            :created-at="currentRecordDetail.created_at"
            :cover-url="currentRecordDetail.media_url"
            :author="currentRecordDetail.author || 'AI创作助手'"
            :source-label="getContentTypeLabel(currentRecordDetail.content_type)"
          />
        </div>
        
        <!-- 其他类型：显示传统详情 -->
        <template v-else>
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
            <pre class="detail-content">{{ currentRecordDetail.content || '暂无内容' }}</pre>
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
        </template>
      </div>
      <template #footer>
        <el-button @click="recordDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 发布平台选择弹窗 -->
    <el-dialog
      v-model="publishPlatformDialogVisible"
      width="900px"
      class="publish-platform-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="true"
    >
      <template #header>
        <div class="dialog-header-custom">
          <h2>选择发布平台444</h2>
          <p style="font-size: 12px; color: #909399; margin-top: 4px;">
            内容类型: {{ currentPublishRecord?.content_type || '未知' }} | 
            记录ID: {{ currentPublishRecord?.id || '无' }}
          </p>
        </div>
      </template>
      <div class="publish-platform-content">
        <!-- 1. 发布平台选择 -->
        <div class="form-grid">
          <div class="form-section form-section-full">
            <h3>发布平台 <span class="required">*</span></h3>
            <!-- 视频类型：单选 -->
            <el-radio-group v-if="currentPublishRecord?.content_type === 'video'" v-model="publishPlatformForm.platform">
                <el-radio label="视频号">视频号</el-radio>
                <el-radio label="抖音">抖音</el-radio>
                <el-radio label="小红书">小红书</el-radio>
                <el-radio label="快手">快手</el-radio>
            </el-radio-group>
            <!-- 图文类型：多选 -->
            <el-checkbox-group v-else v-model="publishPlatformForm.platforms">
              <el-checkbox label="微信图文">微信图文</el-checkbox>
              <el-checkbox label="小红书">小红书</el-checkbox>
              <el-checkbox label="Facebook">Facebook</el-checkbox>
              <el-checkbox label="Instagram">Instagram</el-checkbox>
              <el-checkbox label="YouTube">YouTube</el-checkbox>
              <el-checkbox label="Thread">Thread</el-checkbox>
              <el-checkbox label="X">X</el-checkbox>
              <el-checkbox label="LinkedIn">LinkedIn</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
         <!-- 账号选择（所有类型通用） -->
         <div style="margin-top: 20px;">
          <div class="form-grid">
            <div class="form-section form-section-full">
              <h3>发布账号 <span class="required">*</span></h3>
              <!-- 视频类型：单个平台账号选择 -->
              <div v-if="currentPublishRecord?.content_type === 'video'" class="account-display">
                <div class="selected-accounts">
                  <el-tag
                    v-for="(accountId, index) in publishPlatformForm.selectedAccounts"
                    :key="index"
                    closable
                    @close="removePublishAccount(index)"
                    class="account-tag"
                  >
                    {{ getAccountDisplayNameById(accountId) }}
                  </el-tag>
                  <el-tag v-if="publishPlatformForm.selectedAccounts.length === 0" type="info" class="account-tag">
                    未选择账号
                  </el-tag>
                </div>
                <el-button 
                  type="primary" 
                  plain 
                  @click="openPublishAccountDialog"
                  class="select-account-btn"
                >
                  选择账号
                </el-button>
              </div>
              <!-- 图文类型：多平台账号选择 -->
              <template v-else-if="currentPublishRecord?.content_type === 'image-text'">
                <div class="account-display-multi">
                  <template v-if="publishPlatformForm.platforms && publishPlatformForm.platforms.length > 0">
                    <div v-for="platform in publishPlatformForm.platforms" :key="platform" class="platform-accounts">
                      <div class="platform-label">
                        <el-tag type="primary" size="small">{{ platform }}</el-tag>
                        <span class="account-count">
                          ({{ getSelectedAccountsForPlatform(platform).length }}个账号)
                        </span>
                      </div>
                      <div class="selected-accounts">
                        <el-tag
                          v-for="(accountId, index) in getSelectedAccountsForPlatform(platform)"
                          :key="`${platform}-${accountId}`"
                          closable
                          @close="removePublishAccountForPlatform(platform, index)"
                          class="account-tag"
                        >
                          {{ getAccountDisplayNameById(accountId) }}
                        </el-tag>
                        <el-tag v-if="getSelectedAccountsForPlatform(platform).length === 0" type="info" class="account-tag">
                          未选择账号
                        </el-tag>
                      </div>
                      <el-button 
                        type="primary" 
                        plain 
                        size="small"
                        @click="openPublishAccountDialogForPlatform(platform)"
                        class="select-account-btn"
                      >
                        选择{{ platform }}账号
                      </el-button>
                    </div>
                  </template>
                  <div v-else class="no-platforms">
                    <el-tag type="info">请先选择发布平台</el-tag>
                  </div>
                </div>
              </template>
              <!-- 其他类型：显示提示 -->
              <div v-else class="account-display-placeholder">
                <el-tag type="info">当前内容类型不支持账号选择</el-tag>
              </div>
            </div>
          </div>
        </div>

       
        <!-- 2. 标题输入 -->
        <div class="form-grid" style="margin-top: 20px;">
          <div class="form-section form-section-full">
            <h3>标题</h3>
            <el-input
              v-model="publishPlatformForm.title"
              type="textarea"
              :rows="3"
              placeholder="请输入标题"
              maxlength="500"
              show-word-limit
            />
          </div>
        </div>

        <!-- 3. 描述输入 -->
        <div class="form-grid" style="margin-top: 20px;">
          <div class="form-section form-section-full">
            <h3>描述</h3>
            <el-input
              v-model="publishPlatformForm.desc"
              type="textarea"
              :rows="4"
              placeholder="请输入描述"
              maxlength="2000"
              show-word-limit
            />
          </div>
        </div>

        <!-- 图文类型专用配置：摘要、正文、话题 -->
        <div v-if="currentPublishRecord?.content_type === 'image-text'" style="margin-top: 20px;">
          <!-- 1. 摘要配置 -->
          <div class="form-grid">
            <div class="form-section form-section-full">
              <h3>摘要</h3>
              <el-input
                v-model="publishPlatformForm.summary"
                type="textarea"
                :rows="3"
                placeholder="请输入摘要"
                maxlength="500"
                show-word-limit
              />
            </div>
          </div>

          <!-- 2. 正文配置 -->
          <div class="form-grid" style="margin-top: 20px;">
            <div class="form-section form-section-full">
              <h3>正文</h3>
              <el-input
                v-model="publishPlatformForm.content"
                type="textarea"
                :rows="6"
                placeholder="请输入正文内容"
                maxlength="5000"
                show-word-limit
              />
            </div>
          </div>

          <!-- 3. 话题选择配置 -->
          <div class="form-grid" style="margin-top: 20px;">
            <div class="form-section form-section-full">
              <h3>话题</h3>
              <div class="topic-display">
                <div class="selected-topics">
                  <el-tag
                    v-for="(topic, index) in publishPlatformForm.selectedTopics"
                    :key="index"
                    closable
                    @close="removePublishTopic(index)"
                    class="topic-tag"
                  >
                    #{{ topic }}
                  </el-tag>
                  <el-tag v-if="publishPlatformForm.selectedTopics.length === 0" type="info" class="topic-tag">
                    未选择话题
                  </el-tag>
                </div>
                <el-button 
                  type="primary" 
                  plain 
                  @click="openPublishTopicDialog"
                  class="select-topic-btn"
                >
                  选择话题
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 视频类型专用配置 -->
        <div v-if="currentPublishRecord?.content_type === 'video'" style="margin-top: 20px;">
          <!-- 1. 视频素材选择 -->
          <div class="form-grid">
            <div class="form-section form-section-full">
              <h3>视频素材 <span class="required">*</span></h3>
              <div class="video-material-display">
                <div class="selected-video">
                  <el-tag v-if="publishPlatformForm.selectedVideo" closable @close="publishPlatformForm.selectedVideo = null" class="video-tag">
                    {{ getVideoDisplayName(publishPlatformForm.selectedVideo) }}
                  </el-tag>
                  <el-tag v-else type="info" class="video-tag">
                    未选择视频
                  </el-tag>
                </div>
                <div class="video-actions">
                  <el-button 
                    type="primary" 
                    plain 
                    @click="openPublishVideoMaterialDialog"
                    class="select-video-btn"
                  >
                    从素材库选择
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. 话题选择配置 -->
          <div class="form-grid" style="margin-top: 20px;">
            <div class="form-section form-section-full">
              <h3>话题</h3>
              <div class="topic-display">
                <div class="selected-topics">
                  <el-tag
                    v-for="(topic, index) in publishPlatformForm.selectedTopics"
                    :key="index"
                    closable
                    @close="removePublishTopic(index)"
                    class="topic-tag"
                  >
                    #{{ topic }}
                  </el-tag>
                  <el-tag v-if="publishPlatformForm.selectedTopics.length === 0" type="info" class="topic-tag">
                    未选择话题
                  </el-tag>
                </div>
                <el-button 
                  type="primary" 
                  plain 
                  @click="openPublishTopicDialog"
                  class="select-topic-btn"
                >
                  选择话题
                </el-button>
              </div>
            </div>
          </div>

          <!-- 3. 草稿选项（仅视频号） -->
          <div v-if="publishPlatformForm.platform === '视频号'" class="form-grid">
            <div class="form-section form-section-full">
              <h3>草稿选项</h3>
              <el-checkbox
                v-model="publishPlatformForm.isDraft"
                label="视频号仅保存草稿(用手机发布)"
              />
            </div>
          </div>

          <!-- 4. 商品配置（仅抖音） -->
          <div v-if="publishPlatformForm.platform === '抖音'" class="form-grid">
            <div class="form-section">
              <h3>商品名称</h3>
              <el-input
                v-model="publishPlatformForm.productTitle"
                type="text"
                placeholder="请输入商品名称（可选）"
                maxlength="200"
              />
            </div>
            <div class="form-section">
              <h3>商品链接</h3>
              <el-input
                v-model="publishPlatformForm.productLink"
                type="text"
                placeholder="请输入商品链接（可选）"
                maxlength="500"
              />
            </div>
          </div>
        </div>
         <!-- 5. 定时发布配置 -->
         <div style="margin-top: 20px;">
          <div class="form-grid">
            <div class="form-section form-section-full">
              <h3>定时发布</h3>
              <el-switch
                v-model="publishPlatformForm.enableTimer"
                active-text="定时发布"
                inactive-text="立即发布"
              />
          </div>
          </div>

          <!-- 定时发布详细配置（仅在启用定时时显示） -->
          <template v-if="publishPlatformForm.enableTimer">
            <div class="form-grid">
              <div class="form-section">
                <h3>每天发布视频数</h3>
                <el-select v-model="publishPlatformForm.videosPerDay" placeholder="选择发布数量" style="width: 100%">
                  <el-option
                    v-for="num in Array.from({length: 10}, (_, i) => i + 1)"
                    :key="num"
                    :label="`${num}个`"
                    :value="num"
                  />
                </el-select>
              </div>
              <div class="form-section">
                <h3>开始发布天数</h3>
                <el-input-number
                  v-model="publishPlatformForm.startDays"
                  :min="0"
                  :max="30"
                  placeholder="从今天开始计算的天数"
                  style="width: 100%"
                />
              </div>
            </div>
            <div class="form-grid">
              <div class="form-section form-section-full">
                <h3>每天发布时间</h3>
                <el-time-picker
                  v-model="publishPlatformForm.dailyTimes"
                  is-range
                  range-separator="至"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  format="HH:mm"
                  value-format="HH:mm"
                  style="width: 100%"
                />
                <div style="margin-top: 8px; color: #909399; font-size: 12px;">
                  提示：设置时间范围，系统会在该范围内随机选择发布时间
                </div>
              </div>
            </div>
          </template>
        </div>

       
      </div>
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button @click="publishPlatformDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="confirmPublishWithPlatform" size="large">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 发布账号选择弹窗 -->
    <el-dialog
      v-model="publishAccountDialogVisible"
      :title="currentPublishRecord?.content_type === 'image-text' ? `选择${publishPlatformForm.platform}发布账号` : '选择发布账号'"
      width="600px"
      class="account-dialog"
      :close-on-click-modal="false"
      @opened="() => {
        console.log('🔍 [账号选择弹框] 弹框已打开')
        console.log('🔍 [账号选择弹框] publishPlatformForm.platform:', publishPlatformForm.platform)
        console.log('🔍 [账号选择弹框] availablePublishAccounts:', availablePublishAccounts.value.length)
        console.log('🔍 [账号选择弹框] availablePublishAccounts 详情:', availablePublishAccounts.value.map(acc => ({ id: acc.id, name: acc.name, platform: acc.platform })))
      }"
    >
      <div class="account-dialog-content">
        <div v-if="availablePublishAccounts.length === 0" class="empty-accounts">
          <el-empty 
            description="暂无可用账号" 
            :image-size="100"
          >
            <template #description>
              <p>当前平台（{{ currentPublishRecord?.content_type === 'image-text' ? publishPlatformForm.platform : publishPlatformForm.platform }}）暂无可用账号</p>
              <p style="font-size: 12px; color: #909399; margin-top: 8px;">
                请先在"账号管理"中添加{{ currentPublishRecord?.content_type === 'image-text' ? publishPlatformForm.platform : publishPlatformForm.platform }}账号
              </p>
            </template>
          </el-empty>
        </div>
        <!-- 视频类型：单选平台，直接使用数组 -->
        <el-checkbox-group v-else-if="currentPublishRecord?.content_type === 'video'" v-model="publishPlatformForm.selectedAccounts">
          <div class="account-list">
            <el-checkbox
              v-for="account in availablePublishAccounts"
              :key="account.id"
              :label="account.id"
              class="account-item"
            >
              <div class="account-info">
                <span class="account-name">{{ account.name }}</span>
                <el-tag :type="account.status === '正常' ? 'success' : 'danger'" size="small">
                  {{ account.status }}
                </el-tag>
              </div>
            </el-checkbox>
          </div>
        </el-checkbox-group>
        <!-- 图文类型：多选平台，按平台分组 -->
        <div v-else class="account-list-multi">
          <div v-if="!publishPlatformForm.platform" class="no-platform-selected">
            <el-empty 
              description="未选择平台" 
              :image-size="100"
            >
              <template #description>
                <p>请先选择发布平台</p>
              </template>
            </el-empty>
          </div>
          <div v-else-if="availablePublishAccounts.length === 0" class="empty-accounts">
          <el-empty 
            description="暂无可用账号" 
            :image-size="100"
          >
            <template #description>
              <p>当前平台（{{ publishPlatformForm.platform }}）暂无可用账号</p>
              <p style="font-size: 12px; color: #909399; margin-top: 8px;">
                请先在"账号管理"中添加{{ publishPlatformForm.platform }}账号
              </p>
            </template>
          </el-empty>
        </div>
          <el-checkbox-group v-else v-model="publishPlatformForm.selectedAccounts[publishPlatformForm.platform]">
          <div class="account-list">
            <el-checkbox
              v-for="account in availablePublishAccounts"
              :key="account.id"
              :label="account.id"
              class="account-item"
            >
              <div class="account-info">
                <span class="account-name">{{ account.name }}</span>
                <el-tag :type="account.status === '正常' ? 'success' : 'danger'" size="small">
                  {{ account.status }}
                </el-tag>
              </div>
            </el-checkbox>
          </div>
        </el-checkbox-group>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelPublishAccountSelection">取消</el-button>
          <el-button type="primary" @click="confirmPublishAccountSelection">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 图片放大查看器 -->
    <el-dialog
      v-model="imageViewerVisible"
      :show-close="true"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      width="90%"
      class="image-viewer-dialog"
      @close="closeImageViewer"
    >
      <template #header>
        <div class="image-viewer-header">
          <span class="image-viewer-title">
            {{ currentImageIndex + 1 }} / {{ imageViewerImages.length }}
          </span>
          <el-button
            type="primary"
            :icon="Close"
            circle
            @click="closeImageViewer"
            class="close-btn"
          />
        </div>
      </template>
      <div class="image-viewer-content">
        <div class="image-viewer-container">
          <el-button
            v-if="imageViewerImages.length > 1 && currentImageIndex > 0"
            class="nav-button prev-button"
            :icon="ArrowLeft"
            circle
            @click="prevImage"
          />
          <div class="image-wrapper">
            <img 
              :src="imageViewerUrl" 
              class="viewer-image"
              @error="handleImageError"
            />
          </div>
          <el-button
            v-if="imageViewerImages.length > 1 && currentImageIndex < imageViewerImages.length - 1"
            class="nav-button next-button"
            :icon="ArrowRight"
            circle
            @click="nextImage"
          />
        </div>
        <div v-if="imageViewerImages.length > 1" class="image-thumbnails">
          <div
            v-for="(url, index) in imageViewerImages"
            :key="index"
            :class="['thumbnail-item', { active: index === currentImageIndex }]"
            @click="currentImageIndex = index; imageViewerUrl = url"
          >
            <img :src="url" :alt="`缩略图 ${index + 1}`" />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 发布视频素材选择弹窗 -->
    <el-dialog
      v-model="publishVideoMaterialDialogVisible"
      title="选择生成素材（仅显示生成素材）"
      width="900px"
      class="material-dialog"
      :close-on-click-modal="false"
    >
      <div class="material-dialog-content">
        <div v-if="availableVideoMaterials.length === 0" class="empty-materials">
          <el-empty 
            description="暂无生成素材" 
            :image-size="100"
          >
            <template #description>
              <p>素材库中暂无生成素材</p>
              <p style="font-size: 12px; color: #909399; margin-top: 8px;">
                生成素材由n8n自动创建，请等待视频生成完成
              </p>
            </template>
          </el-empty>
        </div>
        <el-table
          v-else
          :data="availableVideoMaterials"
          style="width: 100%"
          max-height="500"
          highlight-current-row
          @current-change="handleVideoMaterialSelection"
          :row-class-name="getVideoMaterialRowClassName"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column label="预览" width="150" align="center">
            <template #default="scope">
              <div class="material-preview-cell">
                <video 
                  v-if="isVideoFile(scope.row.filename)"
                  :src="scope.row.uri || materialApi.getMaterialPreviewUrl(scope.row.file_path.split('/').pop())"
                  :class="{ 'selected-video-preview': isVideoMaterialSelected(scope.row) }"
                  style="width: 120px; height: 80px; object-fit: cover; border-radius: 4px; cursor: pointer;"
                  muted
                  @click="selectVideoMaterial(scope.row)"
                />
                <div v-else class="material-placeholder" :class="{ 'selected-video-preview': isVideoMaterialSelected(scope.row) }" style="width: 120px; height: 80px; display: flex; align-items: center; justify-content: center; background: #f5f7fa; border-radius: 4px;">
                  <el-icon :size="40"><VideoCamera /></el-icon>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="filename" label="文件名" min-width="200">
            <template #default="scope">
              <el-tooltip :content="scope.row.filename" placement="top" :popper-class="'custom-table-tooltip'">
                <div class="text-ellipsis">{{ scope.row.filename }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="120" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.source === '生成素材' ? 'success' : 'primary'" size="small">
                {{ scope.row.source || '本地上传' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="filesize" label="文件大小" width="120" align="center">
            <template #default="scope">
              {{ scope.row.filesize || 0 }} MB
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="上传时间" width="180" />
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button 
                :type="isVideoMaterialSelected(scope.row) ? 'success' : 'primary'"
                size="small"
                @click="selectVideoMaterial(scope.row)"
                :icon="isVideoMaterialSelected(scope.row) ? Check : null"
                :class="{ 'material-selected-btn': isVideoMaterialSelected(scope.row) }"
              >
                {{ isVideoMaterialSelected(scope.row) ? '已选择' : '选择' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="publishVideoMaterialDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmPublishVideoMaterialSelection"
            :disabled="!publishPlatformForm.selectedVideo"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 制作中心素材选择弹窗 -->
    <el-dialog
      v-model="productionMaterialDialogVisible"
      title="选择素材"
      width="900px"
      class="material-dialog"
      :close-on-click-modal="false"
    >
      <div class="material-dialog-content">
        <div v-if="availableProductionMaterials.length === 0" class="empty-materials">
          <el-empty 
            description="暂无视频素材" 
            :image-size="100"
          >
            <template #description>
              <p>素材库中暂无非生成素材的视频素材</p>
              <p style="font-size: 12px; color: #909399; margin-top: 8px;">
                请先在"素材管理"中上传视频素材（本地上传或谷歌存储上传）
              </p>
            </template>
          </el-empty>
        </div>
        <el-table
          v-else
          :data="availableProductionMaterials"
          style="width: 100%"
          max-height="500"
          highlight-current-row
          @current-change="handleProductionMaterialSelection"
          :row-class-name="getMaterialRowClassName"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column label="预览" width="150" align="center">
            <template #default="scope">
              <div class="material-preview-cell">
                <video 
                  v-if="isVideoFile(scope.row.filename)"
                  :src="materialApi.getMaterialPreviewUrl(scope.row.file_path.split('/').pop())"
                  style="width: 120px; height: 80px; object-fit: cover; border-radius: 4px; cursor: pointer;"
                  muted
                  @click="selectProductionMaterial(scope.row)"
                />
                <div v-else class="material-placeholder" style="width: 120px; height: 80px; display: flex; align-items: center; justify-content: center; background: #f5f7fa; border-radius: 4px;">
                  <el-icon :size="40"><VideoCamera /></el-icon>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="filename" label="文件名" min-width="200">
            <template #default="scope">
              <el-tooltip :content="scope.row.filename" placement="top" :popper-class="'custom-table-tooltip'">
                <div class="text-ellipsis">{{ scope.row.filename }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="filesize" label="文件大小" width="120" align="center">
            <template #default="scope">
              {{ scope.row.filesize }} MB
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="120" align="center">
            <template #default="scope">
              <el-tag size="small">{{ scope.row.source || '本地上传' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="scope">
              <el-button
                :type="isMaterialSelected(scope.row) ? 'success' : 'primary'"
                size="small"
                @click="selectProductionMaterial(scope.row)"
                :icon="isMaterialSelected(scope.row) ? Check : null"
                :class="{ 'material-selected-btn': isMaterialSelected(scope.row) }"
              >
                {{ isMaterialSelected(scope.row) ? '已选择' : '选择' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="productionMaterialDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmProductionMaterialSelection"
            :disabled="!selectedProductionMaterial"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { Upload, Plus, Close, Folder, VideoCamera, Picture, Document, Promotion, Check, CircleCheckFilled, ArrowLeft, ArrowRight, View, Edit, RefreshRight, Finished, Delete, FolderOpened, Link, Loading, ZoomIn } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { materialApi } from '@/api/material'
import { accountApi } from '@/api/account'
import MobileArticlePreview from '@/components/MobileArticlePreview.vue'
import MobileImageTextPreview from '@/components/MobileImageTextPreview.vue'
import { formatDateWithOffset, formatLocalDateTime, toBeijingTime } from '@/utils/dateTime'

// API base URL - 使用统一的工具函数
import { resolveApiBaseUrl } from '@/utils/apiConfig'

const apiBaseUrl = resolveApiBaseUrl()

// Authorization headers
const authHeaders = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
}))

// 当前激活的tab
const activeTab = ref('')

// tab计数器
let tabCounter = 1

// 内容类型相关
const contentTypeDialogVisible = ref(false)
const selectedContentType = ref('image-text')
const dialogStep = ref('select') // 'select' 或 'config'

// 临时配置数据（用于弹窗中的配置）
const tempConfig = reactive({
  video: {
    materialUrl: '', // 素材网址
    editingStyle: 'toxic-movie', // 剪辑风格，默认毒舌电影风格
    shotCount: 5, // 分镜数量
    language: 'zh-cn', // 语言
    copywriting: '', // 文案
    selectedAccounts: [], // 选中的账号列表
    selectedTopics: [], // 选中的话题列表
    scheduleEnabled: false, // 是否启用定时发布
    videosPerDay: 1, // 每天发布视频数量
    dailyTimes: ['10:00'], // 每天发布时间点
    startDays: 0 // 开始发布天数
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
    imageModel: 'qianwen',
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

const currentEditingTask = ref(null)

// 内容类型配置
const contentTypes = [
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
const selectedMaterials = ref([])
const currentUploadTab = ref(null)

// 批量发布相关状态
const batchPublishDialogVisible = ref(false)
const publishProgress = ref(0)
const publishResults = ref([])
const currentPublishingTab = ref(null)

// 素材相关状态
const materials = ref([])

// 平台配置
const platforms = [
  { key: 3, name: '抖音' },
  { key: 4, name: '快手' },
  { key: 2, name: '视频号' },
  { key: 1, name: '小红书' }
]

const defaultTabInit = {
  name: 'tab1',
  label: '制作1',
  contentType: 'article', // 内容类型：video, image-text, article
  fileList: [], // 后端返回的文件名列表
  displayFileList: [], // 用于显示的文件列表
  video: {
    materialUrl: '', // 素材网址
    editingStyle: 'toxic-movie', // 剪辑风格，默认毒舌电影风格
    shotCount: 5, // 分镜数量
    language: 'zh-cn', // 语言
    copywriting: '' // 文案
  },
  publishing: false, // 是否正在发布
  publishStatus: null, // 发布状态信息
  imageText: {
    contentSourceType: 'custom',
    imageModel: 'qianwen',
    inputContent: '',
    contentLayoutStyle: 'xiaohongshu-hot',
    contentLayoutReference: '',
    imageStyleType: 'ai-auto',
    imageStyleReference: '',
    coverStyleType: 'ai-auto',
    coverStyleReference: '',
    coverImageRatio: '1664*928',
    infoGraphicType: 'minimalist-tech',
    imageCount: 1,
    imageRatio: '1664*928',
    publishPlatform: 'xiaohongshu',
    contentWordCount: 500,
    externalArticleLink: '',
    externalArticleSource: 'juejin'
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

// tab页数据 - 初始为空数组，用户需要手动创建任务
const tabs = reactive([])

// 后端制作记录列表
const productionRecords = ref([])
const productionListLoading = ref(false)

// 内容类型Tab切换
const activeContentTypeTab = ref('all')

// 按内容类型过滤的记录
const filteredProductionRecords = computed(() => {
  if (activeContentTypeTab.value === 'all') {
    return productionRecords.value
  }
  return productionRecords.value.filter(record => record.content_type === activeContentTypeTab.value)
})
const recordDetailVisible = ref(false)
const currentRecordDetail = ref(null)
const recordsTableRef = ref(null)
const selectedRecords = ref([])
const listBatchPublishing = ref(false)
const publishingRecordId = ref(null)
const publishWebhookUrl = 'https://aicode.ltd/webhook/c155e570-faf5-4351-b1bd-7b908cf6db36'

/**
 * 解析图片URL列表
 * 支持多种格式：字符串、数组、JSON字符串
 */
const parsedImageUrls = computed(() => {
  if (!currentRecordDetail.value) return []
  
  const record = currentRecordDetail.value
  let urls = []
  
  // 优先使用images字段（如果是数组）
  if (record.images && Array.isArray(record.images)) {
    urls = record.images.filter(url => url && typeof url === 'string')
  }
  // 如果有media_url字段
  else if (record.media_url) {
    try {
      // 尝试解析为JSON数组
      const parsed = JSON.parse(record.media_url)
      if (Array.isArray(parsed)) {
        urls = parsed.filter(url => url && typeof url === 'string')
      } else if (typeof parsed === 'string') {
        urls = [parsed]
      }
    } catch {
      // 如果不是JSON，当作单个URL字符串处理
      // 检查是否包含多个URL（用逗号、分号或换行分隔）
      const urlString = record.media_url.trim()
      if (urlString.includes(',') || urlString.includes(';') || urlString.includes('\n')) {
        urls = urlString
          .split(/[,;\n]/)
          .map(url => url.trim())
          .filter(url => url && url.length > 0)
      } else {
        urls = [urlString]
      }
    }
  }
  
  return urls
})

/**
 * 获取记录的图片URL列表（用于列表显示）
 * @param {Object} record - 记录对象
 * @returns {Array} 图片URL数组
 */
const getImageUrls = (record) => {
  let urls = []
  
  // 文章类型优先使用 url 字段
  if (record.content_type === 'article') {
    const articleUrl = record.url || record.article_media_url || record.media_url
    if (articleUrl) {
      try {
        // 尝试解析为JSON数组
        const parsed = JSON.parse(articleUrl)
        if (Array.isArray(parsed)) {
          urls = parsed.filter(url => url && typeof url === 'string')
        } else if (typeof parsed === 'string') {
          urls = [parsed]
        }
      } catch {
        // 如果不是JSON，当作单个URL字符串处理
        // 检查是否包含多个URL（用逗号、分号或换行分隔）
        const urlString = articleUrl.trim()
        if (urlString.includes(',') || urlString.includes(';') || urlString.includes('\n')) {
          urls = urlString
            .split(/[,;\n]/)
            .map(url => url.trim())
            .filter(url => url && url.length > 0)
        } else {
          urls = [urlString]
        }
      }
    }
  }
  // 其他类型优先使用 media_ids 字段（如果是数组）
  else if (record.media_ids && Array.isArray(record.media_ids)) {
    urls = record.media_ids.filter(url => url && typeof url === 'string')
  }
  // 如果有 media_url 字段
  else if (record.media_url) {
    try {
      // 尝试解析为JSON数组
      const parsed = JSON.parse(record.media_url)
      if (Array.isArray(parsed)) {
        urls = parsed.filter(url => url && typeof url === 'string')
      } else if (typeof parsed === 'string') {
        urls = [parsed]
      }
    } catch {
      // 如果不是JSON，当作单个URL字符串处理
      // 检查是否包含多个URL（用逗号、分号或换行分隔）
      const urlString = record.media_url.trim()
      if (urlString.includes(',') || urlString.includes(';') || urlString.includes('\n')) {
        urls = urlString
          .split(/[,;\n]/)
          .map(url => url.trim())
          .filter(url => url && url.length > 0)
      } else {
        urls = [urlString]
      }
    }
  }
  
  return urls
}

/**
 * 获取第一个图片URL（用于显示链接文本）
 * @param {Object} record - 记录对象
 * @returns {String} 第一个图片URL
 */
const getFirstImageUrl = (record) => {
  // 文章类型优先使用 url 字段
  if (record.content_type === 'article') {
    const articleUrl = record.url || record.article_media_url || record.media_url
    if (articleUrl) {
      return articleUrl
    }
  }
  
  const urls = getImageUrls(record)
  return urls.length > 0 ? urls[0] : (record.media_url || '')
}

/**
 * 处理图片加载错误
 */
const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// 图片预览相关状态
const previewVisible = ref(false)
const previewImages = ref([])
const previewStyle = ref({})
const imageLoaded = ref({})
const currentPreviewUrl = ref('') // 当前正在预览的URL
let hidePreviewTimer = null // 隐藏预览的定时器

// 图片放大查看相关状态
const imageViewerVisible = ref(false)
const imageViewerUrl = ref('')
const imageViewerImages = ref([])
const currentImageIndex = ref(0)

/**
 * 显示图片预览
 */
const showPreview = (event, images) => {
  if (!images || images.length === 0) {
    console.log('预览：没有图片')
    return
  }
  
  // 获取第一个图片URL作为标识
  const firstUrl = images[0]
  currentPreviewUrl.value = firstUrl
  previewImages.value = images
  previewVisible.value = true
  
  console.log('预览：显示预览', {
    firstUrl,
    imagesCount: images.length,
    previewVisible: previewVisible.value,
    currentPreviewUrl: currentPreviewUrl.value
  })
  
  // 计算预览框位置
  const rect = event.currentTarget.getBoundingClientRect()
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft
  
  // 预览框大小（根据图片数量调整）
  const imageCount = Math.min(images.length, 4) // 最多显示4张
  const cols = imageCount <= 1 ? 1 : imageCount <= 2 ? 2 : 2
  const rows = Math.ceil(imageCount / cols)
  const previewWidth = cols * 100 + (cols - 1) * 8 + 16 // 图片宽度 + 间距 + 内边距
  const previewHeight = rows * 100 + (rows - 1) * 8 + 16
  
  // 计算位置：默认显示在链接上方，居中对齐
  // 水平居中：链接中心 - 预览框宽度的一半
  let left = rect.left + scrollLeft + (rect.width / 2) - (previewWidth / 2)
  // 垂直位置：链接上方，留出10px间距
  let top = rect.top + scrollTop - previewHeight - 10
  
  // 如果上方空间不足，显示在链接下方
  if (top < scrollTop) {
    top = rect.bottom + scrollTop + 10
  }
  
  // 确保不超出屏幕左侧
  if (left < scrollLeft) {
    left = scrollLeft + 10
  }
  
  // 确保不超出屏幕右侧
  if (left + previewWidth > window.innerWidth + scrollLeft) {
    left = window.innerWidth + scrollLeft - previewWidth - 10
  }
  
  // 确保不超出屏幕底部（如果显示在下方时）
  if (top + previewHeight > window.innerHeight + scrollTop) {
    top = window.innerHeight + scrollTop - previewHeight - 10
  }
  
  previewStyle.value = {
    position: 'fixed',
    left: `${left}px`,
    top: `${top}px`,
    zIndex: 9999
  }
}

/**
 * 隐藏图片预览（带延迟，允许鼠标移动到预览组件上）
 */
const hidePreview = () => {
  // 清除之前的定时器
  if (hidePreviewTimer) {
    clearTimeout(hidePreviewTimer)
  }
  
  // 延迟隐藏，给鼠标时间移动到预览组件上
  hidePreviewTimer = setTimeout(() => {
    previewVisible.value = false
    previewImages.value = []
    currentPreviewUrl.value = ''
    hidePreviewTimer = null
  }, 200) // 200ms 延迟
}

/**
 * 取消隐藏预览（当鼠标进入预览组件时调用）
 */
const cancelHidePreview = () => {
  if (hidePreviewTimer) {
    clearTimeout(hidePreviewTimer)
    hidePreviewTimer = null
  }
}

/**
 * 处理图片加载完成
 */
const handleImageLoad = (event) => {
  const url = event.target.src
  imageLoaded.value[url] = true
}

/**
 * 点击图片放大查看
 */
const showImageViewer = (url, allImages = []) => {
  imageViewerImages.value = allImages.length > 0 ? allImages : [url]
  currentImageIndex.value = allImages.length > 0 ? allImages.indexOf(url) : 0
  imageViewerUrl.value = url
  imageViewerVisible.value = true
}

/**
 * 关闭图片查看器
 */
const closeImageViewer = () => {
  imageViewerVisible.value = false
  imageViewerUrl.value = ''
  imageViewerImages.value = []
  currentImageIndex.value = 0
}

/**
 * 切换到上一张图片
 */
const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
    imageViewerUrl.value = imageViewerImages.value[currentImageIndex.value]
  }
}

/**
 * 切换到下一张图片
 */
const nextImage = () => {
  if (currentImageIndex.value < imageViewerImages.value.length - 1) {
    currentImageIndex.value++
    imageViewerUrl.value = imageViewerImages.value[currentImageIndex.value]
  }
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
    'creating': 'warning',  // 制作中
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
    'creating': '制作中',  // 制作中
    'success': '成功',
    'failed': '失败'
  }
  return labelMap[status] || '待发布'
}

/**
 * 更新制作中心记录的状态
 * @param {number} recordId - 记录ID
 * @param {string} status - 状态值: pending, processing, success, failed
 */
const updateProductionStatus = async (recordId, status) => {
  try {
    const response = await fetch(`${apiBaseUrl}/production/records/${recordId}/status`, {
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
    console.error('更新制作中心状态失败:', error)
  }
}

const fetchProductionRecords = async (contentType = '') => {
  const normalized = (contentType || '').toLowerCase()
  const query = normalized && normalized !== 'all' ? `?content_type=${normalized}` : ''
  productionListLoading.value = true
  try {
    const response = await fetch(`${apiBaseUrl}/production/records${query}`)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    const result = await response.json()
    if (result.code !== 200) {
      throw new Error(result.msg || '获取制作记录失败')
    }
    productionRecords.value = result.data?.items || []
    clearRecordSelection()
  } catch (error) {
    console.error('获取制作记录失败:', error)
    ElMessage.error(error.message || '获取制作记录失败')
  } finally {
    productionListLoading.value = false
  }
}

const openRecordDetail = (record) => {
  currentRecordDetail.value = record
  recordDetailVisible.value = true
}

const refreshProductionRecords = () => {
  if (productionListLoading.value) return
  fetchProductionRecords()
}

// 轮询监听图文记录
let imageTextPollingInterval = null
const startImageTextPolling = () => {
  // 如果已经有轮询在运行，先清除
  if (imageTextPollingInterval) {
    clearInterval(imageTextPollingInterval)
  }
  
  // 每20秒检查一次图文记录
  imageTextPollingInterval = setInterval(async () => {
    try {
      // 静默刷新，不显示loading
      const response = await fetch(`${apiBaseUrl}/production/records?content_type=image-text`)
      if (response.ok) {
        const result = await response.json()
        if (result.code === 200) {
          const newRecords = result.data?.items || []
          
          // 获取当前的图文记录（包括虚拟记录）
          const currentImageTextRecords = productionRecords.value.filter(r => r.content_type === 'image-text')
          const currentRealRecords = currentImageTextRecords.filter(r => !r.isVirtual)
          const virtualRecords = currentImageTextRecords.filter(r => r.isVirtual)
          
          // 检查是否有新记录或记录有更新
          const currentRealIds = new Set(currentRealRecords.map(r => r.id))
          const newRealIds = new Set(newRecords.map(r => r.id))
          
          // 检查是否有新记录
          const hasNewRecords = Array.from(newRealIds).some(id => !currentRealIds.has(id))
          
          // 检查是否有记录更新
          const hasUpdatedRecords = newRecords.some(newRecord => {
            const oldRecord = currentRealRecords.find(r => r.id === newRecord.id)
            return oldRecord && (
              oldRecord.title !== newRecord.title ||
              oldRecord.content !== newRecord.content ||
              oldRecord.publish_status !== newRecord.publish_status ||
              oldRecord.summary !== newRecord.summary
            )
          })
          
          // 如果有新记录或记录有更新，更新列表
          if (hasNewRecords || hasUpdatedRecords) {
            // 获取其他类型的记录
            const otherRecords = productionRecords.value.filter(r => r.content_type !== 'image-text')
            
            // 合并图文记录：所有真实记录 + 虚拟记录（虚拟记录会在pollForRecordCompletion中被替换）
            const allImageTextRecords = [...newRecords]
            
            // 检查是否有新完成的记录（标题不是"制作中..."）
            const hasNewCompletedRecord = newRecords.some(realRecord => 
              !currentRealIds.has(realRecord.id) &&
              realRecord.title && 
              realRecord.title.trim() !== '' && 
              realRecord.title !== '制作中...'
            )
            
            // 保留所有虚拟记录（它们会在有对应真实记录时被pollForRecordCompletion替换）
            virtualRecords.forEach(virtualRecord => {
              // 如果没有新完成的记录，保留虚拟记录
              // 如果有新完成的记录，虚拟记录会被pollForRecordCompletion替换，这里不添加
              if (!hasNewCompletedRecord) {
                allImageTextRecords.push(virtualRecord)
              }
            })
            
            // 按创建时间倒序排序
            allImageTextRecords.sort((a, b) => {
              const timeA = new Date(a.created_at || 0).getTime()
              const timeB = new Date(b.created_at || 0).getTime()
              return timeB - timeA
            })
            
            // 更新列表：其他类型记录 + 图文记录
            productionRecords.value = [...otherRecords, ...allImageTextRecords]
            
            console.log('✅ 图文记录列表已自动更新', { 
              hasNewRecords, 
              hasUpdatedRecords,
              totalRecords: allImageTextRecords.length,
              virtualRecordsCount: virtualRecords.length
            })
            
            // 如果检测到新完成的记录（说明n8n已经创建了记录），停止轮询
            if (hasNewCompletedRecord) {
              console.log('✅ 检测到新完成的图文记录，停止轮询监听')
              stopImageTextPolling()
            }
          }
          
          // 检查是否还有虚拟记录，如果没有虚拟记录，停止轮询
          const remainingVirtualRecords = productionRecords.value.filter(r => 
            r.content_type === 'image-text' && r.isVirtual
          )
          if (remainingVirtualRecords.length === 0 && imageTextPollingInterval) {
            console.log('✅ 没有虚拟记录等待中，停止轮询监听')
            stopImageTextPolling()
          }
        }
      }
    } catch (error) {
      console.error('轮询检查图文记录失败:', error)
      // 静默失败，不显示错误提示
    }
  }, 20000) // 每20秒检查一次
  
  console.log('✅ 已启动图文记录轮询监听（每20秒检查一次）')
}

const stopImageTextPolling = () => {
  if (imageTextPollingInterval) {
    clearInterval(imageTextPollingInterval)
    imageTextPollingInterval = null
    console.log('✅ 已停止图文记录轮询监听')
  }
}

// 轮询监听文章记录
let articlePollingInterval = null
const startArticlePolling = () => {
  // 如果已经有轮询在运行，先清除
  if (articlePollingInterval) {
    clearInterval(articlePollingInterval)
  }
  
  // 每20秒检查一次文章记录
  articlePollingInterval = setInterval(async () => {
    try {
      // 静默刷新，不显示loading
      const response = await fetch(`${apiBaseUrl}/production/records?content_type=article`)
      if (response.ok) {
        const result = await response.json()
        if (result.code === 200) {
          const newRecords = result.data?.items || []
          
          // 获取当前的文章记录（包括虚拟记录）
          const currentArticleRecords = productionRecords.value.filter(r => r.content_type === 'article')
          const currentRealRecords = currentArticleRecords.filter(r => !r.isVirtual)
          const virtualRecords = currentArticleRecords.filter(r => r.isVirtual)
          
          // 检查是否有新记录或记录有更新
          const currentRealIds = new Set(currentRealRecords.map(r => r.id))
          const newRealIds = new Set(newRecords.map(r => r.id))
          
          // 检查是否有新记录
          const hasNewRecords = Array.from(newRealIds).some(id => !currentRealIds.has(id))
          
          // 检查是否有记录更新
          const hasUpdatedRecords = newRecords.some(newRecord => {
            const oldRecord = currentRealRecords.find(r => r.id === newRecord.id)
            return oldRecord && (
              oldRecord.title !== newRecord.title ||
              oldRecord.content !== newRecord.content ||
              oldRecord.publish_status !== newRecord.publish_status ||
              oldRecord.summary !== newRecord.summary
            )
          })
          
          // 如果有新记录或记录有更新，更新列表
          if (hasNewRecords || hasUpdatedRecords) {
            // 获取其他类型的记录
            const otherRecords = productionRecords.value.filter(r => r.content_type !== 'article')
            
            // 合并文章记录：所有真实记录 + 虚拟记录
            const allArticleRecords = [...newRecords]
            
            // 检查是否有新完成的记录（标题不是"制作中..."）
            const hasNewCompletedRecord = newRecords.some(realRecord => 
              !currentRealIds.has(realRecord.id) &&
              realRecord.title && 
              realRecord.title.trim() !== '' && 
              realRecord.title !== '制作中...'
            )
            
            // 保留所有虚拟记录（它们会在有对应真实记录时被pollForRecordCompletion替换）
            virtualRecords.forEach(virtualRecord => {
              // 如果没有新完成的记录，保留虚拟记录
              if (!hasNewCompletedRecord) {
                allArticleRecords.push(virtualRecord)
              }
            })
            
            // 按创建时间倒序排序
            allArticleRecords.sort((a, b) => {
              const timeA = new Date(a.created_at || 0).getTime()
              const timeB = new Date(b.created_at || 0).getTime()
              return timeB - timeA
            })
            
            // 更新列表：其他类型记录 + 文章记录
            productionRecords.value = [...otherRecords, ...allArticleRecords]
            
            console.log('✅ 文章记录列表已自动更新', { 
              hasNewRecords, 
              hasUpdatedRecords,
              totalRecords: allArticleRecords.length,
              virtualRecordsCount: virtualRecords.length
            })
            
            // 如果检测到新完成的记录（说明n8n已经创建了记录），停止轮询
            if (hasNewCompletedRecord) {
              console.log('✅ 检测到新完成的文章记录，停止轮询监听')
              stopArticlePolling()
            }
          }
          
          // 检查是否还有虚拟记录，如果没有虚拟记录，停止轮询
          const remainingVirtualRecords = productionRecords.value.filter(r => 
            r.content_type === 'article' && r.isVirtual
          )
          if (remainingVirtualRecords.length === 0 && articlePollingInterval) {
            console.log('✅ 没有虚拟记录等待中，停止文章轮询监听')
            stopArticlePolling()
          }
        }
      }
    } catch (error) {
      console.error('轮询检查文章记录失败:', error)
      // 静默失败，不显示错误提示
    }
  }, 20000) // 每20秒检查一次
  
  console.log('✅ 已启动文章记录轮询监听（每20秒检查一次）')
}

const stopArticlePolling = () => {
  if (articlePollingInterval) {
    clearInterval(articlePollingInterval)
    articlePollingInterval = null
    console.log('✅ 已停止文章记录轮询监听')
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

// 发布平台选择弹窗
const publishPlatformDialogVisible = ref(false)
const publishAccountDialogVisible = ref(false)
const publishVideoMaterialDialogVisible = ref(false)
const currentPublishRecord = ref(null)
const publishPlatformForm = reactive({
  platform: '微信图文', // 视频类型使用字符串，图文类型使用数组
  platforms: [], // 图文类型多选平台（数组）
  // 标题和描述
  title: '',
  desc: '',
  // 图文类型专用：摘要、正文、话题
  summary: '', // 摘要
  content: '', // 正文
  selectedTopics: [], // 话题列表
  // 账号选择（按平台分组）
  selectedAccounts: {}, // 格式: { '微信图文': [accountId1, accountId2], '小红书': [accountId3] }
  // 视频素材选择
  selectedVideo: null, // 选中的视频素材（可以是记录中的视频或素材库中的视频）
  useMaterialLibrary: false, // 是否使用素材库
  // 定时发布配置
  enableTimer: false,
  videosPerDay: 1,
  dailyTimes: ['10:00'],
  startDays: 0,
  // 草稿选项（仅视频号）
  isDraft: false,
  // 商品配置（仅抖音）
  productLink: '',
  productTitle: '',
  // 分类（可选）
  category: 0
})

// 获取可用发布账号（根据选择的平台过滤）
const availablePublishAccounts = computed(() => {
  const record = currentPublishRecord.value
  if (!record) return []
  
  // 视频类型：使用单个平台
  if (record.content_type === 'video') {
  if (!publishPlatformForm.platform) {
    return []
  }
  const filtered = accountStore.accounts.filter(
    acc => acc.platform === publishPlatformForm.platform
  )
  return filtered
  }
  
  // 图文类型：使用多个平台
  if (record.content_type === 'image-text') {
    // 如果通过 openPublishAccountDialogForPlatform 设置了当前平台，只返回该平台的账号
    if (publishPlatformForm.platform) {
      const filtered = accountStore.accounts.filter(
        acc => acc.platform === publishPlatformForm.platform
      )
      return filtered
    }
    // 否则返回所有选中平台的账号
    if (!publishPlatformForm.platforms || publishPlatformForm.platforms.length === 0) {
      return []
    }
    const filtered = accountStore.accounts.filter(
      acc => publishPlatformForm.platforms.includes(acc.platform)
    )
    return filtered
  }
  
  return []
})

// 根据账号ID获取显示名称
const getAccountDisplayNameById = (accountId) => {
  const account = accountStore.accounts.find(acc => acc.id === accountId)
  return account ? account.name : `账号${accountId}`
}

// 打开发布账号选择对话框
const openPublishAccountDialog = async () => {
  // 确保账号列表已加载
  if (accountStore.accounts.length === 0) {
    try {
      console.log('📥 账号列表为空，正在加载账号列表...')
      const response = await accountApi.getAccounts()
      if (response.code === 200 && response.data) {
        accountStore.setAccounts(response.data)
        console.log('✅ 账号列表加载成功，总数:', accountStore.accounts.length)
      }
    } catch (error) {
      console.error('加载账号列表失败:', error)
    }
  }
  
  console.log('打开账号选择对话框:', {
    platform: publishPlatformForm.platform,
    availableAccounts: availablePublishAccounts.value.length,
    allAccounts: accountStore.accounts.length,
    accounts: accountStore.accounts.map(acc => ({ id: acc.id, name: acc.name, platform: acc.platform }))
  })
  publishAccountDialogVisible.value = true
}

// 监听平台切换，确保账号列表已加载（视频类型）
watch(() => publishPlatformForm.platform, async (newPlatform) => {
  const record = currentPublishRecord.value
  // 只监听视频类型的平台切换
  if (record && record.content_type === 'video' && newPlatform && accountStore.accounts.length === 0) {
    try {
      console.log('📥 平台切换，账号列表为空，正在加载账号列表...')
      const response = await accountApi.getAccounts()
      if (response.code === 200 && response.data) {
        accountStore.setAccounts(response.data)
        console.log('✅ 账号列表加载成功，总数:', accountStore.accounts.length)
        console.log('📋 当前平台可用账号:', availablePublishAccounts.value.map(acc => acc.name))
      }
    } catch (error) {
      console.error('加载账号列表失败:', error)
    }
  } else if (newPlatform && record && record.content_type === 'video') {
    console.log('📋 平台切换为:', newPlatform, '可用账号:', availablePublishAccounts.value.map(acc => acc.name))
  }
})

// 监听图文类型平台数组变化，确保账号列表已加载
watch(() => publishPlatformForm.platforms, async (newPlatforms) => {
  const record = currentPublishRecord.value
  if (record && record.content_type === 'image-text' && newPlatforms && newPlatforms.length > 0 && accountStore.accounts.length === 0) {
    try {
      console.log('📥 图文平台选择变化，账号列表为空，正在加载账号列表...')
      const response = await accountApi.getAccounts()
      if (response.code === 200 && response.data) {
        accountStore.setAccounts(response.data)
        console.log('✅ 账号列表加载成功，总数:', accountStore.accounts.length)
      }
    } catch (error) {
      console.error('加载账号列表失败:', error)
    }
  }
}, { deep: true })

// 取消发布账号选择
const cancelPublishAccountSelection = () => {
  const record = currentPublishRecord.value
  // 图文类型：清除临时设置的平台值（避免影响后续操作）
  if (record && record.content_type === 'image-text') {
    publishPlatformForm.platform = ''
  }
  publishAccountDialogVisible.value = false
}

// 确认发布账号选择
const confirmPublishAccountSelection = () => {
  const record = currentPublishRecord.value
  if (!record) {
    cancelPublishAccountSelection()
    return
  }
  
  // 视频类型：检查数组长度
  if (record.content_type === 'video') {
  if (publishPlatformForm.selectedAccounts.length === 0) {
    ElMessage.warning('请至少选择一个账号')
    return
  }
  } else {
    // 图文类型：检查当前平台的账号
    const currentPlatform = publishPlatformForm.platform
    if (!publishPlatformForm.selectedAccounts[currentPlatform] || publishPlatformForm.selectedAccounts[currentPlatform].length === 0) {
      ElMessage.warning(`请至少为${currentPlatform}选择一个账号`)
      return
    }
  }
  
  // 图文类型：清除临时设置的平台值（避免影响后续操作）
  if (record.content_type === 'image-text') {
    publishPlatformForm.platform = ''
  }
  
  publishAccountDialogVisible.value = false
}

// 移除发布账号（视频类型）
const removePublishAccount = (index) => {
  publishPlatformForm.selectedAccounts.splice(index, 1)
}

// 获取指定平台的已选账号（图文类型）
const getSelectedAccountsForPlatform = (platform) => {
  if (!publishPlatformForm.selectedAccounts[platform]) {
    return []
  }
  return publishPlatformForm.selectedAccounts[platform]
}

// 移除指定平台的账号（图文类型）
const removePublishAccountForPlatform = (platform, index) => {
  if (publishPlatformForm.selectedAccounts[platform]) {
    publishPlatformForm.selectedAccounts[platform].splice(index, 1)
  }
}

// 为指定平台打开发布账号选择对话框（图文类型）
const openPublishAccountDialogForPlatform = async (platform) => {
  console.log('🔍 [账号选择] 为平台打开发布账号选择对话框，平台:', platform)
  
  // 先设置当前选择的平台（用于账号选择对话框）
  publishPlatformForm.platform = platform
  console.log('🔍 [账号选择] 平台已设置为:', publishPlatformForm.platform)
  
  // 确保该平台的账号数组已初始化
  if (!publishPlatformForm.selectedAccounts[platform]) {
    publishPlatformForm.selectedAccounts[platform] = []
  }
  
  // 确保账号列表已加载
  if (accountStore.accounts.length === 0) {
    try {
      console.log('📥 [账号选择] 加载账号列表...')
      const response = await accountApi.getAccounts()
      if (response.code === 200 && response.data) {
        accountStore.setAccounts(response.data)
        console.log('✅ [账号选择] 账号列表加载成功，总数:', accountStore.accounts.length)
      } else {
        console.error('❌ [账号选择] 账号列表加载失败')
        ElMessage.error('加载账号列表失败')
        return
      }
    } catch (error) {
      console.error('❌ [账号选择] 加载账号列表失败:', error)
      ElMessage.error('加载账号列表失败')
      return
    }
  }
  
  // 检查可用账号
  const availableAccounts = accountStore.accounts.filter(acc => acc.platform === platform)
  console.log('🔍 [账号选择] 可用账号数量:', availableAccounts.length)
  
  if (availableAccounts.length === 0) {
    ElMessage.warning(`当前没有可用的${platform}账号，请先在账号管理中添加`)
    return
  }
  
  // 等待响应式更新完成
  await nextTick()
  
  // 打开弹框
  publishAccountDialogVisible.value = true
  console.log('✅ [账号选择] 账号选择弹框已打开')
}

// 获取可用视频素材（从素材库中过滤视频文件，只显示生成素材）
// 注意：这个计算属性用于制作中心发布弹框的素材选择，只显示生成素材
const availableVideoMaterials = computed(() => {
  const materials = appStore.materials || []
  return materials.filter(material => {
    // 只显示生成素材
    if (material.source !== '生成素材') {
      return false
    }
    // 过滤视频文件
    const filename = (material.filename || '').toLowerCase()
    return filename.endsWith('.mp4') || 
           filename.endsWith('.mov') || 
           filename.endsWith('.avi') || 
           filename.endsWith('.mkv') ||
           filename.endsWith('.m4v')
  })
})

// 获取可用视频素材（从素材库中过滤视频文件，只显示非生成素材）
// 注意：这个计算属性用于制作中心新建任务时的素材选择，只显示非生成素材（本地上传、谷歌存储上传等）
const availableProductionMaterials = computed(() => {
  const materials = appStore.materials || []
  return materials.filter(material => {
    // 只显示非生成素材（排除生成素材）
    if (material.source === '生成素材') {
      return false
    }
    // 过滤视频文件
    const filename = (material.filename || '').toLowerCase()
    return filename.endsWith('.mp4') || 
           filename.endsWith('.mov') || 
           filename.endsWith('.avi') || 
           filename.endsWith('.mkv') ||
           filename.endsWith('.m4v')
  })
})

// 判断是否为视频文件
const isVideoFile = (filename) => {
  if (!filename) return false
  const lower = filename.toLowerCase()
  return lower.endsWith('.mp4') || 
         lower.endsWith('.mov') || 
         lower.endsWith('.avi') || 
         lower.endsWith('.mkv') ||
         lower.endsWith('.m4v')
}


// 打开发布视频素材选择弹窗
const openPublishVideoMaterialDialog = async () => {
  console.log('打开视频素材选择弹窗（仅显示生成素材）')
  // 重置选择
  publishPlatformForm.selectedVideo = null
  
  // 获取素材数据（只获取生成素材，每次都重新获取，确保数据最新）
  try {
    const response = await materialApi.getAllMaterials('生成素材')
    if (response.code === 200) {
      // 只设置生成素材到store
      appStore.setMaterials(response.data || [])
      console.log('✅ 生成素材列表获取成功，总数:', response.data.length)
      console.log('✅ 过滤后的视频素材数量:', availableVideoMaterials.value.length)
      
      // 验证是否都是生成素材
      const nonGeneratedMaterials = response.data.filter(m => m.source !== '生成素材')
      if (nonGeneratedMaterials.length > 0) {
        console.warn('⚠️ 警告：返回的素材中包含非生成素材:', nonGeneratedMaterials.length)
      }
      
      publishVideoMaterialDialogVisible.value = true
    } else {
      ElMessage.error('获取素材列表失败')
      return
    }
  } catch (error) {
    console.error('获取素材列表出错:', error)
    ElMessage.error('获取素材列表失败')
    return
  }
}

// 处理视频素材表格行选择
const handleVideoMaterialSelection = (row) => {
  if (row) {
    selectVideoMaterial(row)
  }
}

// 判断视频素材是否被选中（用于发布视频素材选择弹窗）
const isVideoMaterialSelected = (material) => {
  if (!publishPlatformForm.selectedVideo || !material) return false
  // 使用 file_path 作为唯一标识符进行比较
  if (publishPlatformForm.selectedVideo.file_path) {
    return publishPlatformForm.selectedVideo.file_path === material.file_path
  }
  // 如果没有 file_path，使用 filename 比较
  if (publishPlatformForm.selectedVideo.filename && material.filename) {
    return publishPlatformForm.selectedVideo.filename === material.filename
  }
  return false
}

// 获取视频素材表格行的样式类名（用于发布视频素材选择弹窗）
const getVideoMaterialRowClassName = ({ row }) => {
  if (isVideoMaterialSelected(row)) {
    return 'selected-video-material-row'
  }
  return ''
}

// 选择视频素材
const selectVideoMaterial = (material) => {
  // 保存完整的素材信息，包括uri和file_path
  console.log('📦 原始素材数据:', material)
  publishPlatformForm.selectedVideo = {
    ...material,
    type: 'material',
    // 如果uri存在且是URL，优先使用uri；否则使用file_path
    path: (material.uri && (material.uri.startsWith('http://') || material.uri.startsWith('https://'))) 
      ? material.uri 
      : material.file_path,
    file_path: material.file_path,  // 保留file_path作为备用
    uri: material.uri  // 保留uri字段，用于判断是否是生成素材
  }
  publishPlatformForm.useMaterialLibrary = true
  console.log('✅ 已选择视频素材:', {
    uri: publishPlatformForm.selectedVideo.uri,
    file_path: publishPlatformForm.selectedVideo.file_path,
    path: publishPlatformForm.selectedVideo.path,
    source: publishPlatformForm.selectedVideo.source
  })
}

// 确认发布视频素材选择
const confirmPublishVideoMaterialSelection = () => {
  if (!publishPlatformForm.selectedVideo) {
    ElMessage.warning('请选择一个视频素材')
    return
  }
  publishPlatformForm.useMaterialLibrary = true
  publishVideoMaterialDialogVisible.value = false
  ElMessage.success('已选择视频素材')
}

// 打开制作中心素材选择弹窗
const openMaterialSelectionDialog = async () => {
  console.log('打开制作中心素材选择弹窗（仅显示非生成素材）')
  // 重置选择
  selectedProductionMaterial.value = null
  
  // 获取素材数据（获取所有素材，但只显示非生成素材）
  try {
    const response = await materialApi.getAllMaterials()
    if (response.code === 200) {
      appStore.setMaterials(response.data || [])
      console.log('素材列表获取成功，总数:', response.data.length)
      console.log('非生成素材的视频素材数量:', availableProductionMaterials.value.length)
      
      // 验证筛选结果
      const generatedMaterials = availableProductionMaterials.value.filter(m => m.source === '生成素材')
      if (generatedMaterials.length > 0) {
        console.warn('⚠️ 警告：筛选后的素材中包含生成素材:', generatedMaterials.length)
      }
      
      productionMaterialDialogVisible.value = true
    } else {
      ElMessage.error('获取素材列表失败')
      return
    }
  } catch (error) {
    console.error('获取素材列表出错:', error)
    ElMessage.error('获取素材列表失败')
    return
  }
}

// 处理制作中心素材表格行选择
const handleProductionMaterialSelection = (row) => {
  if (row) {
    selectProductionMaterial(row)
  }
}

// 判断素材是否被选中
const isMaterialSelected = (material) => {
  if (!selectedProductionMaterial.value || !material) return false
  // 使用 file_path 作为唯一标识符进行比较
  return selectedProductionMaterial.value.file_path === material.file_path
}

// 获取素材表格行的样式类名
const getMaterialRowClassName = ({ row }) => {
  if (isMaterialSelected(row)) {
    return 'selected-material-row'
  }
  return ''
}

// 选择制作中心素材
const selectProductionMaterial = (material) => {
  selectedProductionMaterial.value = material
  console.log('已选择素材:', material)
}

// 确认制作中心素材选择
const confirmProductionMaterialSelection = () => {
  if (!selectedProductionMaterial.value) {
    ElMessage.warning('请选择一个素材')
    return
  }
  
  const material = selectedProductionMaterial.value
  let materialUrl = ''
  
  // 如果是谷歌云存储上传的素材，使用其URI地址
  if (material.source === '谷歌存储上传') {
    if (material.uri && material.uri.startsWith('https://storage.googleapis.com/n8n-test-3344')) {
      // 如果URI已经是完整的Google Storage URL，直接使用
      materialUrl = material.uri
    } else if (material.filename) {
      // 如果URI不存在或不完整，根据文件名构建完整的Google Storage URI
      // 文件名需要进行URL编码
      const encodedFilename = encodeURIComponent(material.filename)
      materialUrl = `https://storage.googleapis.com/n8n-test-3344/${encodedFilename}`
    } else {
      ElMessage.warning('该素材缺少文件名或URI地址')
      return
    }
  } else {
    // 本地上传的素材，使用预览URL
    materialUrl = materialApi.getMaterialPreviewUrl(material.file_path.split('/').pop())
  }
  
  tempConfig.video.materialUrl = materialUrl
  
  productionMaterialDialogVisible.value = false
  ElMessage.success('已选择素材')
}

// 获取视频显示名称
const getVideoDisplayName = (video) => {
  if (!video) return '未选择'
  if (typeof video === 'string') {
    return video.split('/').pop() || video
  }
  if (video.name) {
    return video.name
  }
  if (video.filename) {
    return video.filename
  }
  return '未知视频'
}

// 获取记录对应的webhook URL
const getRecordWebhookUrl = (contentType) => {
  if (contentType === 'article') {
    return 'https://aicode.ltd/webhook/publich-article'
  } else if (contentType === 'image-text') {
    return 'https://aicode.ltd/webhook/publich-images'
  } else if (contentType === 'video') {
    return 'https://aicode.ltd/webhook/publich-video'
  }
  return null
}

// 创建发布中心记录
const createPublishRecord = async (recordData) => {
  const requestUrl = `${apiBaseUrl}/publish/records`
  console.log('📝 [创建发布中心记录] 开始创建发布中心记录')
  console.log('📝 [创建发布中心记录] 请求URL:', requestUrl)
  console.log('📝 [创建发布中心记录] 请求数据:', JSON.stringify(recordData, null, 2))
  
  try {
    const response = await fetch(requestUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(recordData)
    })
    
    console.log('📝 [创建发布中心记录] 响应状态:', response.status, response.statusText)
    console.log('📝 [创建发布中心记录] 响应OK:', response.ok)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ [创建发布中心记录] HTTP错误:', {
        status: response.status,
        statusText: response.statusText,
        errorText: errorText
      })
      return null
    }
    
    const result = await response.json()
    console.log('📝 [创建发布中心记录] 响应结果:', JSON.stringify(result, null, 2))
    
    if (result.code === 200) {
      console.log('✅ [创建发布中心记录] 发布中心记录创建成功:', result.data)
      return result.data
    } else {
      console.error('❌ [创建发布中心记录] 创建失败，返回码不是200:', {
        code: result.code,
        msg: result.msg,
        data: result.data
      })
      // 不抛出错误，因为发布已经成功，记录创建失败不影响主流程
      return null
    }
  } catch (error) {
    console.error('❌ [创建发布中心记录] 异常错误:', error)
    console.error('❌ [创建发布中心记录] 错误详情:', {
      name: error.name,
      message: error.message,
      stack: error.stack
    })
    // 不抛出错误，因为发布已经成功，记录创建失败不影响主流程
    return null
  }
}

// 更新发布状态
const updatePublishStatus = async (recordId, status) => {
  try {
    const response = await fetch(`${apiBaseUrl}/production/records/${recordId}/status`, {
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

const publishRecord = async (record) => {
  if (!record) {
    ElMessage.error('未找到要发布的记录')
    return
  }
  // 移除重复点击限制，允许连续点击发布按钮
  // if (publishingRecordId.value && publishingRecordId.value === record.id) {
  //   ElMessage.warning('当前记录正在发布中')
  //   return
  // }

  // 视频和图文类型显示平台选择弹窗，文章类型直接调用接口
  if (record.content_type === 'image-text' || record.content_type === 'video') {
    // 确保账号列表已加载
    if (accountStore.accounts.length === 0) {
      try {
        console.log('📥 账号列表为空，正在加载账号列表...')
        const response = await accountApi.getAccounts()
        if (response.code === 200 && response.data) {
          accountStore.setAccounts(response.data)
          console.log('✅ 账号列表加载成功，总数:', accountStore.accounts.length)
        }
      } catch (error) {
        console.error('加载账号列表失败:', error)
        // 即使加载失败也继续，可能账号列表已经在其他地方加载了
      }
    }
    
    // 保存当前要发布的记录，显示平台选择弹窗
    currentPublishRecord.value = record
    // 初始化标题和描述（使用制作成功的标题和描述作为默认值）
    publishPlatformForm.title = record.title || ''
    publishPlatformForm.desc = record.desc || ''
    // 图文类型：初始化摘要、正文、话题
    if (record.content_type === 'image-text') {
      publishPlatformForm.summary = record.summary || formatContentPreview(record.content, 60) || ''
      publishPlatformForm.content = record.content || ''
      // 处理话题（keywords）
      if (record.keywords) {
        if (Array.isArray(record.keywords)) {
          publishPlatformForm.selectedTopics = [...record.keywords]
        } else if (typeof record.keywords === 'string') {
          try {
            const parsed = JSON.parse(record.keywords)
            publishPlatformForm.selectedTopics = Array.isArray(parsed) ? [...parsed] : [record.keywords]
          } catch (e) {
            // 如果不是JSON，按逗号分割
            publishPlatformForm.selectedTopics = record.keywords.split(',').map(t => t.trim()).filter(t => t)
          }
        }
      } else {
        publishPlatformForm.selectedTopics = []
      }
    }
    // 根据内容类型设置默认平台
    if (record.content_type === 'video') {
      publishPlatformForm.platform = '视频号' // 视频类型默认选择视频号
      // 初始化视频发布配置
      publishPlatformForm.selectedAccounts = []
      publishPlatformForm.selectedVideo = null
      publishPlatformForm.useMaterialLibrary = false
      publishPlatformForm.enableTimer = false
      publishPlatformForm.videosPerDay = 1
      publishPlatformForm.dailyTimes = ['10:00']
      publishPlatformForm.startDays = 0
      publishPlatformForm.isDraft = false
      publishPlatformForm.productLink = ''
      publishPlatformForm.productTitle = ''
      publishPlatformForm.category = 0
      // 初始化话题（keywords）
      if (record.keywords) {
        if (Array.isArray(record.keywords)) {
          publishPlatformForm.selectedTopics = [...record.keywords]
        } else if (typeof record.keywords === 'string') {
          try {
            const parsed = JSON.parse(record.keywords)
            publishPlatformForm.selectedTopics = Array.isArray(parsed) ? [...parsed] : [record.keywords]
          } catch (e) {
            // 如果不是JSON，按逗号分割
            publishPlatformForm.selectedTopics = record.keywords.split(',').map(t => t.trim()).filter(t => t)
          }
        }
      } else {
        publishPlatformForm.selectedTopics = []
      }
      // 自动选择该平台的所有可用账号
      const defaultAccounts = accountStore.accounts.filter(
        acc => acc.platform === '视频号' && acc.status === '正常'
      )
      publishPlatformForm.selectedAccounts = defaultAccounts.map(acc => acc.id)
      // 不默认选择视频，需要用户从素材库选择
      publishPlatformForm.selectedVideo = null
      publishPlatformForm.useMaterialLibrary = false
    } else {
      // 图文类型：使用数组，默认选择微信图文
      publishPlatformForm.platforms = ['微信图文']
      publishPlatformForm.selectedAccounts = {} // 初始化为空对象
    }
    publishPlatformDialogVisible.value = true
    return
  }

  // 文章类型直接调用接口（原有逻辑）
  // 不再使用 publishingRecordId 来阻止重复点击，允许连续发布
  // publishingRecordId.value = record.id
  
  // 更新状态为"进行中"（异步执行，不阻塞）
  updatePublishStatus(record.id, 'processing').catch(err => {
    console.error('更新发布状态失败:', err)
  })
  
  const targetWebhookUrl = getRecordWebhookUrl(record.content_type)
  if (!targetWebhookUrl) {
    ElMessage.error('未配置对应的发布链接')
    // publishingRecordId.value = null
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

    const successMsg = result?.message || result?.msg || '发布任务已发送'
    ElMessage.success(successMsg)
    console.log('✅ 发布成功:', result)
  } catch (error) {
    console.error('❌ 发布接口调用失败:', error)
    const errorMsg = error.message || '发布失败，请稍后重试'
    ElMessage.error({
      message: `发布失败: ${errorMsg}`,
      duration: 5000,
      showClose: true
    })
  }
  // 不再使用 publishingRecordId，允许连续点击
  // finally {
  //   publishingRecordId.value = null
  // }
}

// 确认发布（带平台选择）
const confirmPublishWithPlatform = async () => {
  const record = currentPublishRecord.value
  if (!record) {
    ElMessage.error('未找到要发布的记录')
    publishPlatformDialogVisible.value = false
    return
  }

  // 验证平台选择
  if (record.content_type === 'video') {
    if (!publishPlatformForm.platform) {
      ElMessage.warning('请选择发布平台')
      return
    }
  } else if (record.content_type === 'image-text') {
    if (!publishPlatformForm.platforms || publishPlatformForm.platforms.length === 0) {
      ElMessage.warning('请至少选择一个发布平台')
      return
    }
    // 不再验证每个平台是否选择了账号，允许没有账号的平台跳过发布
  }

  // 关闭弹窗
  publishPlatformDialogVisible.value = false

  // 不再使用 publishingRecordId 来阻止重复点击，允许连续发布
  // publishingRecordId.value = record.id
  
  // 更新状态为"进行中"（异步执行，不阻塞）
  updatePublishStatus(record.id, 'processing').catch(err => {
    console.error('更新发布状态失败:', err)
  })
  
  // 如果是视频类型且选择的是视频号、抖音、小红书或快手，直接调用后端的 /postVideo API
  if (record.content_type === 'video') {
    const platformMap = {
      '视频号': 2,
      '抖音': 3,
      '小红书': 1,
      '快手': 4
    }
    
    const platformType = platformMap[publishPlatformForm.platform]
    
    if (platformType) {
      // 验证账号选择
      if (publishPlatformForm.selectedAccounts.length === 0) {
        ElMessage.error('请至少选择一个发布账号')
        // publishingRecordId.value = null
        await updatePublishStatus(record.id, 'failed')
        return
      }
      
      // 获取选中的账号
      const selectedAccountObjects = accountStore.accounts.filter(
        acc => publishPlatformForm.selectedAccounts.includes(acc.id)
      )
      
      if (selectedAccountObjects.length === 0) {
        ElMessage.error('选择的账号不存在或已被删除')
        // publishingRecordId.value = null
        await updatePublishStatus(record.id, 'failed')
        return
      }
      
      try {
        // 处理视频文件路径
        let videoPath = null
        
        // 必须从素材库选择视频
        if (!publishPlatformForm.useMaterialLibrary || !publishPlatformForm.selectedVideo) {
          ElMessage.error('请从素材库选择视频素材')
          // publishingRecordId.value = null
          await updatePublishStatus(record.id, 'failed')
          return
        }
        
            // 从素材库选择的视频
        if (typeof publishPlatformForm.selectedVideo === 'object') {
          // 优先使用uri（完整URL），如果是生成素材，uri应该是完整的谷歌云存储URL
          const selectedVideo = publishPlatformForm.selectedVideo
          console.log('🔍 选择的视频素材信息:', {
            uri: selectedVideo.uri,
            file_path: selectedVideo.file_path,
            path: selectedVideo.path,
            source: selectedVideo.source
          })
          
          // 优先检查uri字段，如果存在且是URL，直接使用
          if (selectedVideo.uri && (selectedVideo.uri.startsWith('http://') || selectedVideo.uri.startsWith('https://'))) {
            videoPath = selectedVideo.uri  // 使用完整URL，后端会自动下载
            console.log('✅ 使用URI（完整URL）:', videoPath)
          } else if (selectedVideo.path && (selectedVideo.path.startsWith('http://') || selectedVideo.path.startsWith('https://'))) {
            // 如果path是URL（可能是从material.uri设置的），也使用
            videoPath = selectedVideo.path
            console.log('✅ 使用path（完整URL）:', videoPath)
          } else if (selectedVideo.file_path) {
            // 使用本地文件路径
            videoPath = selectedVideo.file_path.split('/').pop() || selectedVideo.file_path
            console.log('📁 使用本地文件路径:', videoPath)
          } else if (selectedVideo.path) {
            videoPath = selectedVideo.path
            console.log('📁 使用path（本地文件）:', videoPath)
          }
          } else if (typeof publishPlatformForm.selectedVideo === 'string') {
            videoPath = publishPlatformForm.selectedVideo
          console.log('📝 使用字符串路径:', videoPath)
        }
        
        // 如果是URL（http/https开头），直接传递完整URL，后端会自动下载
        // 如果是本地文件名，直接使用
        // 不再提取URL中的文件名，让后端处理URL下载
        
        if (!videoPath) {
          ElMessage.error('请选择视频素材')
          // publishingRecordId.value = null
          await updatePublishStatus(record.id, 'failed')
          return
        }
        
        console.log('🎬 最终使用的视频路径:', videoPath, '是否为URL:', videoPath.startsWith('http://') || videoPath.startsWith('https://'))
        
        // 处理标签（keywords）- 使用弹窗中选择的话题
        let tags = []
        if (publishPlatformForm.selectedTopics && publishPlatformForm.selectedTopics.length > 0) {
          tags = [...publishPlatformForm.selectedTopics]
        } else if (record.keywords) {
          // 如果弹窗中没有选择话题，则使用记录中的话题作为后备
          if (Array.isArray(record.keywords)) {
            tags = record.keywords
          } else if (typeof record.keywords === 'string') {
            try {
              // 尝试解析JSON字符串
              const parsed = JSON.parse(record.keywords)
              tags = Array.isArray(parsed) ? parsed : [record.keywords]
            } catch (e) {
              // 如果不是JSON，按逗号分割
              tags = record.keywords.split(',').map(t => t.trim()).filter(t => t)
            }
          }
        }
        
        // 处理定时发布时间
        let dailyTimesArray = ['10:00']
        if (publishPlatformForm.enableTimer && publishPlatformForm.dailyTimes) {
          if (Array.isArray(publishPlatformForm.dailyTimes)) {
            // 如果是时间范围（el-time-picker is-range 模式返回 [start, end]）
            if (publishPlatformForm.dailyTimes.length === 2) {
              const [start, end] = publishPlatformForm.dailyTimes
              // 使用开始时间作为默认发布时间
              // 注意：后端可能需要处理时间范围，这里先使用开始时间
              dailyTimesArray = [start]
            } else {
              // 如果是时间数组，直接使用
              dailyTimesArray = publishPlatformForm.dailyTimes
            }
          } else if (typeof publishPlatformForm.dailyTimes === 'string') {
            // 如果是单个时间字符串
            dailyTimesArray = [publishPlatformForm.dailyTimes]
          }
        }
        
        // 构建符合 /postVideo API 格式的请求体
        const content = publishPlatformForm.desc || record.desc || record.content || '' // 支持desc和content字段
        const publishData = {
          type: platformType,
          title: publishPlatformForm.title || record.title || '', // 使用表单中的标题，如果没有则使用记录中的标题
          desc: content, // 使用表单中的描述，如果没有则使用记录中的描述
          content: content, // 同时传递content字段，确保兼容性
          tags: tags,
          fileList: [videoPath], // 视频文件路径列表
          accountList: selectedAccountObjects.map(acc => acc.filePath), // 账号文件路径列表
          category: publishPlatformForm.category || 0, // 分类，0表示非原创
          enableTimer: publishPlatformForm.enableTimer ? 1 : 0, // 是否启用定时发布
          videosPerDay: publishPlatformForm.videosPerDay || 1, // 每天发布视频数
          dailyTimes: dailyTimesArray, // 每天发布时间
          startDays: publishPlatformForm.startDays || 0, // 开始发布天数
          isDraft: publishPlatformForm.isDraft || false // 是否保存为草稿（仅视频号使用）
        }
        
        // 抖音平台添加商品配置
        if (platformType === 3) {
          if (publishPlatformForm.productLink) {
            publishData.productLink = publishPlatformForm.productLink
          }
          if (publishPlatformForm.productTitle) {
            publishData.productTitle = publishPlatformForm.productTitle
          }
        }
        
        console.log('📤 发送视频发布请求到 /postVideo:', {
          contentType: record.content_type,
          recordId: record.id,
          platform: publishPlatformForm.platform,
          platformType: platformType,
          accountCount: selectedAccountObjects.length
        })
        console.log('📋 请求体:', JSON.stringify(publishData, null, 2))
        
        const response = await fetch(`${apiBaseUrl}/postVideo`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(publishData)
        })
        
        const result = await response.json()
        console.log('📤 [视频发布] 后端响应:', JSON.stringify(result, null, 2))
        console.log('📤 [视频发布] 响应code:', result.code)
        
        if (result.code === 200) {
          const successMsg = result.msg || '发布任务已提交'
          ElMessage.success(successMsg)
          console.log('✅ [视频发布] 发布成功，开始更新状态和创建发布记录')
          console.log('✅ [视频发布] 记录ID:', record.id)
          console.log('✅ [视频发布] 平台:', publishPlatformForm.platform)
          
          await updatePublishStatus(record.id, 'success')
          console.log('✅ [视频发布] 状态更新完成，开始创建发布中心记录')
          
          // 构建发布中心记录数据
          const publishRecordData = {
            production_id: record.id,
            content_type: record.content_type,
            platform: publishPlatformForm.platform,
            title: publishPlatformForm.title || record.title || '',
            content: record.content || '',
            desc: publishPlatformForm.desc || record.desc || '',
            video: videoPath || record.video || '',
            material_url: record.material_url || '',
            url: record.video || '', // 生成内容链接
            keywords: publishPlatformForm.tags || record.keywords || []
          }
          console.log('📝 [视频发布] 准备创建发布中心记录，数据:', JSON.stringify(publishRecordData, null, 2))
          
          // 创建发布中心记录
          const publishRecordResult = await createPublishRecord(publishRecordData)
          if (publishRecordResult) {
            console.log('✅ [视频发布] 发布中心记录创建成功，结果:', publishRecordResult)
          } else {
            console.warn('⚠️ [视频发布] 发布中心记录创建失败，但发布已成功')
          }
        } else {
          const errorMsg = result.msg || '发布失败'
          console.error('❌ [视频发布] 发布失败:', result)
          console.error('❌ [视频发布] 错误信息:', errorMsg)
          ElMessage.error(`发布失败: ${errorMsg}`)
          await updatePublishStatus(record.id, 'failed')
        }
      } catch (error) {
        console.error('❌ 发布接口调用失败:', error)
        const errorMsg = error.message || '发布失败，请稍后重试'
        ElMessage.error({
          message: `发布失败: ${errorMsg}`,
          duration: 5000,
          showClose: true
        })
        await updatePublishStatus(record.id, 'failed')
      }
      // 不再使用 publishingRecordId，允许连续点击
      // finally {
      //   publishingRecordId.value = null
      // }
      
      return // 视频类型已处理，直接返回
    }
  }
  
  // 图文类型：支持多平台发布
  if (record.content_type === 'image-text') {
  const targetWebhookUrl = getRecordWebhookUrl(record.content_type)
  if (!targetWebhookUrl) {
    ElMessage.error('未配置对应的发布链接')
    // publishingRecordId.value = null
    return
  }
  
    // 循环发布到每个选中的平台
    const platforms = publishPlatformForm.platforms || []
    console.log('🔍 图文类型多平台发布 - 开始处理:', {
      platforms: platforms,
      platformsCount: platforms.length,
      selectedAccounts: publishPlatformForm.selectedAccounts,
      recordId: record.id
    })
    
    if (platforms.length === 0) {
      console.error('❌ 没有选择任何平台')
      ElMessage.error('请至少选择一个发布平台')
      // publishingRecordId.value = null
      await updatePublishStatus(record.id, 'failed')
      return
    }
    
    let successCount = 0
    let failCount = 0
    
    for (const platform of platforms) {
      try {
        console.log(`🔄 开始处理平台: ${platform}`)
        // 获取该平台的账号
        let platformAccounts = publishPlatformForm.selectedAccounts[platform] || []
        console.log(`📋 ${platform} 平台账号情况:`, {
          platformAccounts: platformAccounts,
          accountCount: platformAccounts.length
        })
        
        // 添加账号列表
        let accountObjects = accountStore.accounts.filter(acc => platformAccounts.includes(acc.id))
        
        // 小红书平台：调用自己的自动化接口
        if (platform === '小红书') {
          // 如果没有选择账号，自动选择"程序员饼干"账号
          if (platformAccounts.length === 0 || accountObjects.length === 0) {
            console.log(`⚠️ ${platform} 没有选择账号，尝试自动选择"程序员饼干"账号...`)
            
            // 确保账号列表已加载
            if (accountStore.accounts.length === 0) {
              console.log('📥 账号列表为空，正在加载账号列表...')
              try {
                const response = await accountApi.getAccounts()
                if (response.code === 200 && response.data) {
                  accountStore.setAccounts(response.data)
                  console.log('✅ 账号列表加载成功，总数:', accountStore.accounts.length)
                } else {
                  console.error('❌ 账号列表加载失败')
                }
              } catch (error) {
                console.error('❌ 加载账号列表失败:', error)
              }
            }
            
            // 查找"程序员饼干"账号（支持多种名称匹配）
            const biscuitAccount = accountStore.accounts.find(acc => {
              if (acc.platform !== '小红书') return false
              const name = (acc.name || '').toLowerCase()
              return name === '程序员饼干' || 
                     name.includes('程序员饼干') || 
                     name.includes('biscuit') ||
                     name.includes('程序员') && name.includes('饼干')
            })
            
            if (biscuitAccount) {
              console.log(`✅ 找到"程序员饼干"账号:`, {
                id: biscuitAccount.id,
                name: biscuitAccount.name,
                platform: biscuitAccount.platform,
                filePath: biscuitAccount.filePath
              })
              
              // 自动选择该账号
              if (!publishPlatformForm.selectedAccounts[platform]) {
                publishPlatformForm.selectedAccounts[platform] = []
              }
              publishPlatformForm.selectedAccounts[platform] = [biscuitAccount.id]
              platformAccounts = [biscuitAccount.id]
              accountObjects = [biscuitAccount]
              
              console.log(`✅ 已自动选择"程序员饼干"账号，账号ID: ${biscuitAccount.id}, filePath: ${biscuitAccount.filePath}`)
              ElMessage.info(`已自动选择"程序员饼干"账号进行发布`)
            } else {
              console.error(`❌ ${platform} 没有选择账号，且未找到"程序员饼干"账号`)
              console.log('📋 当前所有账号列表:', accountStore.accounts.map(acc => ({
                id: acc.id,
                name: acc.name,
                platform: acc.platform
              })))
              console.log('📋 小红书平台账号:', accountStore.accounts.filter(acc => acc.platform === '小红书').map(acc => ({
                id: acc.id,
                name: acc.name
              })))
              ElMessage.error(`${platform} 发布失败：请先选择发布账号，或确保存在"程序员饼干"账号`)
              failCount++
              continue
            }
          }
          // 解析图片列表
          let imageList = []
          
          // 优先使用 media_ids
          if (record.media_ids) {
            if (Array.isArray(record.media_ids)) {
              // 直接使用数组，保持URL或文件名原样，让后端处理
              imageList = record.media_ids
            } else if (typeof record.media_ids === 'string') {
              try {
                const parsed = JSON.parse(record.media_ids)
                if (Array.isArray(parsed)) {
                  imageList = parsed
                } else {
                  imageList = [parsed]
                }
              } catch (e) {
                // 如果不是JSON，当作单个文件名或URL处理
                imageList = [record.media_ids]
              }
            }
          } else if (record.media_url) {
            // 使用 media_url 作为备选
            if (typeof record.media_url === 'string') {
              try {
                const parsed = JSON.parse(record.media_url)
                if (Array.isArray(parsed)) {
                  imageList = parsed
                } else {
                  imageList = [parsed]
                }
              } catch (e) {
                imageList = [record.media_url]
              }
            }
          }
          
          if (imageList.length === 0) {
            console.error(`❌ ${platform} 没有找到图片列表`)
            ElMessage.error(`${platform} 发布失败：没有找到图片列表`)
            failCount++
            continue
          }
          
          // 再次确认 accountObjects 不为空
          if (accountObjects.length === 0) {
            console.error(`❌ ${platform} 账号对象为空，无法发布`)
            ElMessage.error(`${platform} 发布失败：账号信息缺失`)
            failCount++
            continue
          }
          
          // 构建请求体
          const accountList = accountObjects.map(acc => {
            if (!acc.filePath) {
              console.warn(`⚠️ 账号 ${acc.name} (ID: ${acc.id}) 没有 filePath`)
            }
            return acc.filePath || acc.id
          }).filter(path => path) // 过滤掉空值
          
          if (accountList.length === 0) {
            console.error(`❌ ${platform} 账号列表为空，无法发布`)
            ElMessage.error(`${platform} 发布失败：账号文件路径缺失`)
            failCount++
            continue
          }
          
          // 获取正文内容，优先使用弹窗中的输入，其次使用记录中的内容
          const content = publishPlatformForm.content || record.content || ''
          
          // 详细日志记录
          console.log(`🔍 [${platform}发布] 正文内容检查:`, {
            publishPlatformFormContent: publishPlatformForm.content,
            publishPlatformFormContentLength: publishPlatformForm.content ? publishPlatformForm.content.length : 0,
            recordContent: record.content,
            recordContentLength: record.content ? record.content.length : 0,
            finalContent: content,
            finalContentLength: content ? content.length : 0,
            recordId: record.id
          })
          
          // 验证正文内容
          if (!content || !content.trim()) {
            console.warn(`⚠️ ${platform} 发布警告：正文内容为空`, {
              publishPlatformFormContent: publishPlatformForm.content,
              recordContent: record.content,
              recordId: record.id
            })
            ElMessage.warning(`${platform} 发布：正文内容为空，将只发布标题`)
          } else {
            console.log(`✅ [${platform}发布] 正文内容已准备，长度: ${content.length} 字符`)
          }
          
          const requestBody = {
            imageList: imageList,
            accountList: accountList,
            title: publishPlatformForm.title || record.title || '',
            content: content.trim(), // 使用处理后的正文，去除首尾空格
            tags: publishPlatformForm.selectedTopics.length > 0 ? publishPlatformForm.selectedTopics : (record.keywords ? (Array.isArray(record.keywords) ? record.keywords : JSON.parse(record.keywords || '[]')) : []), // 使用弹窗中的话题
            enableTimer: publishPlatformForm.enableTimer || false,
            imagesPerDay: publishPlatformForm.imagesPerDay || 1,
            dailyTimes: publishPlatformForm.dailyTimes || [],
            startDays: publishPlatformForm.startDays || 0
          }
          
          console.log(`📤 准备发送${platform}发布请求到 /postImageText:`, {
            contentType: record.content_type,
            recordId: record.id,
            platform: platform,
            accountCount: accountObjects.length,
            accountList: accountList,
            imageCount: imageList.length,
            title: requestBody.title,
            content: requestBody.content ? `${requestBody.content.substring(0, 50)}...` : '(空)',
            contentLength: requestBody.content ? requestBody.content.length : 0,
            tags: requestBody.tags
          })
          
          const response = await fetch(`${apiBaseUrl}/postImageText`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
          })
          
          console.log(`📥 ${platform}发布请求响应:`, {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok
          })
          
          const result = await response.json()
          
          if (result.code === 200) {
            console.log(`✅ ${platform}发布成功:`, result)
            successCount++
            
            // 创建发布中心记录
            await createPublishRecord({
              production_id: record.id,
              content_type: record.content_type,
              platform: platform,
              title: publishPlatformForm.title || record.title || '',
              content: publishPlatformForm.content || record.content || '', // 使用弹窗中的正文
              desc: publishPlatformForm.desc || record.desc || '',
              summary: publishPlatformForm.summary || record.summary || '', // 使用弹窗中的摘要
              video: record.video || '',
              material_url: record.material_url || '',
              url: record.url || '',
              media_ids: record.media_ids || [],
              keywords: publishPlatformForm.selectedTopics.length > 0 ? publishPlatformForm.selectedTopics : (record.keywords || []) // 使用弹窗中的话题
            })
          } else {
            const errorMsg = result.msg || '发布失败'
            console.error(`❌ ${platform}发布失败:`, errorMsg)
            ElMessage.error(`${platform} 发布失败: ${errorMsg}`)
            failCount++
          }
          
          continue // 继续处理下一个平台
        }
        
        // 其他平台：使用 n8n webhook
    // 构建请求体
    let requestBody = { ...record }
    
    // 添加平台参数
        requestBody.platform = platform
        requestBody.accountList = accountObjects.map(acc => acc.filePath)
    
        // 处理图文类型的 media_ids -> urls 转换
        if (record.content_type === 'image-text' && record.media_ids) {
          let urlsArray = []
          if (Array.isArray(record.media_ids)) {
            urlsArray = record.media_ids.filter(url => url && typeof url === 'string')
          } else if (typeof record.media_ids === 'string') {
            try {
              const parsed = JSON.parse(record.media_ids)
              if (Array.isArray(parsed)) {
                urlsArray = parsed.filter(url => url && typeof url === 'string')
              } else {
                urlsArray = [record.media_ids]
              }
            } catch (e) {
              urlsArray = [record.media_ids]
            }
          }
          // 将 media_ids 转换为 urls
          requestBody.urls = urlsArray
          // 删除 media_ids 字段
          delete requestBody.media_ids
        }
    
        // 添加url参数（用于单图场景）
      let urlValue = null
      if (record.url) {
        urlValue = record.url
      } else if (record.media_url) {
        urlValue = record.media_url
      } else if (record.media_ids && Array.isArray(record.media_ids) && record.media_ids.length > 0) {
        urlValue = record.media_ids[0]
      } else if (record.media_ids && typeof record.media_ids === 'string') {
        try {
          const parsed = JSON.parse(record.media_ids)
          if (Array.isArray(parsed) && parsed.length > 0) {
            urlValue = parsed[0]
          }
        } catch (e) {
          // ignore
        }
      }
      if (urlValue) {
        requestBody.url = urlValue
      }
      requestBody.record_id = record.id
        
        // 添加标题、描述、摘要、正文、话题（如果表单中有修改）
        if (publishPlatformForm.title) {
          requestBody.title = publishPlatformForm.title
        }
        if (publishPlatformForm.desc) {
          requestBody.desc = publishPlatformForm.desc
        }
        if (publishPlatformForm.summary) {
          requestBody.summary = publishPlatformForm.summary
        }
        if (publishPlatformForm.content) {
          requestBody.content = publishPlatformForm.content
        }
        if (publishPlatformForm.selectedTopics && publishPlatformForm.selectedTopics.length > 0) {
          requestBody.keywords = publishPlatformForm.selectedTopics
          requestBody.tags = publishPlatformForm.selectedTopics
        }
        
        console.log(`📤 准备发送${platform}发布请求到 n8n:`, {
          url: targetWebhookUrl,
          contentType: record.content_type,
          recordId: record.id,
          platform: platform,
          accountCount: accountObjects.length,
          requestBody: requestBody
        })
        console.log(`📤 请求体JSON:`, JSON.stringify(requestBody, null, 2))
        
        const response = await fetch(targetWebhookUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        })
        
        console.log(`📥 ${platform}发布请求响应:`, {
          status: response.status,
          statusText: response.statusText,
          ok: response.ok
        })

        // 尝试读取响应体中的错误信息
        let errorMessage = null
        let result = null
        
        try {
          const responseText = await response.text()
          if (responseText) {
            try {
              result = JSON.parse(responseText)
              if (result.msg || result.message || result.error) {
                errorMessage = result.msg || result.message || result.error
              }
            } catch (e) {
              errorMessage = responseText
            }
          }
        } catch (err) {
          console.error('读取响应失败:', err)
        }

        if (!response.ok) {
          const finalErrorMessage = errorMessage || `HTTP ${response.status}: ${response.statusText}`
          console.error(`❌ ${platform}发布失败:`, finalErrorMessage)
          failCount++
          // 继续发布其他平台，不中断
          continue
        }

        console.log(`✅ ${platform}发布成功:`, result)
        successCount++
        
        // 为每个平台创建发布中心记录
        await createPublishRecord({
          production_id: record.id,
          content_type: record.content_type,
          platform: platform,
          title: publishPlatformForm.title || record.title || '',
          content: publishPlatformForm.content || record.content || '', // 使用弹窗中的正文
          desc: publishPlatformForm.desc || record.desc || '',
          summary: publishPlatformForm.summary || record.summary || '', // 使用弹窗中的摘要
          video: record.video || '',
          material_url: record.material_url || '',
          url: urlValue || '',
          media_ids: record.media_ids || [],
          keywords: publishPlatformForm.selectedTopics.length > 0 ? publishPlatformForm.selectedTopics : (record.keywords ? (Array.isArray(record.keywords) ? record.keywords : JSON.parse(record.keywords || '[]')) : []) // 使用弹窗中的话题
        })
      } catch (error) {
        console.error(`❌ ${platform}发布接口调用失败:`, error)
        failCount++
        // 继续发布其他平台
      }
    }
    
    // 更新状态
    console.log(`📊 图文类型多平台发布完成 - 总结:`, {
      totalPlatforms: platforms.length,
      successCount: successCount,
      failCount: failCount,
      recordId: record.id
    })
    
    if (successCount > 0 && failCount === 0) {
      await updatePublishStatus(record.id, 'success')
      ElMessage.success(`成功发布到 ${successCount} 个平台`)
    } else if (successCount > 0 && failCount > 0) {
      await updatePublishStatus(record.id, 'success')
      ElMessage.warning(`成功发布到 ${successCount} 个平台，${failCount} 个平台发布失败`)
    } else {
      await updatePublishStatus(record.id, 'failed')
      if (failCount === platforms.length && platforms.length > 0) {
        ElMessage.error(`所有平台发布失败（共 ${failCount} 个平台，可能因为没有选择账号）`)
      } else {
        ElMessage.error(`所有平台发布失败`)
      }
    }
    
    // 不再使用 publishingRecordId，允许连续点击
    // publishingRecordId.value = null
    return
  }
  
  // 文章类型：使用原有的 webhook 逻辑（单平台）
  const targetWebhookUrl = getRecordWebhookUrl(record.content_type)
  if (!targetWebhookUrl) {
    ElMessage.error('未配置对应的发布链接')
    // publishingRecordId.value = null
    return
  }
  
  try {
    // 构建请求体
    let requestBody = { ...record }
    
    // 添加平台参数
    requestBody.platform = publishPlatformForm.platform
    
    // 添加标题和描述（如果表单中有修改）
    if (publishPlatformForm.title) {
      requestBody.title = publishPlatformForm.title
    }
    if (publishPlatformForm.desc) {
      requestBody.desc = publishPlatformForm.desc
    }
    
    console.log('📤 发送发布请求:', {
      url: targetWebhookUrl,
      contentType: record.content_type,
      recordId: record.id,
      platform: publishPlatformForm.platform
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
          if (result.msg || result.message || result.error) {
            errorMessage = result.msg || result.message || result.error
          }
        } catch (e) {
          errorMessage = responseText
        }
      }
    } catch (err) {
      console.error('读取响应失败:', err)
    }

    if (!response.ok) {
      const finalErrorMessage = errorMessage || `HTTP ${response.status}: ${response.statusText}`
      console.error('❌ 发布失败:', {
        status: response.status,
        statusText: response.statusText,
        errorMessage: finalErrorMessage,
        contentType: record.content_type
      })
      throw new Error(finalErrorMessage)
    }

    const successMsg = result?.message || result?.msg || '发布任务已发送'
    ElMessage.success(successMsg)
    console.log('✅ 发布成功:', result)
    
    // 更新状态为成功
    await updatePublishStatus(record.id, 'success')
    
    // 创建发布中心记录
    await createPublishRecord({
      production_id: record.id,
      content_type: record.content_type,
      platform: publishPlatformForm.platform || '未知平台',
      title: publishPlatformForm.title || record.title || '',
      content: record.content || record.article_content || '',
      desc: publishPlatformForm.desc || record.desc || record.article_desc || '',
      video: record.video || '',
      material_url: record.material_url || '',
      url: record.video || record.url || record.article_media_url || '', // 生成内容链接
      media_ids: record.media_ids || [],
      keywords: publishPlatformForm.tags || record.keywords || []
    })
  } catch (error) {
    console.error('❌ 发布接口调用失败:', error)
    const errorMsg = error.message || '发布失败，请稍后重试'
    ElMessage.error({
      message: `发布失败: ${errorMsg}`,
      duration: 5000,
      showClose: true
    })
    await updatePublishStatus(record.id, 'failed')
  }
  // 不再使用 publishingRecordId，允许连续点击
  // finally {
  //   publishingRecordId.value = null
  // }
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

const deleteProductionRecord = async (record) => {
  if (!record?.id) return
  try {
    await ElMessageBox.confirm(`确认删除【${record.title || '未命名内容'}】吗？`, '删除制作记录', {
      type: 'warning'
    })
  } catch {
    return
  }
  
  // 如果是虚拟记录，直接从列表中删除，不调用后端API
  if (record.isVirtual) {
    productionRecords.value = productionRecords.value.filter(item => item.id !== record.id)
    ElMessage.success('制作记录已删除')
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
    const idsSet = new Set(ids)
    productionRecords.value = productionRecords.value.filter(record => !idsSet.has(record.id))
    ElMessage.success('批量删除成功')
  } catch (error) {
    console.error('批量删除失败:', error)
    ElMessage.error(error.message || '删除失败，请稍后重试')
  } finally {
    clearRecordSelection()
  }
}

// 监听Tab切换，刷新对应类型的数据
watch(activeContentTypeTab, (newTab) => {
  if (newTab === 'all') {
    fetchProductionRecords()
  } else {
    fetchProductionRecords(newTab)
  }
})

onMounted(() => {
  fetchProductionRecords()
  // 启动图文记录轮询监听
  startImageTextPolling()
  // 启动文章记录轮询监听
  startArticlePolling()
  
  // 获取路由实例
  const route = useRoute()
  
  // 检查是否有从爬虫数据列表传入的配置（通过路由查询参数）
  if (route.query.type && route.query.source === 'crawler') {
    console.log('🔍 检测到从爬虫数据列表跳转，类型:', route.query.type)
    console.log('🔍 路由查询参数:', route.query)
    
    try {
      const queryType = route.query.type
      const queryConfig = route.query.config ? JSON.parse(route.query.config) : null
      
      // 如果是文章类型，直接调用文章创作接口
      if (queryType === 'article' && queryConfig) {
        console.log('✅ 检测到文章类型，准备调用文章创作接口')
        console.log('✅ 文章配置:', JSON.stringify(queryConfig, null, 2))
        
        // 验证配置
        if (!queryConfig.writingMode) {
          ElMessage.warning('文章配置缺少写作模式')
          return
        }
        
        if (['polish', 'imitate', 'reprint'].includes(queryConfig.writingMode)) {
          if (!queryConfig.articleLink) {
            ElMessage.warning('文章配置缺少文章链接')
            return
          }
        }
        
        // 立即关闭弹窗（如果打开了）
        contentTypeDialogVisible.value = false
        dialogStep.value = 'select'
        
        // 创建虚拟记录并添加到列表顶部
        const virtualRecord = createVirtualRecord('article')
        if (virtualRecord) {
          productionRecords.value.unshift(virtualRecord)
          console.log('✅ 虚拟文章记录已添加到列表，ID:', virtualRecord.id)
          // 如果有虚拟记录，确保轮询正在运行
          if (!articlePollingInterval) {
            startArticlePolling()
          }
        }
        
        // 异步调用webhook，不阻塞
        console.log('🔍 准备发送文章任务，queryConfig:', queryConfig)
        sendArticleWebhook(queryConfig, 600000) // 10分钟超时
          .then(result => {
            console.log('✅ 文章任务 webhook 调用成功:', result)
            
            // 如果webhook立即返回了完整数据，保存到后端并更新虚拟记录
            if (result && (result.article_title || result.title || result.data?.article_title || result.data?.title)) {
              const articleTitle = result?.article_title || result?.title || result?.data?.article_title || result?.data?.title || `文章任务-${formatLocalDateTime(new Date())}`
              const articleContent = result?.article_content || result?.content || result?.data?.article_content || result?.data?.content || '文章内容生成中，请稍候...'
              const articleDesc = result?.article_desc || result?.description || result?.data?.article_desc || result?.data?.description || ''
              const articleMediaId = result?.article_media_id || result?.media_id || result?.data?.article_media_id || result?.data?.media_id || ''
              const articleMediaUrl = result?.article_media_url || result?.media_url || result?.data?.article_media_url || result?.data?.media_url || ''
              
              // 保存到后端
              fetch(`${apiBaseUrl}/production/articles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  article_title: articleTitle,
                  article_content: articleContent,
                  article_desc: articleDesc,
                  article_media_id: articleMediaId,
                  article_media_url: articleMediaUrl
                })
              })
                .then(saveResponse => saveResponse.json())
                .then(saveResult => {
                  if (saveResult.code === 200 && saveResult.data?.id) {
                    console.log('✅ 文章已保存到后端，ID:', saveResult.data.id)
                    // 更新虚拟记录为真实记录
                    if (virtualRecord) {
                      virtualRecord.id = saveResult.data.id
                      virtualRecord.isVirtual = false
                      virtualRecord.title = articleTitle
                      virtualRecord.article_content = articleContent
                      virtualRecord.article_desc = articleDesc
                      virtualRecord.article_media_id = articleMediaId
                      virtualRecord.article_media_url = articleMediaUrl
                    }
                    // 刷新列表
                    fetchProductionRecords('article')
                  }
                })
                .catch(saveError => {
                  console.error('保存文章到后端失败:', saveError)
                })
            }
          })
          .catch(error => {
            console.error('❌ 文章任务 webhook 调用失败:', error)
            ElMessage.error({
              message: `文章创作失败: ${error.message || '未知错误'}`,
              duration: 5000,
              showClose: true
            })
            // 如果失败，删除虚拟记录
            if (virtualRecord) {
              productionRecords.value = productionRecords.value.filter(item => item.id !== virtualRecord.id)
            }
          })
        
        // 清除路由查询参数，避免重复触发
        if (window.history && window.history.replaceState) {
          const newQuery = { ...route.query }
          delete newQuery.type
          delete newQuery.source
          delete newQuery.config
          delete newQuery.url
          delete newQuery.title
          delete newQuery.desc
          delete newQuery.platform
          window.history.replaceState({}, '', {
            path: route.path,
            query: newQuery
          })
        }
        
        return // 文章类型处理完成，不再处理其他逻辑
      }
      
      // 图文类型的处理逻辑（自动调用webhook）
      if (queryType === 'image-text' && queryConfig) {
        console.log('✅ 检测到图文类型，准备调用图文创作接口')
        console.log('✅ 图文配置原始值:', JSON.stringify(queryConfig, null, 2))
        console.log('✅ 路由查询参数url:', route.query.url)
        
        // 如果 inputContent 为空，尝试从路由参数 url 中获取
        if (!queryConfig.inputContent && route.query.url) {
          console.warn('⚠️ inputContent为空，从路由参数url获取:', route.query.url)
          queryConfig.inputContent = route.query.url
        }
        
        // 验证必填字段并提供默认值（不再直接return，而是使用默认值）
        if (!queryConfig.inputContent) {
          console.error('❌ 图文配置缺少输入内容，且无法从路由参数获取')
          ElMessage.error('图文配置缺少输入内容，请重新配置')
          return
        }
        
        // 为缺失的字段提供默认值，确保能正常调用webhook
        if (!queryConfig.contentLayoutStyle) {
          console.warn('⚠️ 内容排版风格缺失，使用默认值: xiaohongshu-hot')
          queryConfig.contentLayoutStyle = 'xiaohongshu-hot'
        }
        
        if (!queryConfig.imageModel) {
          console.warn('⚠️ 生图模型缺失，使用默认值: qianwen')
          queryConfig.imageModel = 'qianwen'
        }
        
        if (!queryConfig.publishPlatform) {
          console.warn('⚠️ 发布平台缺失，使用默认值: xiaohongshu')
          queryConfig.publishPlatform = 'xiaohongshu'
        }
        
        // 确保其他字段也有默认值
        if (!queryConfig.contentSourceType) {
          queryConfig.contentSourceType = 'other'
        }
        if (queryConfig.imageCount === undefined || queryConfig.imageCount === null) {
          queryConfig.imageCount = 3
        }
        if (!queryConfig.imageStyleType) {
          queryConfig.imageStyleType = 'builtin-ai-no'
        }
        if (!queryConfig.imageRatio) {
          queryConfig.imageRatio = '1664*928'
        }
        if (!queryConfig.coverStyleType) {
          queryConfig.coverStyleType = 'ai-auto'
        }
        if (!queryConfig.coverImageRatio) {
          queryConfig.coverImageRatio = '1664*928'
        }
        if (!queryConfig.infoGraphicType) {
          queryConfig.infoGraphicType = 'minimalist-tech'
        }
        if (queryConfig.contentWordCount === undefined || queryConfig.contentWordCount === null) {
          queryConfig.contentWordCount = 1000
        }
        
        console.log('✅ 应用默认值后的配置:', JSON.stringify(queryConfig, null, 2))
        console.log('✅ 最终字段检查:')
        console.log('  - inputContent:', queryConfig.inputContent ? '✅' : '❌')
        console.log('  - contentSourceType:', queryConfig.contentSourceType ? '✅' : '❌')
        console.log('  - contentLayoutStyle:', queryConfig.contentLayoutStyle ? '✅' : '❌')
        console.log('  - imageModel:', queryConfig.imageModel ? '✅' : '❌')
        console.log('  - publishPlatform:', queryConfig.publishPlatform ? '✅' : '❌')
        console.log('  - imageCount:', queryConfig.imageCount !== undefined && queryConfig.imageCount !== null ? '✅' : '❌')
        console.log('  - imageStyleType:', queryConfig.imageStyleType ? '✅' : '❌')
        console.log('  - imageRatio:', queryConfig.imageRatio ? '✅' : '❌')
        console.log('  - coverStyleType:', queryConfig.coverStyleType ? '✅' : '❌')
        console.log('  - coverImageRatio:', queryConfig.coverImageRatio ? '✅' : '❌')
        console.log('  - infoGraphicType:', queryConfig.infoGraphicType ? '✅' : '❌')
        console.log('  - contentWordCount:', queryConfig.contentWordCount !== undefined && queryConfig.contentWordCount !== null ? '✅' : '❌')
        
        // 立即关闭弹窗（如果打开了）
        contentTypeDialogVisible.value = false
        dialogStep.value = 'select'
        
        // 创建虚拟记录并添加到列表顶部
        const virtualRecord = createVirtualRecord('image-text')
        if (virtualRecord) {
          productionRecords.value.unshift(virtualRecord)
          console.log('✅ 虚拟图文记录已添加到列表，ID:', virtualRecord.id)
          // 如果有虚拟记录，确保轮询正在运行
          if (!imageTextPollingInterval) {
            startImageTextPolling()
          }
        }
        
        // 异步调用webhook，不阻塞
        console.log('🔍 准备发送图文任务，queryConfig:', queryConfig)
        sendImageTextWebhook(queryConfig, 600000) // 10分钟超时
          .then(result => {
            console.log('✅ 图文任务 webhook 调用成功:', result)
            
            // 如果webhook立即返回了完整数据，保存到后端并更新虚拟记录
            if (result && (result.title || result.data?.title)) {
              const title = result.title || result.data?.title || `图文任务-${formatLocalDateTime(new Date())}`
              const content = result.content || result.data?.content || '图文内容生成中...'
              const mediaIds = result.media_ids || result.data?.media_ids || []
              const height = result.height || result.data?.height || 1080
              const width = result.width || result.data?.width || 1920
              
              // 保存到后端
              const urls = Array.isArray(mediaIds) ? mediaIds : (mediaIds ? [mediaIds] : [])
              console.log('💾 保存图文记录到后端，urls数组:', urls)
              fetch(`${apiBaseUrl}/production/image-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content, urls: urls, height, width })
              })
                .then(saveResponse => saveResponse.json())
                .then(saveResult => {
                  if (saveResult.code === 200 && saveResult.data?.id) {
                    console.log('✅ 图文已保存到后端，ID:', saveResult.data.id)
                    // 更新虚拟记录为真实记录
                    if (virtualRecord) {
                      virtualRecord.id = saveResult.data.id
                      virtualRecord.isVirtual = false
                      virtualRecord.title = title
                      virtualRecord.content = content
                      virtualRecord.media_ids = urls
                    }
                    // 刷新列表
                    fetchProductionRecords('image-text')
                  }
                })
                .catch(saveError => {
                  console.error('保存图文到后端失败:', saveError)
                })
            } else {
              // 启动轮询，等待n8n返回结果并替换虚拟记录
              pollForRecordCompletion(virtualRecord.id, 'image-text', 300, 2000)
                .then(found => {
                  if (found) {
                    ElMessage.success('✅ 图文任务已完成，列表已更新')
                  } else {
                    ElMessage.warning('⚠️ 图文任务已发送，但未检测到完成记录，请稍后手动刷新')
                  }
                })
            }
          })
          .catch(error => {
            console.error('❌ 图文任务 webhook 调用失败:', error)
            ElMessage.error({
              message: `图文创作失败: ${error.message || '未知错误'}`,
              duration: 5000,
              showClose: true
            })
            // 如果失败，删除虚拟记录
            if (virtualRecord) {
              productionRecords.value = productionRecords.value.filter(item => item.id !== virtualRecord.id)
            }
          })
        
        // 清除路由查询参数，避免重复触发
        if (window.history && window.history.replaceState) {
          const newQuery = { ...route.query }
          delete newQuery.type
          delete newQuery.source
          delete newQuery.config
          delete newQuery.url
          delete newQuery.title
          delete newQuery.desc
          delete newQuery.platform
          window.history.replaceState({}, '', {
            path: route.path,
            query: newQuery
          })
        }
        
        return // 图文类型处理完成，不再处理其他逻辑
      }
      
      // 视频类型的处理逻辑（打开弹窗）
      if (queryType === 'video') {
        // 打开制作类型选择弹窗
        selectedContentType.value = queryType
        dialogStep.value = 'select'
        contentTypeDialogVisible.value = true
        
        // 如果选择了类型，自动进入配置步骤
        if (selectedContentType.value) {
          // 等待弹窗渲染完成后再进入配置步骤
          setTimeout(() => {
            dialogStep.value = 'config'
            
            // 应用配置
            if (queryConfig) {
              Object.assign(tempConfig.video, queryConfig)
            }
          }, 100)
        }
      }
    } catch (error) {
      console.error('解析爬虫数据列表传入的配置失败:', error)
      ElMessage.error('配置解析失败: ' + error.message)
    }
  }
  
  // 检查是否有从热点中心传入的配置
  const pendingConfigStr = sessionStorage.getItem('hotspot_pending_production_config')
  if (pendingConfigStr) {
    try {
      const pendingConfig = JSON.parse(pendingConfigStr)
      sessionStorage.removeItem('hotspot_pending_production_config') // 清除配置
      
      // 打开制作类型选择弹窗
      selectedContentType.value = pendingConfig.contentType || 'image-text'
      dialogStep.value = 'select'
      contentTypeDialogVisible.value = true
      
      // 如果选择了类型，自动进入配置步骤
      if (selectedContentType.value) {
        // 等待弹窗渲染完成后再进入配置步骤
        setTimeout(() => {
          dialogStep.value = 'config'
          
          // 如果是图文类型，填入传入的内容
          if (selectedContentType.value === 'image-text' && pendingConfig.inputContent) {
            tempConfig.imageText.inputContent = pendingConfig.inputContent
            tempConfig.imageText.contentSourceType = pendingConfig.contentSourceType || 'other'
          }
        }, 100)
      }
    } catch (error) {
      console.error('解析热点中心传入的配置失败:', error)
    }
  }
})

onUnmounted(() => {
  // 清理轮询
  stopImageTextPolling()
  stopArticlePolling()
})

// 账号相关状态
const accountDialogVisible = ref(false)
const tempSelectedAccounts = ref([])
const currentTab = ref(null)

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
  // 如果是视频配置弹窗，不再需要根据平台过滤（平台选择已移除）
  if (accountDialogVisible.value && selectedContentType.value === 'video') {
    return []
  }
  // 如果是tab中的配置，使用currentTab.value.selectedPlatform
  const currentPlatform = currentTab.value ? platformMap[currentTab.value.selectedPlatform] : null
  return currentPlatform ? accountStore.accounts.filter(acc => acc.platform === currentPlatform) : []
})

const ARTICLE_FORM_MODE = import.meta.env.VITE_FORM_MODE || 'test'

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

/**
 * @param {string} content 待展示的正文内容
 * @param {number} length 预览的最大长度
 * @returns {string} 处理后的预览字符串
 */
const formatContentPreview = (content, length = 120) => {
  const text = safeString(content).trim()
  if (!text) return '—'
  return text.length > length ? `${text.slice(0, length)}...` : text
}

// 使用统一的时间工具函数（已从 @/utils/dateTime 导入）

const formatArticlePayload = (tab) => {
  const article = tab.article ? { ...tab.article } : {}
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

// 话题相关状态
const topicDialogVisible = ref(false)
const productionMaterialDialogVisible = ref(false) // 制作中心素材选择弹窗
const selectedProductionMaterial = ref(null) // 选中的素材
const customTopic = ref('')
const isPublishTopicDialog = ref(false) // 标识是否为发布弹窗的话题选择模式

// 推荐话题列表
const recommendedTopics = [
  '游戏', '电影', '音乐', '美食', '旅行', '文化',
  '科技', '生活', '娱乐', '体育', '教育', '艺术',
  '健康', '时尚', '美妆', '摄影', '宠物', '汽车'
]
// 添加新tab - 先显示类型选择 Modal
const addTab = () => {
  console.log('🔔 点击了添加Tab按钮')
  selectedContentType.value = 'image-text' // 默认选择图文
  dialogStep.value = 'select'
  contentTypeDialogVisible.value = true
  // 重置临时配置和编辑状态
  resetTempConfig()
  currentEditingTask.value = null
  console.log('📋 Modal 应该显示了，状态:', contentTypeDialogVisible.value)
}

/**
 * 重置临时配置
 */
const resetTempConfig = () => {
  tempConfig.video = {
    materialUrl: '', // 素材网址
    editingStyle: 'toxic-movie', // 剪辑风格，默认毒舌电影风格
    shotCount: 5, // 分镜数量
    language: 'zh-cn', // 语言
    copywriting: '' // 文案
  }
  tempConfig.imageText = {
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
    imageModel: 'qianwen',
    publishPlatform: 'xiaohongshu'
  }
  tempConfig.article = {
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
 * 进入配置步骤
 */
const goToConfigStep = () => {
  if (!selectedContentType.value) {
    ElMessage.warning('请选择制作类型')
    return
  }
  dialogStep.value = 'config'
}

/**
 * 处理弹窗取消
 */
const handleDialogCancel = () => {
  contentTypeDialogVisible.value = false
  dialogStep.value = 'select'
  resetTempConfig()
}

/**
 * 在弹窗中打开话题选择
 */
const openTopicDialogInModal = () => {
  // 视频配置已移除话题功能
  ElMessage.info('视频配置已更新，不再支持话题选择')
}

/**
 * 确认创建任务
 */
const validateImageTextConfig = () => {
  const cfg = tempConfig.imageText
  if (!cfg.contentSourceType) {
    ElMessage.warning('请选择图文内容来源')
    return false
  }
  if (!cfg.contentLayoutStyle) {
    ElMessage.warning('请选择内容排版风格')
    return false
  }
  if (!cfg.imageModel) {
    ElMessage.warning('请选择生图模型')
    return false
  }
  if (!cfg.publishPlatform) {
    ElMessage.warning('请选择发布平台')
    return false
  }
  if (!cfg.contentWordCount || cfg.contentWordCount <= 0) {
    ElMessage.warning('请选择图文内容字数')
    return false
  }
  if (cfg.contentSourceType === 'custom') {
    if (!cfg.inputContent || !cfg.inputContent.trim()) {
      ElMessage.warning('请输入图文内容')
      return false
    }
  }
  return true
}

const IMAGE_TEXT_WEBHOOK_URL = 'https://aicode.ltd/webhook/create-images'
const ARTICLE_WEBHOOK_URL = 'https://aicode.ltd/webhook/create-artical'
const VIDEO_WEBHOOK_URL = 'https://aicode.ltd/webhook/create-video'

const sendImageTextWebhook = async (imageTextConfig, timeout = 600000) => {
  const payload = convertImageTextToChineseKeys(imageTextConfig)
  console.log('📤 制作中心图文任务 webhook payload:', payload)
  console.log('📋 原始配置中的输入内容:', imageTextConfig.inputContent)
  console.log('📋 payload中的输入内容:', payload['输入内容'])
  console.log('📋 原始配置中的文章链接:', imageTextConfig.externalArticleLink)
  console.log('📋 payload中的文章链接:', payload['配图风格类型选择-文章外图片-文章链接'])
  console.log('📋 完整payload JSON:', JSON.stringify(payload, null, 2))
  
  // 创建超时控制器
  const controller = new AbortController()
  const timeoutId = setTimeout(() => {
    controller.abort()
  }, timeout)
  
  // 验证payload中是否包含"输入内容"字段
  if (!payload.hasOwnProperty('输入内容')) {
    console.error('❌ 错误：payload中缺少"输入内容"字段！')
    console.error('payload对象:', payload)
    console.error('payload的keys:', Object.keys(payload))
  } else {
    console.log('✅ payload中已包含"输入内容"字段，值:', payload['输入内容'])
  }
  
  // 验证JSON序列化后的字符串
  const payloadJson = JSON.stringify(payload)
  console.log('📦 发送的JSON字符串长度:', payloadJson.length)
  console.log('📦 JSON中是否包含"输入内容":', payloadJson.includes('输入内容'))
  
  try {
    const response = await fetch(IMAGE_TEXT_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payloadJson,
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      throw new Error(`Webhook 请求失败：HTTP ${response.status}`)
    }
    return response.json().catch(() => ({}))
  } catch (error) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('n8n连接超时，请检查网络连接或n8n服务状态')
    }
    throw error
  }
}

/**
 * 创建虚拟记录（只在内存中，不保存到数据库）
 * @param {string} contentType - 内容类型: 'article'、'image-text' 或 'video'
 * @returns {object} 虚拟记录对象
 */
const createVirtualRecord = (contentType) => {
  const now = new Date()
  const virtualId = `virtual_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  const createdAt = formatDateWithOffset().replace('T', ' ').substring(0, 19)
  
  if (contentType === 'image-text') {
    return {
      id: virtualId,
      content_type: 'image-text',
      title: '',
      summary: '',
      content: '',
      media_url: '',
      media_ids: [],
      height: null,
      width: null,
      publish_status: 'creating',
      created_at: createdAt,
      isVirtual: true  // 标记为虚拟记录
    }
  } else if (contentType === 'article') {
    return {
      id: virtualId,
      content_type: 'article',
      title: '',
      summary: '',
      content: '',
      media_id: '',
      media_url: '',
      media_ids: [],
      publish_status: 'creating',
      created_at: createdAt,
      isVirtual: true  // 标记为虚拟记录
    }
  } else if (contentType === 'video') {
    return {
      id: virtualId,
      content_type: 'video',
      title: '',
      summary: '',
      content: '',
      video: '',
      keywords: [],
      publish_status: 'creating',
      created_at: createdAt,
      isVirtual: true  // 标记为虚拟记录
    }
  }
  return null
}

/**
 * 剪辑风格英文值到中文名称的映射
 */
const editingStyleMap = {
  'toxic-movie': '毒舌电影风格',
  'playful-nature-doc': '俏皮自然纪录片风格',
  'deep-film-analysis': '深度拉片风格',
  'product-review': '商品评测风格',
  'my-movie': '顾我电影风格',
  'historical-doc': '历史纪录片风格',
  'general-commentary': '通用解说风格',
  'children-animation': '儿童动画片风格',
  'tiktok-product-intro': 'TikTok 商品介绍风格',
  'tiktok-text-product-intro': 'TikTok 文字商品介绍风格',
  'engaging-doc': '引人入胜纪录片风格',
  'speech': '演讲风格',
  'game-commentary': '游戏解说风格',
  'variety-entertainment': '综艺娱乐解说风格',
  'long-to-short': '长视频剪辑短视频风格'
}

/**
 * 发送视频webhook
 */
const sendVideoWebhook = async (videoConfig, timeout = 600000) => {
  // 将英文值转换为中文名称
  const editingStyleChinese = editingStyleMap[videoConfig.editingStyle] || videoConfig.editingStyle || ''
  
  const payload = {
    '素材网址': videoConfig.materialUrl || '',
    '剪辑风格': editingStyleChinese,
    '分镜数量': videoConfig.shotCount || 5,
    '语言': videoConfig.language || 'zh-cn',
    '文案': videoConfig.copywriting || ''
  }
  
  console.log('📤 制作中心视频任务 webhook payload:', payload)
  
  const controller = new AbortController()
  const timeoutId = setTimeout(() => {
    controller.abort()
  }, timeout)
  
  try {
    const response = await fetch(VIDEO_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      throw new Error(`Webhook 请求失败：HTTP ${response.status}`)
    }
    return response.json().catch(() => ({}))
  } catch (error) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('n8n连接超时，请检查网络连接或n8n服务状态')
    }
    throw error
  }
}

/**
 * 轮询检查新记录，用真实记录替换虚拟记录
 * @param {string} virtualId - 虚拟记录ID
 * @param {string} contentType - 内容类型: 'article'、'image-text' 或 'video'
 * @param {number} maxAttempts - 最大尝试次数
 * @param {number} interval - 轮询间隔（毫秒）
 */
const pollForRecordCompletion = async (virtualId, contentType, maxAttempts = 150, interval = 2000) => {
  const startTime = Date.now()
  console.log(`🔍 开始轮询检查${contentType === 'article' ? '文章' : '图文'}记录完成情况`)
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    // 等待间隔时间
    if (attempt > 0) {
      await new Promise(resolve => setTimeout(resolve, interval))
    }
    
    try {
      // 刷新列表
      const query = contentType ? `?content_type=${contentType}` : ''
      const response = await fetch(`${apiBaseUrl}/production/records${query}`)
      if (response.ok) {
        const result = await response.json()
        if (result.code === 200) {
          const newRecords = result.data?.items || []
          
          // 查找是否有新记录（有完整标题和内容，且不是虚拟记录）
          const completedRecord = newRecords.find(r => 
            r.content_type === contentType && 
            r.title && 
            r.title.trim() !== '' && 
            r.title !== '制作中...' &&
            !r.isVirtual
          )
          
          if (completedRecord) {
            // 找到新记录，替换虚拟记录
            const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualId)
            if (virtualIndex !== -1) {
              // 用真实记录替换虚拟记录
              productionRecords.value[virtualIndex] = completedRecord
            } else {
              // 如果找不到虚拟记录，直接添加新记录
              productionRecords.value.unshift(completedRecord)
            }
            
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
            const typeLabel = contentType === 'article' ? '文章' : contentType === 'image-text' ? '图文' : '视频'
            console.log(`✅ ${typeLabel}记录已完成，耗时 ${elapsed}秒`)
            return true
          }
        }
      }
    } catch (error) {
      console.error('轮询检查失败:', error)
    }
    
    if (attempt < maxAttempts - 1) {
      console.log(`⏳ 等待n8n返回结果... (${attempt + 1}/${maxAttempts})`)
    }
  }
  
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
  console.warn(`⚠️ 轮询超时（${elapsed}秒），未检测到完成记录`)
  return false
}

/**
 * 轮询检查新记录，直到找到新记录或超时
 * @param {string} contentType - 内容类型: 'article' 或 'image-text'
 * @param {number} maxAttempts - 最大尝试次数
 * @param {number} interval - 轮询间隔（毫秒）
 */
const pollForNewRecord = async (contentType, maxAttempts = 30, interval = 2000) => {
  const startTime = Date.now()
  // 记录初始记录数量
  const initialCount = productionRecords.value.filter(r => r.content_type === contentType).length
  console.log(`🔍 开始轮询检查新${contentType === 'article' ? '文章' : '图文'}记录，初始数量: ${initialCount}`)
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    // 等待间隔时间
    if (attempt > 0) {
      await new Promise(resolve => setTimeout(resolve, interval))
    }
    
    try {
      // 刷新列表（不显示loading，避免闪烁）
      const query = contentType ? `?content_type=${contentType}` : ''
      const response = await fetch(`${apiBaseUrl}/production/records${query}`)
      if (response.ok) {
        const result = await response.json()
        if (result.code === 200) {
          const newRecords = result.data?.items || []
          const currentCount = newRecords.filter(r => r.content_type === contentType).length
          
          // 如果找到了新记录
          if (currentCount > initialCount) {
            // 更新列表
            productionRecords.value = newRecords
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
            console.log(`✅ 找到新${contentType === 'article' ? '文章' : '图文'}记录，耗时 ${elapsed}秒`)
            return true
          }
        }
      }
    } catch (error) {
      console.error('轮询检查失败:', error)
    }
    
    if (attempt < maxAttempts - 1) {
      console.log(`⏳ 等待n8n返回结果... (${attempt + 1}/${maxAttempts})`)
    }
  }
  
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
  console.warn(`⚠️ 轮询超时（${elapsed}秒），未找到新${contentType === 'article' ? '文章' : '图文'}记录`)
  return false
}

const sendArticleWebhook = async (articleConfig, timeout = 600000) => {
  // formatArticlePayload 期望接收一个 tab 对象，其中包含 article 属性
  const mockTab = { article: articleConfig }
  const payload = formatArticlePayload(mockTab)
  console.log('📤 制作中心文章任务 webhook payload:', payload)
  
  // 创建超时控制器
  const controller = new AbortController()
  const timeoutId = setTimeout(() => {
    controller.abort()
  }, timeout)
  
  try {
    const response = await fetch(ARTICLE_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      throw new Error(`Webhook 请求失败：HTTP ${response.status}`)
    }
    return response.json().catch(() => ({}))
  } catch (error) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('n8n连接超时，请检查网络连接或n8n服务状态')
    }
    throw error
  }
}

const confirmCreateTask = async () => {
  // 添加调试日志，确认当前选择的内容类型
  console.log('🔍 confirmCreateTask - selectedContentType:', selectedContentType.value)
  console.log('🔍 confirmCreateTask - tempConfig:', JSON.stringify(tempConfig, null, 2))
  
  // 验证必填项
  if (selectedContentType.value === 'video') {
    if (!tempConfig.video.materialUrl) {
      ElMessage.warning('请输入素材网址')
      return
    }
    if (!tempConfig.video.editingStyle) {
      ElMessage.warning('请选择剪辑风格')
      return
    }
    if (!tempConfig.video.shotCount) {
      ElMessage.warning('请选择分镜数量')
      return
    }
    if (!tempConfig.video.language) {
      ElMessage.warning('请选择语言')
      return
    }
    
    // 调用视频 webhook
    try {
      // 立即关闭弹窗
      contentTypeDialogVisible.value = false
      dialogStep.value = 'select'
      
      // 保存配置副本，因为resetTempConfig会清空
      const videoConfigCopy = { ...tempConfig.video }
      resetTempConfig()
      
      // 创建虚拟记录并添加到列表顶部
      const virtualRecord = createVirtualRecord('video')
      if (virtualRecord) {
        productionRecords.value.unshift(virtualRecord)
        console.log('✅ 虚拟视频记录已添加到列表，ID:', virtualRecord.id)
      }
      
      // 异步调用webhook，不阻塞
      console.log('🔍 准备发送视频任务，videoConfigCopy:', videoConfigCopy)
      
      sendVideoWebhook(videoConfigCopy, 600000) // 10分钟超时
        .then(result => {
          console.log('✅ 视频任务 webhook 调用成功:', result)
          
          // 如果webhook立即返回了完整数据，保存到后端并更新虚拟记录
          if (result && (result.title || result.data?.title)) {
            const title = result.title || result.data?.title || `视频任务-${formatLocalDateTime(new Date())}`
            const desc = result.desc || result.data?.desc || ''
            const keywords = result.keywords || result.data?.keywords || []
            const video = result.video || result.data?.video || ''
            
            // 保存到后端（包含素材网址）
            fetch(`${apiBaseUrl}/production/video`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                title, 
                desc, 
                keywords, 
                video,
                material_url: videoConfig.materialUrl || ''  // 保存素材网址
              })
            })
              .then(saveResponse => saveResponse.json())
              .then(saveResult => {
                if (saveResult.code === 200 && saveResult.data?.id) {
                  // 用真实记录替换虚拟记录
                  const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualRecord.id)
                  if (virtualIndex !== -1) {
                    fetchProductionRecords().then(() => {
                      ElMessage.success('✅ 视频任务已完成')
                    })
                  }
                }
              })
              .catch(saveError => {
                console.error('保存视频记录失败:', saveError)
              })
            return
          }
          
          // 启动轮询，等待n8n返回结果并替换虚拟记录
          pollForRecordCompletion(virtualRecord.id, 'video', 300, 2000)
            .then(found => {
              if (found) {
                ElMessage.success('✅ 视频任务已完成，列表已更新')
              } else {
                ElMessage.warning('⚠️ 视频任务已发送，但未检测到完成记录，虚拟记录将保留，请稍后手动刷新')
              }
            })
        })
        .catch(error => {
          console.error('创建视频任务时调用 webhook 失败:', error)
          const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualRecord.id)
          if (virtualIndex !== -1) {
            // 启动轮询，即使webhook失败也继续等待
            pollForRecordCompletion(virtualRecord.id, 'video', 300, 2000)
              .then(found => {
                if (found) {
                  ElMessage.success('✅ 视频任务已完成，列表已更新')
                } else {
                  ElMessage.warning('⚠️ 视频任务已发送，但未检测到完成记录，虚拟记录将保留，请稍后手动刷新')
                }
              })
          }
          if (error.message && (error.message.includes('超时') || error.message.includes('n8n') || error.message.includes('连接'))) {
            ElMessage.warning('⚠️ n8n连接异常：' + error.message + '，但任务可能仍在处理中，虚拟记录将保留')
          } else if (error.message && error.message.includes('Failed to fetch')) {
            ElMessage.warning('⚠️ 无法连接到n8n服务，但任务可能仍在处理中，虚拟记录将保留')
          } else {
            ElMessage.warning('⚠️ ' + (error.message || '创建视频任务时出现错误，但任务可能仍在处理中，虚拟记录将保留'))
          }
        })
    } catch (error) {
      console.error('创建视频任务失败:', error)
      ElMessage.error(error.message || '创建视频任务失败，请稍后重试')
      contentTypeDialogVisible.value = false
      dialogStep.value = 'select'
      resetTempConfig()
      return
    }
  } else if (selectedContentType.value === 'image-text') {
    console.log('✅ 确认是图文类型，准备调用 sendImageTextWebhook')
    console.log('✅ tempConfig.imageText:', JSON.stringify(tempConfig.imageText, null, 2))
    
    if (!validateImageTextConfig()) return
    try {
      // 立即关闭弹窗
      contentTypeDialogVisible.value = false
      dialogStep.value = 'select'
      
      // 保存配置副本，因为resetTempConfig会清空
      const imageTextConfigCopy = { ...tempConfig.imageText }
      resetTempConfig()
      
      // 创建虚拟记录并添加到列表顶部
      const virtualRecord = createVirtualRecord('image-text')
      if (virtualRecord) {
        productionRecords.value.unshift(virtualRecord)
        console.log('✅ 虚拟图文记录已添加到列表，ID:', virtualRecord.id)
        // 如果有虚拟记录，确保轮询正在运行
        if (!imageTextPollingInterval) {
          startImageTextPolling()
        }
      }
      
      // 异步调用webhook，不阻塞
      console.log('🔍 准备发送图文任务，imageTextConfigCopy:', imageTextConfigCopy)
      console.log('🔍 inputContent值:', imageTextConfigCopy.inputContent)
      console.log('🔍 完整配置对象:', JSON.stringify(imageTextConfigCopy, null, 2))
      
      sendImageTextWebhook(imageTextConfigCopy, 600000) // 10分钟超时
        .then(result => {
          console.log('✅ 图文任务 webhook 调用成功:', result)
          
          // 如果webhook立即返回了完整数据，保存到后端并更新虚拟记录
          if (result && (result.title || result.data?.title)) {
            const title = result.title || result.data?.title || `图文任务-${formatLocalDateTime(new Date())}`
            const content = result.content || result.data?.content || '图文内容生成中...'
            const mediaIds = result.media_ids || result.data?.media_ids || []
            const height = result.height || result.data?.height || 1080
            const width = result.width || result.data?.width || 1920
            
            // 保存到后端
            // ⚠️ 重要：后端接口期望 urls 字段（数组），不是 media_ids
            // 数据流：前端 urls 数组 → 后端保存到 media_ids 字段（JSON字符串）→ 读取时解析为数组
            // 如果使用错误的字段名 media_ids，后端会返回 400 错误
            const urls = Array.isArray(mediaIds) ? mediaIds : (mediaIds ? [mediaIds] : [])
            console.log('💾 保存图文记录到后端，urls数组:', urls)
            if (urls.length === 0) {
              console.warn('⚠️ 警告：urls 数组为空，可能无法正确保存')
            }
            fetch(`${apiBaseUrl}/production/image-text`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ title, content, urls: urls, height, width })
            })
              .then(saveResponse => saveResponse.json())
              .then(saveResult => {
                if (saveResult.code === 200 && saveResult.data?.id) {
                  // 用真实记录替换虚拟记录
                  const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualRecord.id)
                  if (virtualIndex !== -1) {
                    fetchProductionRecords().then(() => {
                      ElMessage.success('✅ 图文任务已完成')
                    })
                  }
                }
              })
              .catch(saveError => {
                console.error('保存图文记录失败:', saveError)
              })
            return
          }
          
          // 启动轮询，等待n8n返回结果并替换虚拟记录（10分钟超时：300次 * 2秒）
          pollForRecordCompletion(virtualRecord.id, 'image-text', 300, 2000)
            .then(found => {
              if (found) {
                ElMessage.success('✅ 图文任务已完成，列表已更新')
              } else {
                // 轮询超时，但保留虚拟记录，提示用户手动刷新
                ElMessage.warning('⚠️ 图文任务已发送，但未检测到完成记录，虚拟记录将保留，请稍后手动刷新')
              }
            })
        })
        .catch(error => {
          console.error('创建图文任务时调用 webhook 失败:', error)
          // 不移除虚拟记录，保留它以便用户知道任务已发送
          // 更新虚拟记录状态为"失败"（可选，或者保持"制作中"状态）
          const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualRecord.id)
          if (virtualIndex !== -1) {
            // 保留虚拟记录，但可以更新状态为"失败"
            // productionRecords.value[virtualIndex].publish_status = 'failed'
            // 或者保持"制作中"状态，继续轮询等待真实记录
            // 启动轮询，即使webhook失败也继续等待（可能n8n仍在处理）
            pollForRecordCompletion(virtualRecord.id, 'image-text', 300, 2000)
              .then(found => {
                if (found) {
                  ElMessage.success('✅ 图文任务已完成，列表已更新')
                } else {
                  ElMessage.warning('⚠️ 图文任务已发送，但未检测到完成记录，虚拟记录将保留，请稍后手动刷新')
                }
              })
          }
          // 检查是否是n8n连接问题
          if (error.message && (error.message.includes('超时') || error.message.includes('n8n') || error.message.includes('连接'))) {
            ElMessage.warning('⚠️ n8n连接异常：' + error.message + '，但任务可能仍在处理中，虚拟记录将保留')
          } else if (error.message && error.message.includes('Failed to fetch')) {
            ElMessage.warning('⚠️ 无法连接到n8n服务，但任务可能仍在处理中，虚拟记录将保留')
          } else {
            ElMessage.warning('⚠️ ' + (error.message || '创建图文任务时出现错误，但任务可能仍在处理中，虚拟记录将保留'))
          }
        })
    } catch (error) {
      console.error('创建图文任务失败:', error)
      ElMessage.error(error.message || '创建图文任务失败，请稍后重试')
      // 即使失败也关闭弹窗
      contentTypeDialogVisible.value = false
      dialogStep.value = 'select'
      resetTempConfig()
      return
    }
  } else if (selectedContentType.value === 'article') {
    console.log('✅ 确认是文章类型，准备调用 sendArticleWebhook')
    console.log('✅ tempConfig.article:', JSON.stringify(tempConfig.article, null, 2))
    
    if (!tempConfig.article.writingMode) {
      ElMessage.warning('请选择写作模式')
      return
    }
    // 根据写作模式进行不同的验证
    if (['polish', 'imitate', 'reprint'].includes(tempConfig.article.writingMode)) {
      if (!tempConfig.article.articleLink) {
        ElMessage.warning('请输入对标文章链接')
        return
      }
    }
    if (tempConfig.article.writingMode === 'imitate') {
      if (!tempConfig.article.imitateTopic) {
        ElMessage.warning('请输入仿写主题内容')
        return
      }
    }
    if (tempConfig.article.writingMode === 'original') {
      if (!tempConfig.article.originalKeywords) {
        ElMessage.warning('请输入深度研究领域关键词')
        return
      }
    }
    // 调用文章 webhook
    try {
      // 立即关闭弹窗
      contentTypeDialogVisible.value = false
      dialogStep.value = 'select'
      
      // 保存配置副本，因为resetTempConfig会清空
      const articleConfigCopy = { ...tempConfig.article }
      resetTempConfig()
      
      // 创建虚拟记录并添加到列表顶部
      const virtualRecord = createVirtualRecord('article')
      if (virtualRecord) {
        productionRecords.value.unshift(virtualRecord)
        console.log('✅ 虚拟文章记录已添加到列表，ID:', virtualRecord.id)
        // 如果有虚拟记录，确保轮询正在运行
        if (!articlePollingInterval) {
          startArticlePolling()
        }
      }
      
      // 异步调用webhook，不阻塞
      console.log('🔍 准备发送文章任务，articleConfigCopy:', articleConfigCopy)
      sendArticleWebhook(articleConfigCopy, 600000) // 10分钟超时
        .then(result => {
          console.log('✅ 文章任务 webhook 调用成功:', result)
          
          // 如果webhook立即返回了完整数据，保存到后端并更新虚拟记录
          if (result && (result.article_title || result.title || result.data?.article_title || result.data?.title)) {
            const articleTitle = result?.article_title || result?.title || result?.data?.article_title || result?.data?.title || `文章任务-${formatLocalDateTime(new Date())}`
            const articleContent = result?.article_content || result?.content || result?.data?.article_content || result?.data?.content || '文章内容生成中，请稍候...'
            const articleDesc = result?.article_desc || result?.description || result?.data?.article_desc || result?.data?.description || ''
            const articleMediaId = result?.article_media_id || result?.media_id || result?.data?.article_media_id || result?.data?.media_id || ''
            const articleMediaUrl = result?.article_media_url || result?.media_url || result?.data?.article_media_url || result?.data?.media_url || ''
            
            // 保存到后端
            fetch(`${apiBaseUrl}/production/articles`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                article_title: articleTitle,
                article_content: articleContent,
                article_desc: articleDesc,
                article_media_id: articleMediaId,
                article_media_url: articleMediaUrl
              })
            })
              .then(saveResponse => saveResponse.json())
              .then(saveResult => {
                if (saveResult.code === 200 && saveResult.data?.id) {
                  // 用真实记录替换虚拟记录
                  const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualRecord.id)
                  if (virtualIndex !== -1) {
                    fetchProductionRecords().then(() => {
                      ElMessage.success('✅ 文章任务已完成')
                    })
                  }
                }
              })
              .catch(saveError => {
                console.error('保存文章记录失败:', saveError)
              })
            return
          }
          
          // 启动轮询，等待n8n返回结果并替换虚拟记录（10分钟超时：300次 * 2秒）
          pollForRecordCompletion(virtualRecord.id, 'article', 300, 2000)
            .then(found => {
              if (found) {
                ElMessage.success('✅ 文章任务已完成，列表已更新')
              } else {
                // 轮询超时，但保留虚拟记录，提示用户手动刷新
                ElMessage.warning('⚠️ 文章任务已发送，但未检测到完成记录，虚拟记录将保留，请稍后手动刷新')
              }
            })
        })
        .catch(error => {
          console.error('创建文章任务时调用 webhook 失败:', error)
          // 不移除虚拟记录，保留它以便用户知道任务已发送
          // 更新虚拟记录状态为"失败"（可选，或者保持"制作中"状态）
          const virtualIndex = productionRecords.value.findIndex(r => r.id === virtualRecord.id)
          if (virtualIndex !== -1) {
            // 保留虚拟记录，但可以更新状态为"失败"
            // productionRecords.value[virtualIndex].publish_status = 'failed'
            // 或者保持"制作中"状态，继续轮询等待真实记录
            // 启动轮询，即使webhook失败也继续等待（可能n8n仍在处理）
            pollForRecordCompletion(virtualRecord.id, 'article', 300, 2000)
              .then(found => {
                if (found) {
                  ElMessage.success('✅ 文章任务已完成，列表已更新')
                } else {
                  ElMessage.warning('⚠️ 文章任务已发送，但未检测到完成记录，虚拟记录将保留，请稍后手动刷新')
                }
              })
          }
          // 检查是否是n8n连接问题
          if (error.message && (error.message.includes('超时') || error.message.includes('n8n') || error.message.includes('连接'))) {
            ElMessage.warning('⚠️ n8n连接异常：' + error.message + '，但任务可能仍在处理中，虚拟记录将保留')
          } else if (error.message && error.message.includes('Failed to fetch')) {
            ElMessage.warning('⚠️ 无法连接到n8n服务，但任务可能仍在处理中，虚拟记录将保留')
          } else {
            ElMessage.warning('⚠️ ' + (error.message || '创建文章任务时出现错误，但任务可能仍在处理中，虚拟记录将保留'))
          }
        })
    } catch (error) {
      console.error('创建文章任务失败:', error)
      ElMessage.error(error.message || '创建文章任务失败，请稍后重试')
      // 即使失败也关闭弹窗
      contentTypeDialogVisible.value = false
      dialogStep.value = 'select'
      resetTempConfig()
      return
    }
  }
  
  // 注意：视频类型已经在上面的if块中处理并return了，不会执行到这里
  // 如果是编辑模式，更新现有任务
  if (currentEditingTask.value) {
    const task = currentEditingTask.value
    
    // 应用配置到现有任务
    if (selectedContentType.value === 'video') {
      Object.assign(task.video, tempConfig.video)
    } else if (selectedContentType.value === 'image-text') {
      Object.assign(task.imageText, tempConfig.imageText)
    } else if (selectedContentType.value === 'article') {
      Object.assign(task.article, tempConfig.article)
    }
    
    ElMessage.success(`已更新${getContentTypeLabel(selectedContentType.value)}类型的制作任务`)
    currentEditingTask.value = null
  } else {
    // 创建新tab并应用配置
    tabCounter++
    const newTab = makeNewTab()
    newTab.name = `tab${tabCounter}`
    newTab.label = `制作${tabCounter}`
    newTab.contentType = selectedContentType.value
    
    // 应用配置到新tab
    if (selectedContentType.value === 'video') {
      Object.assign(newTab.video, tempConfig.video)
    } else if (selectedContentType.value === 'image-text') {
      Object.assign(newTab.imageText, tempConfig.imageText)
    } else if (selectedContentType.value === 'article') {
      Object.assign(newTab.article, tempConfig.article)
    }
    
    tabs.push(newTab)
    activeTab.value = newTab.name
    ElMessage.success(`已创建${getContentTypeLabel(selectedContentType.value)}类型的制作任务`)
  }
  
  // 关闭弹窗并重置
  contentTypeDialogVisible.value = false
  dialogStep.value = 'select'
  resetTempConfig()
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
  'none': '无',
  
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
  console.log('🔍 convertImageTextToChineseKeys - 接收到的imageTextData:', JSON.stringify(imageTextData, null, 2))
  console.log('🔍 convertImageTextToChineseKeys - imageTextData类型:', typeof imageTextData)
  console.log('🔍 convertImageTextToChineseKeys - imageTextData是否为null:', imageTextData === null)
  console.log('🔍 convertImageTextToChineseKeys - imageTextData是否为undefined:', imageTextData === undefined)
  
  // 确保输入内容字段被正确传递（即使为空字符串也要发送）
  const inputContent = imageTextData && imageTextData.inputContent !== undefined && imageTextData.inputContent !== null 
    ? String(imageTextData.inputContent) 
    : ""
  console.log('🔍 convertImageTextToChineseKeys - inputContent值:', inputContent)
  console.log('🔍 convertImageTextToChineseKeys - imageTextData.inputContent原始值:', imageTextData?.inputContent)
  console.log('🔍 convertImageTextToChineseKeys - imageTextData完整对象:', JSON.stringify(imageTextData, null, 2))
  
  // 验证imageTextData是否包含必要的字段
  if (!imageTextData || typeof imageTextData !== 'object') {
    console.error('❌ 错误：imageTextData不是有效对象！', imageTextData)
    throw new Error('图文配置数据无效')
  }
  
  // 辅助函数：安全获取值，即使为0或false也返回
  const safeGet = (value, defaultValue = "") => {
    if (value === null || value === undefined) return defaultValue
    return value
  }
  
  // 辅助函数：安全转换为字符串，即使为0也转换
  const safeString = (value, defaultValue = "") => {
    if (value === null || value === undefined) return defaultValue
    if (value === 0 || value === false) return String(value)
    return value ? String(value) : defaultValue
  }
  
  const payload = {
    "内容来源类型": getChineseLabel(imageTextData.contentSourceType),
    "输入内容": inputContent,
    "内容排版风格": getChineseLabel(imageTextData.contentLayoutStyle),
    "内容排版类型-小红书爆款风格": safeGet(imageTextData.contentLayoutReference, ""),
    "配图风格类型选择": getChineseLabel(imageTextData.imageStyleType),
    "配图风格选择-小红书爆款参考链接": safeGet(imageTextData.imageStyleReference, ""),
    "配图-比例": safeGet(imageTextData.imageRatio, ""),
    "封面图风格类型选择": getChineseLabel(imageTextData.coverStyleType),
    "封面图风格选择-小红书爆款风格": safeGet(imageTextData.coverStyleReference, ""),
    "封面图-比例": safeGet(imageTextData.coverImageRatio, ""),
    "配图张数": safeString(imageTextData.imageCount, ""),
    "生图模型": getChineseLabel(imageTextData.imageModel),
    "发布平台": getChineseLabel(imageTextData.publishPlatform),
    "图文内容字数": safeString(imageTextData.contentWordCount, ""),
    "封面图-信息图类型": getChineseLabel(imageTextData.infoGraphicType),
    "配图风格类型选择-文章外图片-文章链接": safeGet(imageTextData.externalArticleLink, ""),
    "配图风格类型选择-文章外图片-文章来源": getChineseLabel(imageTextData.externalArticleSource),
    "submittedAt": formatDateWithOffset(),
    "formMode": "production"
  }
  
  console.log('🔍 convertImageTextToChineseKeys - 最终payload:', JSON.stringify(payload, null, 2))
  return payload
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
    
    // 调用后端代理接口（解决CORS问题）
    const apiUrl = '/api/generateImageText'
    
    const startTime = Date.now()
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(chineseData)
    })
    
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
    const webhookUrl = 'https://aicode.ltd/webhook/c155e570-faf5-4351-b1bd-7b908cf6db36'
    
    const startTime = Date.now()
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      controller.abort()
    }, 10 * 60 * 1000)

    let response
    try {
      response = await fetch(webhookUrl, {
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
  
  // 视频配置已移除话题功能
  const targetTopics = currentTab.value?.selectedTopics || []
  
  if (!targetTopics.includes(customTopic.value.trim())) {
    targetTopics.push(customTopic.value.trim())
    customTopic.value = ''
    ElMessage.success('话题添加成功')
  } else {
    ElMessage.warning('话题已存在')
  }
}

// 切换推荐话题
const toggleRecommendedTopic = (topic) => {
  // 视频配置已移除话题功能
  const targetTopics = currentTab.value?.selectedTopics || []
  
  if (!targetTopics) return
  
  const index = targetTopics.indexOf(topic)
  if (index > -1) {
    targetTopics.splice(index, 1)
  } else {
    targetTopics.push(topic)
  }
}

/**
 * 获取话题按钮类型（用于显示选中状态）
 */
const getTopicButtonType = (topic) => {
  // 视频配置已移除话题功能
  const targetTopics = currentTab.value?.selectedTopics || []
  return targetTopics?.includes(topic) ? 'primary' : 'default'
}

// 删除话题
const removeTopic = (tab, index) => {
  tab.selectedTopics.splice(index, 1)
}

// 确认添加话题
const confirmTopicSelection = () => {
  topicDialogVisible.value = false
  customTopic.value = ''
  // 如果是在弹窗中，不需要清空 currentTab
  if (!(contentTypeDialogVisible.value && dialogStep.value === 'config')) {
    currentTab.value = null
  }
  ElMessage.success('添加话题完成')
}

// 发布弹窗的话题选择相关函数
const openPublishTopicDialog = () => {
  isPublishTopicDialog.value = true
  customTopic.value = ''
  topicDialogVisible.value = true
  console.log(topicDialogVisible,'topicDialogVisible')
}

const removePublishTopic = (index) => {
  publishPlatformForm.selectedTopics.splice(index, 1)
}

const addCustomTopicForPublish = () => {
  if (!customTopic.value.trim()) {
    ElMessage.warning('请输入话题内容')
    return
  }
  const topic = customTopic.value.trim().replace(/^#/, '') // 移除开头的#号
  if (!publishPlatformForm.selectedTopics.includes(topic)) {
    publishPlatformForm.selectedTopics.push(topic)
    customTopic.value = ''
    ElMessage.success('话题添加成功')
  } else {
    ElMessage.warning('该话题已存在')
  }
}

const toggleRecommendedTopicForDialog = (topic) => {
  if (isPublishTopicDialog.value) {
    // 发布弹窗模式
    const index = publishPlatformForm.selectedTopics.indexOf(topic)
    if (index > -1) {
      publishPlatformForm.selectedTopics.splice(index, 1)
    } else {
      publishPlatformForm.selectedTopics.push(topic)
    }
  } else {
    // 制作配置模式
    toggleRecommendedTopic(topic)
  }
}

const getTopicButtonTypeForDialog = (topic) => {
  if (isPublishTopicDialog.value) {
    // 发布弹窗模式
    return publishPlatformForm.selectedTopics.includes(topic) ? 'primary' : 'default'
  } else {
    // 制作配置模式
    return getTopicButtonType(topic)
  }
}

const confirmTopicSelectionForPublish = () => {
  topicDialogVisible.value = false
  isPublishTopicDialog.value = false
  customTopic.value = ''
  ElMessage.success('添加话题完成')
}

// 账号选择相关方法
// 打开账号选择弹窗（用于视频配置）
const openAccountDialogForVideo = () => {
  tempSelectedAccounts.value = [...tempConfig.video.selectedAccounts]
  accountDialogVisible.value = true
}

// 删除视频配置中的账号
const removeVideoAccount = (index) => {
  tempConfig.video.selectedAccounts.splice(index, 1)
}

// 话题相关方法
// 打开话题选择弹窗（用于视频配置）
const openTopicDialogForVideo = () => {
  customTopic.value = ''
  topicDialogVisible.value = true
}

// 添加自定义话题（用于视频配置）
const addCustomTopicForVideo = () => {
  if (!customTopic.value || !customTopic.value.trim()) {
    ElMessage.warning('请输入话题内容')
    return
  }
  const topic = customTopic.value.trim().replace(/^#/, '') // 移除开头的#号
  if (!tempConfig.video.selectedTopics.includes(topic)) {
    tempConfig.video.selectedTopics.push(topic)
    customTopic.value = ''
  } else {
    ElMessage.warning('该话题已存在')
  }
}

// 切换推荐话题（用于视频配置）
const toggleRecommendedTopicForVideo = (topic) => {
  const index = tempConfig.video.selectedTopics.indexOf(topic)
  if (index > -1) {
    tempConfig.video.selectedTopics.splice(index, 1)
  } else {
    tempConfig.video.selectedTopics.push(topic)
  }
}

// 删除视频配置中的话题
const removeVideoTopic = (index) => {
  tempConfig.video.selectedTopics.splice(index, 1)
}

// 确认添加话题（用于视频配置）
const confirmTopicSelectionForVideo = () => {
  topicDialogVisible.value = false
  customTopic.value = ''
  ElMessage.success('添加话题完成')
}

// 打开账号选择弹窗（用于tab配置）
const openAccountDialog = (tab) => {
  currentTab.value = tab
  tempSelectedAccounts.value = [...tab.selectedAccounts]
  accountDialogVisible.value = true
}

// 确认账号选择
const confirmAccountSelection = () => {
  // 如果是视频配置弹窗
  if (selectedContentType.value === 'video') {
    tempConfig.video.selectedAccounts = [...tempSelectedAccounts.value]
  } else if (currentTab.value) {
    // 如果是tab配置
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

    // 调用后端发布API
    fetch(`${apiBaseUrl}/postVideo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders.value
      },
      body: JSON.stringify(publishData)
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
  
  // 如果素材库为空，先获取素材数据
  if (materials.value.length === 0) {
    try {
      const response = await materialApi.getAllMaterials()
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
        const fileInfo = {
          name: material.filename,
          url: materialApi.getMaterialPreviewUrl(material.file_path.split('/').pop()),
          path: material.file_path,
          size: material.filesize * 1024 * 1024, // 转换为字节
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

.production-center {
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
      margin-top: 20px;
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
  .production-content {
    flex: 1;
    background-color: #fff;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    padding: 24px;
    
    // 任务列表容器
    .task-list-container {
      width: 100%;
      
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
      
      .empty-task-list {
        padding: 60px 0;
        text-align: center;
      }
    }

    .record-detail {
      .preview-container {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 20px 0;
        min-height: 400px;
      }

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

  // 已上传文件列表样式
  .uploaded-files {
    margin-top: 20px;
    
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
  
  // 添加话题弹窗样式（已移至全局样式，因为使用了 append-to-body）

  // 内容类型选择 Modal 样式 - 高级扁平设计
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
        animation: slideInDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      }
    }
    
    @keyframes slideInDown {
      from {
        opacity: 0;
        transform: translateY(-8px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
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
          animation: cardFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
          
          &:nth-child(1) {
            animation-delay: 0.05s;
          }
          &:nth-child(2) {
            animation-delay: 0.1s;
          }
          &:nth-child(3) {
            animation-delay: 0.15s;
          }
          
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
            background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
            
            &::before {
              opacity: 1;
              transform: scaleX(1);
            }
            
            .type-card-icon {
              transform: scale(1.1) rotate(5deg);
              box-shadow: 0 8px 16px rgba(59, 130, 246, 0.2);
            }
            
            .type-card-title {
              color: #3b82f6;
            }
          }
          
          &.selected {
            border-color: #3b82f6;
            border-width: 2px;
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #f0f9ff 100%);
            box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2), 0 4px 16px rgba(59, 130, 246, 0.1);
            transform: translateY(-2px);
            animation: selectedPulse 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            
            &::before {
              opacity: 1;
              transform: scaleX(1);
            }
            
            .type-card-icon {
              animation: iconBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }
          }
          
          @keyframes cardFadeIn {
            from {
              opacity: 0;
              transform: translateY(20px) scale(0.95);
            }
            to {
              opacity: 1;
              transform: translateY(0) scale(1);
            }
          }
          
          @keyframes selectedPulse {
            0%, 100% {
              box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2), 0 4px 16px rgba(59, 130, 246, 0.1);
            }
            50% {
              box-shadow: 0 16px 40px rgba(59, 130, 246, 0.3), 0 6px 20px rgba(59, 130, 246, 0.15);
            }
          }
          
          @keyframes iconBounce {
            0%, 100% {
              transform: scale(1) rotate(0deg);
            }
            25% {
              transform: scale(1.15) rotate(-5deg);
            }
            50% {
              transform: scale(1.2) rotate(5deg);
            }
            75% {
              transform: scale(1.1) rotate(-3deg);
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
            position: relative;
            
            &::after {
              content: '';
              position: absolute;
              inset: -2px;
              border-radius: 16px;
              padding: 2px;
              background: linear-gradient(135deg, #3b82f6, #8b5cf6);
              -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
              -webkit-mask-composite: xor;
              mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
              mask-composite: exclude;
              opacity: 0;
              transition: opacity 0.3s ease;
            }
            
            .el-icon {
              color: #3b82f6;
              font-size: 30px;
              transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
              filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.2));
            }
          }
          
          &.selected .type-card-icon {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
            
            &::after {
              opacity: 1;
            }
            
            .el-icon {
              color: white;
              filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
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
              transition: all 0.3s ease;
              letter-spacing: -0.01em;
            }
            
            .type-card-desc {
              font-size: 12px;
              color: #6b7280;
              margin: 0 0 14px 0;
              line-height: 1.5;
              min-height: 36px;
              transition: color 0.3s ease;
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
                opacity: 0.9;
                transition: all 0.3s ease;
                transform: translateX(0);
                
                &:hover {
                  opacity: 1;
                  transform: translateX(4px);
                  color: #111827;
                }
                
                &:last-child {
                  margin-bottom: 0;
                }
                
                .el-icon {
                  color: #10b981;
                  font-size: 13px;
                  flex-shrink: 0;
                  transition: all 0.3s ease;
                  filter: drop-shadow(0 1px 2px rgba(16, 185, 129, 0.2));
                }
                
                &:hover .el-icon {
                  transform: scale(1.2) rotate(5deg);
                  color: #059669;
                }
              }
            }
          }
          
          &.selected .type-card-content {
            .type-card-title {
              color: #3b82f6;
              font-weight: 700;
            }
            
            .type-card-desc {
              color: #4b5563;
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
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            
            &::before {
              content: '';
              position: absolute;
              inset: -4px;
              border-radius: 50%;
              background: linear-gradient(135deg, #3b82f6, #8b5cf6);
              opacity: 0.3;
              animation: ripple 1.5s ease-out infinite;
            }
            
            .el-icon {
              color: white;
              font-size: 14px;
              position: relative;
              z-index: 1;
            }
          }
          
          &.selected .type-card-check {
            opacity: 1;
            transform: scale(1);
            animation: checkPop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
          }
          
          @keyframes checkPop {
            0% {
              transform: scale(0) rotate(-180deg);
            }
            50% {
              transform: scale(1.2) rotate(10deg);
            }
            100% {
              transform: scale(1) rotate(0deg);
            }
          }
          
          @keyframes ripple {
            0% {
              transform: scale(0.8);
              opacity: 0.3;
            }
            100% {
              transform: scale(1.5);
              opacity: 0;
            }
          }
        }
      }
    }
    
    .dialog-footer-custom {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      padding: 20px 24px;
      background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
      border-top: 1px solid #f3f4f6;
      
      .el-button {
        border-radius: 8px;
        font-size: 14px;
        height: 38px;
        padding: 0 24px;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 50%;
          width: 0;
          height: 0;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.3);
          transform: translate(-50%, -50%);
          transition: width 0.6s, height 0.6s;
        }
        
        &:active::before {
          width: 300px;
          height: 300px;
        }
        
        &.el-button--primary {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          border: none;
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          color: white;
          
          &:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            transform: translateY(-1px);
          }
          
          &:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
          }
        }
        
        &.el-button--default {
          background: #ffffff;
          border: 1.5px solid #e5e7eb;
          color: #374151;
          
          &:hover {
            background: #f9fafb;
            border-color: #d1d5db;
            color: #111827;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          }
          
          &:active {
            transform: translateY(0);
          }
        }
      }
    }
    
    .config-form-container {
      padding: 0;
      
      .config-form {
        padding: 20px 0;
        
        // 图文、视频、文章配置都使用外部样式
        &.image-text-content,
        &.video-content,
        &.article-content {
          padding: 0;
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


  // 添加全局动画
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .video-content .form-section,
  .image-text-content .form-section,
  .article-content .form-section {
    animation: slideIn 0.3s ease-out backwards;
    
    @for $i from 1 through 20 {
      &:nth-child(#{$i}) {
        animation-delay: #{$i * 0.03}s;
      }
    }
  }
  
  // 发布平台选择弹窗样式
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
    
    .publish-platform-content {
      padding: 24px 28px;
      max-width: 100%;
      width: 100%;
      margin: 0 auto;
      max-height: 70vh;
      overflow-y: auto;
      
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
        margin-bottom: 0;
        border: 1px solid #e2e8f0;
        
        h3 {
          font-size: 14px;
          font-weight: 600;
          color: #1e293b;
          margin: 0 0 16px 0;
          display: flex;
          align-items: center;
          gap: 4px;
          
          .required {
            color: #ef4444;
            font-size: 14px;
          }
        }
        
        :deep(.el-radio-group) {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          
          .el-radio {
            margin: 0;
            height: auto;
            
            :deep(.el-radio__input) {
              .el-radio__inner {
                width: 18px;
                height: 18px;
                border-color: #cbd5e1;
                
                &::after {
                  width: 8px;
                  height: 8px;
                  background-color: #6366f1;
                }
              }
              
              &.is-checked .el-radio__inner {
                border-color: #6366f1;
                background-color: #6366f1;
              }
            }
            
            :deep(.el-radio__label) {
              padding-left: 8px;
              font-size: 14px;
              color: #475569;
              font-weight: 500;
            }
            
            :deep(.el-radio__input.is-checked + .el-radio__label) {
              color: #6366f1;
            }
          }
        }
      }
      .platform-accounts{
        display: flex;
        flex-direction: row;
        gap: 12px;
        .selected-accounts{
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .select-account-btn{
          align-self: flex-start;
        }
      }
    }
  }

  // 响应式布局
  @media (max-width: 1400px) {
    .video-content,
    .image-text-content,
    .article-content {
      .form-grid {
        gap: 16px;
      }
      
      .form-section {
        padding: 18px 20px;
      }
    }
  }
  
  @media (max-width: 900px) {
    .video-content,
    .image-text-content,
    .article-content {
      .form-grid {
        grid-template-columns: 1fr;
        gap: 16px;
      }
      
      .form-section-full {
        grid-column: 1;
      }
      
      .form-section {
        padding: 16px 18px;
        
        :deep(.el-radio-group) {
          flex-direction: column;
          
          .el-radio {
            width: 100%;
          }
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

// 选中的素材行高亮样式
:deep(.selected-material-row) {
  background-color: #e6f7ff !important;
  
  td {
    background-color: #e6f7ff !important;
  }
  
  &:hover td {
    background-color: #bae7ff !important;
  }
}

// 选中的视频素材行高亮样式（用于发布视频素材选择弹窗）
:deep(.selected-video-material-row) {
  background-color: #f0f9ff !important;
  
  td {
    background-color: #f0f9ff !important;
  }
  
  &:hover td {
    background-color: #dbeafe !important;
  }
}

// 选中的视频预览样式
.selected-video-preview {
  border: 3px solid #67c23a !important;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.4) !important;
  transition: all 0.2s ease;
}

// 素材选择按钮选中状态样式
:deep(.material-selected-btn) {
  font-weight: 600 !important;
  border: 2px solid #67c23a !important;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3) !important;
  transform: scale(1.05);
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4) !important;
    transform: scale(1.08);
  }
}

// 图片预览悬浮框样式（优化：宽度缩短为三分之一，支持多行显示）
:deep(.image-preview-tooltip) {
  padding: 10px 12px !important;
  max-width: 180px !important;
  min-width: 120px !important;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 252, 255, 0.98) 100%) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
  backdrop-filter: blur(8px) !important;
  
  .image-preview-container {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 300px;
    overflow-y: auto;
    
    .preview-image {
      max-width: 100%;
      max-height: 200px;
      border-radius: 6px;
      object-fit: contain;
      background: #fff;
      padding: 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      transition: transform 0.2s ease;
      
      &:hover {
        transform: scale(1.02);
      }
    }
  }
}

// Element Plus表格默认tooltip样式优化（用于正文列等）
// :deep(.el-tooltip__popper) {
//   max-width: 100px !important;
//   padding: 8px 12px !important;
//   background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 252, 255, 0.98) 100%) !important;
//   border: 1px solid rgba(64, 158, 255, 0.2) !important;
//   border-radius: 6px !important;
//   box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
//   backdrop-filter: blur(8px) !important;
//   color: #303133 !important;
//   font-size: 13px !important;
//   line-height: 1.6 !important;
//   word-break: break-word !important;
//   word-wrap: break-word !important;
//   overflow-wrap: break-word !important;
//   white-space: normal !important;
  
//   .el-tooltip__arrow {
//     &::before {
//       background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 252, 255, 0.98) 100%) !important;
//       border: 1px solid rgba(64, 158, 255, 0.2) !important;
//     }
//   }
// }

// 图片/媒资链接列样式（清爽、高级、多行显示）
:deep(.media-link-column) {
  .cell {
    padding: 12px 16px !important;
  }
}

// 标题、摘要、正文列的三行省略样式
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

.media-links-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  
  .media-link-item {
    display: flex;
    align-items: center;
    min-width: 0;
    
    .media-link {
      display: flex;
      align-items: center;
      gap: 6px;
      width: 100%;
      min-width: 0;
      padding: 6px 10px;
      background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f5 100%);
      border: 1px solid #e4e7ed;
      border-radius: 6px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      text-decoration: none;
      overflow: hidden;
      
      &:hover {
        background: linear-gradient(135deg, #e6f4ff 0%, #d4edff 100%);
        border-color: #409eff;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
        transform: translateY(-1px);
      }
      
      .link-icon {
        flex-shrink: 0;
        font-size: 14px;
        color: #409eff;
        margin-top: 2px;
      }
      
      .link-text {
        flex: 1;
        min-width: 0;
        color: #303133;
        font-size: 13px;
        font-weight: 400;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      &:visited .link-text {
        color: #606266;
      }
    }
  }
  
  .empty-placeholder {
    color: #909399;
    font-size: 13px;
    padding: 8px 0;
  }
}

// 图片预览组件样式
.image-preview-wrapper {
  position: relative;
  display: inline-block;
  width: 100%;
}

.image-preview-popup {
  position: fixed !important;
  z-index: 99999 !important;
  animation: previewFadeIn 0.2s ease-out;
  pointer-events: auto !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  margin-top: 5px; // 在链接和预览之间留出间隙，方便鼠标移动
  
  .preview-images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 8px;
    max-width: 400px;
    padding: 8px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 252, 255, 0.98) 100%);
    border: 1px solid rgba(64, 158, 255, 0.2);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 4px 8px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(12px);
    
      .preview-image-item {
        position: relative;
        width: 100px;
        height: 100px;
        border-radius: 8px;
        overflow: hidden;
        background: #f5f7fa;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
        
        &:hover {
          transform: scale(1.05);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
          
          .preview-click-hint {
            opacity: 1;
          }
        }
      
      .preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        transition: opacity 0.3s ease;
        
        &[style*="display: none"] {
          opacity: 0;
        }
      }
      
      .preview-click-hint {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
        color: white;
        padding: 4px 8px;
        font-size: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        opacity: 0;
        transition: opacity 0.2s ease;
        pointer-events: none;
        
        .el-icon {
          font-size: 12px;
        }
      }
      
      .preview-loading {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(245, 247, 250, 0.9);
        backdrop-filter: blur(4px);
        
        .loading-icon {
          font-size: 24px;
          color: #409eff;
          animation: rotate 1s linear infinite;
        }
      }
    }
  }
}

@keyframes previewFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 图片查看器样式
:deep(.image-viewer-dialog) {
  .el-dialog__body {
    padding: 0;
    background: rgba(0, 0, 0, 0.9);
  }
  
  .el-dialog__header {
    background: rgba(0, 0, 0, 0.8);
    padding: 12px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .image-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .image-viewer-title {
      color: white;
      font-size: 14px;
      font-weight: 500;
    }
    
    .close-btn {
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: white;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
}

.image-viewer-content {
  position: relative;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  
  .image-viewer-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 40px;
    
    .image-wrapper {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      max-width: 90%;
      max-height: 70vh;
      
      .viewer-image {
        max-width: 100%;
        max-height: 70vh;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      }
    }
    
    .nav-button {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: white;
      font-size: 20px;
      backdrop-filter: blur(10px);
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-50%) scale(1.1);
      }
      
      &.prev-button {
        left: 20px;
      }
      
      &.next-button {
        right: 20px;
      }
    }
  }
  
  .image-thumbnails {
    display: flex;
    gap: 12px;
    padding: 20px;
    justify-content: center;
    background: rgba(0, 0, 0, 0.6);
    overflow-x: auto;
    
    .thumbnail-item {
      width: 80px;
      height: 80px;
      border-radius: 6px;
      overflow: hidden;
      cursor: pointer;
      border: 2px solid transparent;
      transition: all 0.3s ease;
      flex-shrink: 0;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      &:hover {
        border-color: rgba(255, 255, 255, 0.5);
        transform: scale(1.1);
      }
      
      &.active {
        border-color: #409eff;
        box-shadow: 0 0 12px rgba(64, 158, 255, 0.6);
      }
    }
  }
}

</style>

<style lang="scss">
// 全局样式：设置所有 el-tooltip 的最大宽度（tooltip是动态插入到body的，需要全局样式）
.el-tooltip__popper {
  max-width: 100px !important;
  word-break: break-word !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  white-space: normal !important;
  padding: 10px 14px !important;
  font-size: 13px !important;
  line-height: 1.6 !important;
}

// 自定义表格 tooltip 样式（最大宽度 200px，黑色背景）
.custom-table-tooltip {
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

// 针对表格列的 tooltip 样式（表格列的 tooltip 通常需要更宽以显示完整内容）
// 注意：由于 tooltip 是动态插入到 body 的，无法直接通过 .el-table 选择器定位
// 但可以通过更具体的选择器或使用 popper-class 属性
// .el-tooltip__popper[data-popper-placement] {
//   // 所有表格相关的 tooltip 可以设置更宽的宽度
//   max-width: 400px !important;
//   min-width: 150px !important;
// }

// 话题弹窗样式（使用 append-to-body，需要全局样式）
.topic-dialog {
  .el-dialog__body {
    padding: 20px;
  }
  
  .topic-dialog-content {
    .custom-topic-input {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      align-items: center;
      
      .custom-input {
        flex: 1;
      }
      
      .el-button {
        flex-shrink: 0;
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
  
  .el-dialog__footer {
    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 0;
    }
  }
}
</style>



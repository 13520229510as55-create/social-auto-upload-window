<template>
  <div class="mobile-imagetext-preview">
    <div class="phone-shell">
      <div class="phone-notch" />
      <div class="phone-screen">
        <div class="imagetext-scroll">
          <header class="imagetext-header">
            <p class="imagetext-source">{{ sourceLabel }}</p>
            <h1 class="imagetext-title">{{ title || '未命名图文' }}</h1>
            <div class="imagetext-meta">
              <span>{{ author }}</span>
              <span>{{ formattedDate }}</span>
            </div>
          </header>

          <section v-if="summary" class="imagetext-summary">
            <p>{{ summary }}</p>
          </section>

          <!-- 正文内容 -->
          <section v-if="content" class="imagetext-content">
            <MdNicePreview :content="content" />
          </section>

          <!-- 图片列表 -->
          <section v-if="images && images.length > 0" class="imagetext-images">
            <div 
              v-for="(image, index) in images" 
              :key="index" 
              class="image-item"
            >
              <img 
                :src="image" 
                :alt="`图片 ${index + 1}`"
                @error="handleImageError"
                @load="handleImageLoad"
              />
              <div v-if="images.length > 1" class="image-index">
                {{ index + 1 }} / {{ images.length }}
              </div>
            </div>
          </section>

          <!-- 如果没有图片也没有内容，显示提示 -->
          <section v-if="!content && (!images || images.length === 0)" class="empty-state">
            <p>暂无内容</p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MdNicePreview from '@/components/MdNicePreview.vue'

const props = defineProps({
  /**
   * @description 图文标题
   */
  title: {
    type: String,
    default: ''
  },
  /**
   * @description 图文摘要
   */
  summary: {
    type: String,
    default: ''
  },
  /**
   * @description 正文内容（Markdown格式）
   */
  content: {
    type: String,
    default: ''
  },
  /**
   * @description 图片列表（URL数组）
   */
  images: {
    type: Array,
    default: () => []
  },
  /**
   * @description 作者
   */
  author: {
    type: String,
    default: 'AI创作助手'
  },
  /**
   * @description 创建时间
   */
  createdAt: {
    type: String,
    default: ''
  },
  /**
   * @description 来源标签
   */
  sourceLabel: {
    type: String,
    default: '图文内容'
  }
})

const formattedDate = computed(() => {
  if (!props.createdAt) return '刚刚'
  const date = new Date(props.createdAt)
  if (Number.isNaN(date.getTime())) return props.createdAt
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
})

const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  event.target.style.display = 'none'
}

const handleImageLoad = (event) => {
  event.target.style.opacity = '1'
}
</script>

<style scoped lang="scss">
.mobile-imagetext-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
}

.phone-shell {
  width: 360px;
  max-width: 100%;
  background: linear-gradient(160deg, #f1f5f9, #cbd5f5);
  border-radius: 26px;
  padding: 18px 12px;
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.phone-notch {
  width: 120px;
  height: 16px;
  background: #0f172a;
  border-radius: 0 0 12px 12px;
  margin: 0 auto 12px;
}

.phone-screen {
  background: #f9fafb;
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.imagetext-scroll {
  height: 600px;
  overflow-y: auto;
  padding: 20px 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  scrollbar-width: thin;
  scrollbar-color: #cbd5f5 transparent;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #cbd5f5;
    border-radius: 999px;
  }
}

.imagetext-header {
  text-align: left;
  margin-bottom: 18px;

  .imagetext-source {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 4px;
  }

  .imagetext-title {
    font-size: 20px;
    margin: 8px 0;
    color: #111827;
    line-height: 1.4;
    font-weight: 600;
  }

  .imagetext-meta {
    font-size: 12px;
    color: #94a3b8;
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }
}

.imagetext-summary {
  background: rgba(99, 102, 241, 0.08);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;

  p {
    margin: 0;
    color: #4c1d95;
    font-size: 13px;
    line-height: 1.6;
  }
}

.imagetext-content {
  margin-bottom: 16px;
  line-height: 1.8;
  color: #334155;
  font-size: 15px;
}

.imagetext-images {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;

  .image-item {
    position: relative;
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    background: #f1f5f9;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);

    img {
      width: 100%;
      height: auto;
      display: block;
      opacity: 0;
      transition: opacity 0.3s ease;
      object-fit: cover;
    }

    .image-index {
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: rgba(0, 0, 0, 0.6);
      color: white;
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 500;
    }
  }
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
  font-size: 14px;
}
</style>


<template>
  <div class="mobile-article-preview">
    <div class="phone-shell">
      <div class="phone-notch" />
      <div class="phone-screen">
        <div class="article-scroll">
          <header class="article-header">
            <p class="article-source">公众号 · {{ sourceLabel }}</p>
            <h1 class="article-title">{{ title || '未命名文章' }}</h1>
            <div class="article-meta">
              <span>{{ author }}</span>
              <span>{{ formattedDate }}</span>
            </div>
          </header>

          <section v-if="summary" class="article-summary">
            <p>{{ summary }}</p>
          </section>

          <section class="article-cover" v-if="coverUrl">
            <img :src="coverUrl" alt="封面图" />
          </section>

          <MdNicePreview :content="content" />
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
   * @description 文章标题
   */
  title: {
    type: String,
    default: ''
  },
  /**
   * @description 文章摘要
   */
  summary: {
    type: String,
    default: ''
  },
  /**
   * @description 正文 Markdown 内容
   */
  content: {
    type: String,
    default: ''
  },
  /**
   * @description 来源或作者
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
   * @description 封面图链接
   */
  coverUrl: {
    type: String,
    default: ''
  },
  /**
   * @description 来源标签
   */
  sourceLabel: {
    type: String,
    default: '原创'
  }
})

const formattedDate = computed(() => {
  if (!props.createdAt) return '刚刚'
  const date = new Date(props.createdAt)
  if (Number.isNaN(date.getTime())) return props.createdAt
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
})
</script>

<style scoped lang="scss">
.mobile-article-preview {
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

.article-scroll {
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

.article-header {
  text-align: left;
  margin-bottom: 18px;

  .article-source {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 4px;
  }

  .article-title {
    font-size: 20px;
    margin: 8px 0;
    color: #111827;
    line-height: 1.4;
  }

  .article-meta {
    font-size: 12px;
    color: #94a3b8;
    display: flex;
    gap: 8px;
  }
}

.article-summary {
  background: rgba(99, 102, 241, 0.08);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;

  p {
    margin: 0;
    color: #4c1d95;
    font-size: 13px;
  }
}

.article-cover {
  margin-bottom: 16px;

  img {
    width: 100%;
    border-radius: 12px;
    object-fit: cover;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.15);
  }
}
</style>


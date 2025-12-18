<template>
  <div class="mdnice-preview" v-html="renderedHtml" />
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import { escapeHtml } from 'markdown-it/lib/common/utils'

import '@/styles/mdnice.scss'
import 'highlight.js/styles/github.css'

const props = defineProps({
  /**
   * @description Markdown 正文内容
   */
  content: {
    type: String,
    default: ''
  }
})

/**
 * @returns {MarkdownIt} Markdown 解析器实例
 */
const createMarkdownParser = () =>
  new MarkdownIt({
    html: false,
    linkify: true,
    typographer: true,
    highlight(str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang }).value}</code></pre>`
      }
      return `<pre class="hljs"><code>${escapeHtml(str)}</code></pre>`
    }
  })

const mdParser = createMarkdownParser()

const renderedHtml = computed(() => {
  const raw = props.content?.trim()
  if (!raw) {
    return '<p class="mdnice-empty">暂无正文内容</p>'
  }

  const mightBeHtml = /<[^>]+>/.test(raw)
  if (mightBeHtml) {
    return DOMPurify.sanitize(raw)
  }

  const html = mdParser.render(raw)
  return DOMPurify.sanitize(html)
})
</script>


/**
 * Vue 项目中使用示例
 * 可以在 Vue 组件中直接使用这个函数
 */

// 方法1：作为工具函数导入
export function processProductionData(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return data;
    }

    // 分离 Type 为 "1" 的对象和其他对象
    const typeOneItems = data.filter(item => item.Type === "1" || item.Type === 1);
    const otherItems = data.filter(item => item.Type !== "1" && item.Type !== 1);

    // 收集所有 url
    const typeOneUrls = typeOneItems.map(item => item.url).filter(Boolean);
    const otherUrls = otherItems.map(item => item.url).filter(Boolean);

    // 为 Type 为 "1" 的对象添加 urls 字段（Type 为 "1" 的 url 排在第一位）
    typeOneItems.forEach(item => {
        item.urls = [...typeOneUrls, ...otherUrls];
    });

    // 返回：Type 为 "1" 的对象在前，其他对象在后
    return [...typeOneItems, ...otherItems];
}

// 方法2：在 Vue 组件中使用
/*
<template>
  <div>
    <div v-for="item in processedData" :key="item.title">
      <h3>{{ item.title }}</h3>
      <div v-if="item.urls">
        <img v-for="(url, index) in item.urls" :key="index" :src="url" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { processProductionData } from '@/utils/processProductionData'

const rawData = ref([
  // 你的数据
])

const processedData = computed(() => {
  return processProductionData(rawData.value)
})
</script>
*/

// 方法3：在 Vue 3 Composition API 中使用
/*
import { processProductionData } from '@/utils/processProductionData'

const handleData = (data) => {
  return processProductionData(data)
}
*/



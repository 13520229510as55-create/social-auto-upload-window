/**
 * 从 JSON 字符串中提取数组
 * @param {string} jsonString - 包含 JSON 数组的字符串
 * @returns {Array} 解析后的数组
 */
function extractArrayFromJson(jsonString) {
  try {
    // 如果字符串包含代码块标记，先清理
    let cleanedString = jsonString.trim();
    
    // 移除可能的代码块标记（```json 和 ```）
    cleanedString = cleanedString.replace(/^```json\s*/i, '');
    cleanedString = cleanedString.replace(/\s*```$/g, '');
    cleanedString = cleanedString.trim();
    
    // 解析 JSON 字符串
    const parsedArray = JSON.parse(cleanedString);
    
    // 验证是否为数组
    if (!Array.isArray(parsedArray)) {
      throw new Error('解析结果不是数组');
    }
    
    return parsedArray;
  } catch (error) {
    console.error('解析 JSON 失败:', error);
    throw error;
  }
}

// 使用示例
const jsonString = `\`\`\`json
[
	{"bbox_2d": [164, 78, 395, 180], "label": "户型图"},
	{"bbox_2d": [164, 258, 370, 336], "label": "户型图"}
]
\`\`\``;

// 提取数组
const result = extractArrayFromJson(jsonString);
console.log('提取的数组:', result);
console.log('数组长度:', result.length);

// 访问数组元素
result.forEach((item, index) => {
  console.log(`元素 ${index}:`, item);
  console.log(`  bbox_2d:`, item.bbox_2d);
  console.log(`  label:`, item.label);
});

// 导出函数（如果使用模块系统）
// export { extractArrayFromJson };


/**
 * 处理制作数据数组（简洁版）
 * 1. 将 Type 为 "1" 的对象放到数组第0个位置
 * 2. 为 Type 为 "1" 的对象添加 urls 字段，包含所有对象的 url，且 Type 为 "1" 的 url 排在第一位
 */
function processProductionData(data) {
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

// 使用示例
// const result = processProductionData(yourDataArray);

// 导出（根据环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = processProductionData;
}
if (typeof window !== 'undefined') {
    window.processProductionData = processProductionData;
}



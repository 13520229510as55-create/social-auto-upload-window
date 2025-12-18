/**
 * 处理制作数据数组
 * 1. 将 Type 为 "1" 的对象放到数组第0个位置
 * 2. 为 Type 为 "1" 的对象添加 urls 字段，包含所有对象的 url，且 Type 为 "1" 的 url 排在第一位
 * 
 * @param {Array} data - 原始数据数组
 * @returns {Array} 处理后的数组
 */
function processProductionData(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return data;
    }

    // 1. 分离 Type 为 "1" 的对象和其他对象
    const typeOneItems = [];
    const otherItems = [];

    data.forEach(item => {
        if (item.Type === "1" || item.Type === 1) {
            typeOneItems.push(item);
        } else {
            otherItems.push(item);
        }
    });

    // 2. 收集所有对象的 url（过滤掉空值）
    const allUrls = data
        .map(item => item.url)
        .filter(url => url != null && url !== '');

    // 3. 分离 Type 为 "1" 的 url 和其他 url
    const typeOneUrls = typeOneItems
        .map(item => item.url)
        .filter(url => url != null && url !== '');
    
    const otherUrls = otherItems
        .map(item => item.url)
        .filter(url => url != null && url !== '');

    // 4. 为 Type 为 "1" 的对象添加 urls 字段（Type 为 "1" 的 url 排在第一位）
    typeOneItems.forEach(item => {
        item.urls = [...typeOneUrls, ...otherUrls];
    });

    // 5. 重新组合数组：Type 为 "1" 的对象在前，其他对象在后
    return [...typeOneItems, ...otherItems];
}

// 示例数据
const sampleData = [
    {
        "url": "http://150.107.38.113:3000/images/26dd8622b5f0aeaf9e2a8446eb26ac6e.png",
        "content": "🔥Vue 3 生态爆发！12款神仙工具让开发效率翻倍💪\n\n最近发现Vue生态圈真的越来越强大了！从构建工具到动效组件，各种神器层出不穷，今天给大家分享12款超实用的Vue新玩具～\n\n🚀 性能加速组\nVite+：比Webpack快40倍的构建神器\nRolldown：Vite的未来引擎，比Rollup快30倍\nOxfmt：代码格式化闪电侠，比Prettier快45倍\n\n这些Rust驱动的工具真的让构建速度起飞！大型项目秒级完成检查，再也不用等半天了\n\n🎨 视觉交互神器\nVue Bits：60+复制即用的动画组件库\nTresJS：像写HTML一样玩转3D渲染\nVue Data UI：数据可视化新选择\nNativeScript-Vue：用Vue开发原生APP\n\n做酷炫UI变得超级简单，复制粘贴就能用，再也不用自己写复杂动画了\n\n🔧 开发体验升级\nColada：智能数据获取，自动处理缓存\nVue-Official：可视化响应式依赖\nNode Modules Inspector：依赖关系一目了然\nVue-Plugins-Collection：精选插件集合\n\n这些工具让调试变得超直观，再也不用猜为什么数据变了\n\n💡 使用小贴士\n追求构建速度：关注Rolldown和Oxfmt\n快速出图：Vue Bits和TresJS是首选\n数据请求：Colada帮你搞定\n\nVue生态正在从\"能用\"到\"好用\"再到\"极致性能\"蜕变，这些工具让开发者能更专注于业务价值创造！\n\n✨ 记得点赞收藏，评论区分享你用过最香的Vue工具～\n#Vue3 #前端开发 #程序员必备 #开发工具推荐",
        "desc": "一个现代简约风格的科技感配图，展示Vue 3开发工具生态系统的概念图，包含代码编辑器界面、性能图表、3D渲染效果和工具图标，整体采用蓝色和橙色科技色调，体现高效开发的理念",
        "sentences": "Vue 3\n生态爆发\n开发效率\n翻倍神器",
        "title": "🔥Vue 3神仙工具合集",
        "Type": "1"
    },
    {
        "content": "哈喽，大家好，我是前端小仙女👩‍💻\n给大家分享12款Vue 3超实用开发工具，效率翻倍不是梦💪\n\n🔥Vue 3生态全面升级！从构建工具到动效库，这些新玩具让开发体验爽到飞起～\n\n💡性能党必看：\nVite+：比Webpack快40倍的全能工具链\nRolldown：Vite的未来引擎，速度碾压Rollup\nOxfmt：代码格式化神器，性能超Prettier 45倍\n\n🎨视觉控福音：\nVue Bits：60+复制即用动效组件\nTresJS：像写HTML一样玩3D渲染\nVue Data UI：高颜值数据可视化\n\n🚀还有更多实用工具：\nColada：智能数据获取层\nVue-Official：可视化调试工具\n\n这些工具让Vue开发从\"能用\"到\"好用\"，再到\"极致性能\"的蜕变！\n\n💖喜欢就点赞收藏吧～评论区告诉我你最想尝试哪款工具？",
        "desc": "一个现代简约的前端开发工作台，桌面上摆放着笔记本电脑，屏幕上显示着Vue 3代码和炫酷的3D动画效果，周围散落着各种开发工具图标，整体色调以蓝色和橙色为主，充满科技感和活力",
        "keywords": "Vue development tools programming frontend",
        "sentences": "Vue 3\n开发神器\n效率翻倍\n复制即用\n极致性能",
        "title": "Vue 3开发神器合集💻效率翻倍",
        "Type": "0",
        "url": "https://mmbiz.qpic.cn/mmbiz_png/jMJpgEM73PianAUaibwjbql2Jf3OtLaYIHtG06E1cRdfpt4JQJrUpzeHeDcHqhbZOUYBfNlqp5LzBfFZgmjvZu4A/640.png"
    }
];

// 测试
console.log("原始数据：");
console.log(JSON.stringify(sampleData, null, 2));

const processedData = processProductionData(sampleData);

console.log("\n处理后的数据：");
console.log(JSON.stringify(processedData, null, 2));

// 验证结果
console.log("\n验证：");
console.log("第一个对象的 Type:", processedData[0].Type);
console.log("第一个对象的 urls:", processedData[0].urls);

// 导出函数（如果是在模块环境中使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = processProductionData;
}



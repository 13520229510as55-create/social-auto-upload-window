# -*- coding: utf-8 -*-
"""
简单的API测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入"""
    print("=" * 50)
    print("测试模块导入")
    print("=" * 50)
    
    try:
        import config
        print("✓ config 模块导入成功")
    except Exception as e:
        print(f"✗ config 模块导入失败: {e}")
        return False
    
    try:
        from main import CrawlerFactory
        print("✓ CrawlerFactory 导入成功")
    except Exception as e:
        print(f"✗ CrawlerFactory 导入失败: {e}")
        return False
    
    try:
        from cmd_arg.arg import PlatformEnum
        print("✓ PlatformEnum 导入成功")
    except Exception as e:
        print(f"✗ PlatformEnum 导入失败: {e}")
        return False
    
    return True

def test_crawler_factory():
    """测试爬虫工厂"""
    print("\n" + "=" * 50)
    print("测试爬虫工厂")
    print("=" * 50)
    
    try:
        from main import CrawlerFactory
        
        platforms = ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]
        for platform in platforms:
            try:
                crawler = CrawlerFactory.create_crawler(platform)
                print(f"✓ {platform} 爬虫创建成功: {type(crawler).__name__}")
            except Exception as e:
                print(f"✗ {platform} 爬虫创建失败: {e}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n" + "=" * 50)
    print("测试配置模块")
    print("=" * 50)
    
    try:
        import config
        
        print(f"✓ PLATFORM: {getattr(config, 'PLATFORM', 'N/A')}")
        print(f"✓ KEYWORDS: {getattr(config, 'KEYWORDS', 'N/A')}")
        print(f"✓ LOGIN_TYPE: {getattr(config, 'LOGIN_TYPE', 'N/A')}")
        print(f"✓ CRAWLER_TYPE: {getattr(config, 'CRAWLER_TYPE', 'N/A')}")
        print(f"✓ SAVE_DATA_OPTION: {getattr(config, 'SAVE_DATA_OPTION', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False

def test_api_structure():
    """测试API结构"""
    print("\n" + "=" * 50)
    print("测试API结构")
    print("=" * 50)
    
    try:
        # 测试导入admin_api的main
        sys.path.insert(0, str(Path(__file__).parent))
        from main import app
        
        # 获取所有路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods) if route.methods else ['GET']
                routes.append((methods, route.path))
        
        print(f"✓ API应用创建成功，共 {len(routes)} 个路由")
        print("\n路由列表:")
        for methods, path in routes[:10]:  # 只显示前10个
            print(f"  {', '.join(methods):<10} {path}")
        
        return True
    except Exception as e:
        print(f"✗ API结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("MediaCrawler Admin API 测试")
    print("=" * 50 + "\n")
    
    results = []
    
    results.append(("模块导入", test_imports()))
    results.append(("爬虫工厂", test_crawler_factory()))
    results.append(("配置模块", test_config()))
    results.append(("API结构", test_api_structure()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20} {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败，请检查上述错误信息")
    print("=" * 50)


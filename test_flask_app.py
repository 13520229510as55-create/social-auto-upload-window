#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Flask 应用和 getAccounts 路由
"""
import sys

# 设置UTF-8编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=== 测试 Flask 应用 ===\n")

try:
    print("1. 导入 sau_backend...")
    import sau_backend
    print("   ✅ 导入成功")
    
    print("\n2. 获取 Flask app...")
    app = sau_backend.app
    print("   ✅ app 对象获取成功")
    
    print("\n3. 列出所有路由...")
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"   {rule.endpoint}: {rule.rule} {list(rule.methods)}")
    
    # 查找 getAccounts 路由
    getAccounts_route = [r for r in routes if 'getAccounts' in r or '/getAccounts' in r]
    
    if getAccounts_route:
        print(f"   ✅ 找到 getAccounts 路由:")
        for r in getAccounts_route:
            print(f"      {r}")
    else:
        print("   ❌ 未找到 getAccounts 路由")
        print("\n   所有路由:")
        for r in sorted(routes):
            print(r)
    
    print("\n4. 测试 getAccounts 函数...")
    with app.test_client() as client:
        response = client.get('/getAccounts')
        print(f"   状态码: {response.status_code}")
        print(f"   Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            print("   ✅ 响应正常")
            import json
            data = json.loads(response.data)
            print(f"   返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 响应异常")
            print(f"   响应内容: {response.data.decode('utf-8')[:500]}")
    
    print("\n✅ 测试完成")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()


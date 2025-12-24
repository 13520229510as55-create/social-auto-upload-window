#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 getAccounts 函数，诊断 500 错误
"""
import sys
import sqlite3
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from conf import BASE_DIR
    print(f"✅ 导入 conf 成功")
    print(f"   BASE_DIR: {BASE_DIR}")
except Exception as e:
    print(f"❌ 导入 conf 失败: {e}")
    BASE_DIR = Path(__file__).parent.resolve()
    print(f"   使用默认 BASE_DIR: {BASE_DIR}")

print("\n=== 测试数据库操作 ===")

try:
    # 确保数据库目录存在
    db_dir = Path(BASE_DIR / "db")
    print(f"数据库目录: {db_dir}")
    
    db_dir.mkdir(parents=True, exist_ok=True)
    print("✅ 数据库目录已创建/已存在")
    
    db_path = db_dir / "database.db"
    print(f"数据库路径: {db_path}")
    
    # 连接数据库
    with sqlite3.connect(str(db_path), timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 检查表是否存在
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_info'
        ''')
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("⚠️ user_info 表不存在，正在创建...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type INTEGER NOT NULL,
                    filePath TEXT NOT NULL,
                    userName TEXT NOT NULL,
                    status INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            print("✅ user_info 表创建成功")
        else:
            print("✅ user_info 表已存在")
        
        # 查询数据
        cursor.execute('SELECT * FROM user_info')
        rows = cursor.fetchall()
        rows_list = [dict(row) for row in rows]
        
        print(f"✅ 查询成功，共 {len(rows_list)} 条记录")
        
        if rows_list:
            print("\n数据内容:")
            for row in rows_list:
                print(f"  - {row}")
        else:
            print("  (表为空)")
        
        print("\n✅ 所有测试通过！getAccounts 函数应该可以正常工作。")
        
except sqlite3.Error as e:
    print(f"❌ 数据库错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 未知错误: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")


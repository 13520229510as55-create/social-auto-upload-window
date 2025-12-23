# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import sqlite3
import threading
import time
import uuid
import requests
from pathlib import Path
from queue import Queue
from datetime import datetime
from flask_cors import CORS
from myUtils.auth import check_cookie
from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from conf import BASE_DIR

# Windows 系统设置 UTF-8 编码输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 不支持 reconfigure
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
try:
    from conf import HTTP_PROXY, HTTPS_PROXY
except ImportError:
    # 兼容旧版本 conf.py（没有代理配置）
    HTTP_PROXY = ''
    HTTPS_PROXY = ''
from myUtils.login import get_tencent_cookie, douyin_cookie_gen, get_ks_cookie, xiaohongshu_cookie_gen, bilibili_cookie_gen
from myUtils.postVideo import post_video_tencent, post_video_DouYin, post_video_ks, post_video_xhs, post_image_text_xhs
from urllib.parse import urlparse
import shutil

# 获取中国时区的当前时间（UTC+8）
def get_china_time():
    """获取中国时区的当前时间字符串（格式：YYYY-MM-DD HH:MM:SS）"""
    # 获取UTC时间，然后加上8小时得到中国时间
    from datetime import timedelta
    utc_now = datetime.utcnow()
    china_time = utc_now + timedelta(hours=8)
    return china_time.strftime('%Y-%m-%d %H:%M:%S')

active_queues = {}
# 保存登录过程中的浏览器上下文（用于手动确认登录）
active_browser_contexts = {}  # {account_id: {'browser': browser, 'context': context, 'page': page, 'account_name': name}}
app = Flask(__name__)

#允许所有来源跨域访问
CORS(app)

# 注册 MediaCrawler 爬虫管理蓝图
# 如果使用 FastAPI 处理爬虫管理，则不注册 Flask 蓝图
if not os.getenv('USE_FASTAPI_FOR_CRAWLER'):
    try:
        from crawler_api import crawler_bp
        app.register_blueprint(crawler_bp)
        print("✓ MediaCrawler 爬虫管理蓝图已注册（Flask 模式）")
    except ImportError as e:
        print(f"⚠️ MediaCrawler 爬虫管理蓝图注册失败: {e}")
    except Exception as e:
        print(f"⚠️ MediaCrawler 爬虫管理蓝图注册出错: {e}")
else:
    print("ℹ️ 爬虫管理使用 FastAPI（与 MediaCrawler 保持一致），跳过 Flask 蓝图注册")

# 启动 Cookie 自动刷新定时任务（在应用初始化时启动）
def start_cookie_refresh_scheduler():
    """
    启动 Cookie 自动刷新定时任务
    每 2 小时自动刷新一次所有账号的 cookie
    """
    try:
        import schedule
        from myUtils.cookie_refresh import run_cookie_refresh_task
        
        # 每 2 小时执行一次
        schedule.every(2).hours.do(run_cookie_refresh_task)
        
        print(f"[INFO] [{get_china_time()}] Cookie 自动刷新定时任务已启动（每 2 小时执行一次）", flush=True)
        
        def run_scheduler():
            """在后台线程中运行定时任务"""
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        
        # 启动后台线程
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print(f"[INFO] Cookie 刷新定时任务线程已启动", flush=True)
        
    except ImportError as e:
        # 模块不存在时，静默跳过（可选功能）
        print(f"[WARNING] Cookie 刷新模块未找到，跳过定时任务: {str(e)}", flush=True)
    except Exception as e:
        print(f"[WARNING] 启动 Cookie 刷新定时任务失败: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()

# 在应用初始化时启动定时任务
start_cookie_refresh_scheduler()

# 限制上传文件大小为160MB
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024

# 获取当前目录（假设 index.html 和 assets 在这里）
current_dir = os.path.dirname(os.path.abspath(__file__))

# 处理所有静态资源请求（未来打包用）
@app.route('/assets/<filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(current_dir, 'assets'), filename)

# 处理 favicon.ico 静态资源（未来打包用）
@app.route('/favicon.ico')
def favicon(filename):
    return send_from_directory(os.path.join(current_dir, 'assets'), 'favicon.ico')

# （未来打包用）
@app.route('/')
def index():  # put application's code here
    return send_from_directory(current_dir, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            "code": 200,
            "data": None,
            "msg": "No file part in the request"
        }), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "code": 200,
            "data": None,
            "msg": "No selected file"
        }), 400
    try:
        # 保存文件到指定位置
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{file.filename}")
        file.save(filepath)
        return jsonify({"code":200,"msg": "File uploaded successfully", "data": f"{uuid_v1}_{file.filename}"}), 200
    except Exception as e:
        return jsonify({"code":200,"msg": str(e),"data":None}), 500

@app.route('/getFile', methods=['GET'])
def get_file():
    # 获取 filename 参数
    filename = request.args.get('filename')

    if not filename:
        return {"error": "filename is required"}, 400

    # 防止路径穿越攻击
    if '..' in filename or filename.startswith('/'):
        return {"error": "Invalid filename"}, 400

    # 拼接完整路径
    file_path = str(Path(BASE_DIR / "videoFile"))

    # 返回文件
    return send_from_directory(file_path,filename)


@app.route('/uploadSave', methods=['POST'])
def upload_save():
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No file part in the request"
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No selected file"
        }), 400

    # 获取表单中的自定义文件名（可选）
    custom_filename = request.form.get('filename', None)
    if custom_filename:
        filename = custom_filename + "." + file.filename.split('.')[-1]
    else:
        filename = file.filename

    try:
        # 生成 UUID v1
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")

        # 构造文件名和路径
        final_filename = f"{uuid_v1}_{filename}"
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{filename}")

        # 保存文件
        file.save(filepath)

        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            # 确保表中有 source 和 uri 字段
            try:
                cursor.execute("SELECT source FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN source TEXT DEFAULT '本地上传'")
            try:
                cursor.execute("SELECT uri FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN uri TEXT")
            
            cursor.execute('''
                                INSERT INTO file_records (filename, filesize, file_path, source)
            VALUES (?, ?, ?, ?)
                                ''', (filename, round(float(os.path.getsize(filepath)) / (1024 * 1024),2), final_filename, '本地上传'))
            conn.commit()
            print("✅ 上传文件已记录")

        return jsonify({
            "code": 200,
            "msg": "File uploaded and saved successfully",
            "data": {
                "filename": filename,
                "filepath": final_filename
            }
        }), 200

    except Exception as e:
        print(f"Upload failed: {e}")
        return jsonify({
            "code": 500,
            "msg": f"upload failed: {e}",
            "data": None
        }), 500

@app.route('/getFiles', methods=['GET'])
def get_all_files():
    """
    获取所有素材文件
    支持筛选参数: source (可选，如: '生成素材', '本地上传', '谷歌存储上传')
    """
    try:
        # 获取筛选参数（处理URL编码）
        source_filter = request.args.get('source', '').strip()
        if source_filter:
            # 如果参数是URL编码的，尝试解码
            try:
                import urllib.parse
                source_filter = urllib.parse.unquote(source_filter)
            except:
                pass
        
        # 使用 with 自动管理数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row  # 允许通过列名访问结果
            cursor = conn.cursor()

            # 确保表中有 source 和 uri 字段（先检查再查询）
            try:
                cursor.execute("SELECT source FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN source TEXT DEFAULT '本地上传'")
                conn.commit()
            try:
                cursor.execute("SELECT uri FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN uri TEXT")
                conn.commit()
            
            # 根据筛选条件查询
            if source_filter:
                cursor.execute("SELECT * FROM file_records WHERE source = ?", (source_filter,))
            else:
                cursor.execute("SELECT * FROM file_records")
            rows = cursor.fetchall()
            
            # 将结果转为字典列表，并提取UUID
            data = []
            for row in rows:
                row_dict = dict(row)
                # 从 file_path 中提取 UUID (文件名的第一部分，下划线前)
                if row_dict.get('file_path'):
                    file_path_parts = row_dict['file_path'].split('_', 1)  # 只分割第一个下划线
                    if len(file_path_parts) > 0:
                        row_dict['uuid'] = file_path_parts[0]  # UUID 部分
                    else:
                        row_dict['uuid'] = ''
                else:
                    row_dict['uuid'] = ''
                # 确保 source 和 uri 字段存在，如果不存在则设置默认值
                if 'source' not in row_dict:
                    row_dict['source'] = '本地上传'
                if 'uri' not in row_dict:
                    row_dict['uri'] = None
                data.append(row_dict)

            return jsonify({
                "code": 200,
                "msg": "success",
                "data": data
            }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("get file failed!"),
            "data": None
        }), 500

@app.route('/saveGoogleStorageMaterial', methods=['POST'])
def save_google_storage_material():
    """保存谷歌存储上传的素材信息"""
    try:
        data = request.get_json(silent=True) or {}
        
        # 验证必填字段
        required_fields = ['filename', 'filesize']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                "code": 400,
                "msg": f"缺少必要字段: {', '.join(missing_fields)}",
                "data": None
            }), 400
        
        filename = data.get('filename')
        filesize = data.get('filesize')
        uri = data.get('uri')  # URI是可选的
        custom_filename = data.get('custom_filename')  # 可选的自定义文件名
        
        # 如果提供了自定义文件名，使用自定义文件名
        if custom_filename:
            final_filename = custom_filename
        else:
            final_filename = filename
        
        # 生成 UUID v1
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        
        # 构造 file_path（格式：uuid_filename）
        file_path = f"{uuid_v1}_{final_filename}"
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            # 确保表中有 source 和 uri 字段
            try:
                cursor.execute("SELECT source FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN source TEXT DEFAULT '本地上传'")
            try:
                cursor.execute("SELECT uri FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN uri TEXT")
            
            # 插入记录
            cursor.execute('''
                INSERT INTO file_records (filename, filesize, file_path, source, uri)
                VALUES (?, ?, ?, ?, ?)
            ''', (final_filename, filesize, file_path, '谷歌存储上传', uri))
            conn.commit()
            print("✅ 谷歌存储上传文件已记录")
        
        return jsonify({
            "code": 200,
            "msg": "Material saved successfully",
            "data": {
                "filename": final_filename,
                "filepath": file_path,
                "uuid": str(uuid_v1)
            }
        }), 200
        
    except Exception as e:
        print(f"Save Google Storage material failed: {e}")
        return jsonify({
            "code": 500,
            "msg": f"save failed: {str(e)}",
            "data": None
        }), 500

@app.route('/getGoogleFilePublicUrl', methods=['POST'])
def get_google_file_public_url():
    """获取谷歌存储文件的公开访问链接"""
    try:
        data = request.get_json(silent=True) or {}
        file_uri = data.get('uri')
        
        if not file_uri:
            return jsonify({
                "code": 400,
                "msg": "缺少必要参数: uri",
                "data": None
            }), 400
        
        # 从URI中提取文件ID
        # URI格式: https://generativelanguage.googleapis.com/v1beta/files/8kxw2l3kmzkh
        # 或者: files/8kxw2l3kmzkh
        file_id = None
        if '/files/' in file_uri:
            file_id = file_uri.split('/files/')[-1]
        elif file_uri.startswith('files/'):
            file_id = file_uri.replace('files/', '')
        
        if not file_id:
            return jsonify({
                "code": 400,
                "msg": "无法从URI中提取文件ID",
                "data": None
            }), 400
        
        # 使用API Key获取文件信息
        api_key = 'AIzaSyBWj4raKG-ayYkKOVP9eHSdpZO7oT7TuWo'
        file_info_url = f'https://generativelanguage.googleapis.com/v1beta/files/{file_id}?key={api_key}'
        
        try:
            response = requests.get(file_info_url, timeout=10)
            if response.status_code == 200:
                file_data = response.json()
                # 返回文件信息，包括可能的下载链接
                return jsonify({
                    "code": 200,
                    "msg": "success",
                    "data": {
                        "uri": file_uri,
                        "file_id": file_id,
                        "file_info": file_data,
                        # 注意：Google Generative AI API的文件需要通过API访问，没有直接的公开链接
                        # 如果需要公开链接，需要将文件上传到Google Cloud Storage并设置公开权限
                        "public_url": None,  # 需要通过其他方式获取
                        "api_access_url": file_uri  # API访问地址
                    }
                }), 200
            else:
                return jsonify({
                    "code": 500,
                    "msg": f"获取文件信息失败: {response.status_code}",
                    "data": None
                }), 500
        except Exception as e:
            return jsonify({
                "code": 500,
                "msg": f"请求文件信息失败: {str(e)}",
                "data": None
            }), 500
            
    except Exception as e:
        print(f"Get Google file public URL failed: {e}")
        return jsonify({
            "code": 500,
            "msg": f"处理失败: {str(e)}",
            "data": None
        }), 500

@app.route("/getAccounts", methods=['GET'])
def getAccounts():
    """快速获取所有账号信息，不进行cookie验证"""
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM user_info''')
            rows = cursor.fetchall()
            rows_list = [list(row) for row in rows]

            print("\n📋 当前数据表内容（快速获取）：")
            for row in rows:
                print(row)

            return jsonify(
                {
                    "code": 200,
                    "msg": None,
                    "data": rows_list
                }), 200
    except Exception as e:
        print(f"获取账号列表时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"获取账号列表失败: {str(e)}",
            "data": None
        }), 500


@app.route("/getValidAccounts",methods=['GET'])
def getValidAccounts():
    """获取有效账号列表（同步版本，避免Flask async问题）"""
    try:
        async def async_get_valid_accounts():
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM user_info''')
                rows = cursor.fetchall()
                rows_list = [list(row) for row in rows]
                print("\n📋 当前数据表内容：")
                for row in rows:
                    print(row)
                
                # ⚡ 优化：并发验证所有账号，大幅提升速度
                if rows_list:
                    print(f"\n🚀 开始并发验证 {len(rows_list)} 个账号...")
                    start_time = time.time()
                    
                    # 创建所有验证任务
                    check_tasks = [check_cookie(row[1], row[2]) for row in rows_list]
                    
                    # 并发执行所有验证任务
                    check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
                    
                    # 批量更新状态
                    for i, (row, result) in enumerate(zip(rows_list, check_results)):
                        # 处理异常情况
                        if isinstance(result, Exception):
                            print(f"⚠️ 账号 {row[1]} 验证异常: {result}")
                            flag = False
                        else:
                            flag = result
                        
                        if not flag:
                            row[4] = 0
                            cursor.execute('''
                            UPDATE user_info 
                            SET status = ? 
                            WHERE id = ?
                            ''', (0, row[0]))
                        else:
                            row[4] = 1
                            cursor.execute('''
                            UPDATE user_info 
                            SET status = ? 
                            WHERE id = ?
                            ''', (1, row[0]))
                    
                    conn.commit()
                    
                    elapsed_time = time.time() - start_time
                    print(f"✅ 并发验证完成，耗时 {elapsed_time:.2f} 秒")
                    valid_count = sum(1 for r in check_results if not isinstance(r, Exception) and r)
                    print(f"📊 验证结果：{valid_count} 个有效，{len(check_results) - valid_count} 个无效")
                
                # 重新查询更新后的数据
                cursor.execute('SELECT * FROM user_info')
                updated_rows = cursor.fetchall()
                updated_rows_list = [list(row) for row in updated_rows]
                
                for row in updated_rows:
                    print(row)
                    
                return updated_rows_list
        
        # 在同步函数中运行异步函数
        result = asyncio.run(async_get_valid_accounts())
        return jsonify({
            "code": 200,
            "msg": None,
            "data": result
        }), 200
    
    except Exception as e:
        print(f"❌ 获取有效账号失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"获取有效账号失败: {str(e)}",
            "data": None
        }), 500

PRODUCTION_ARTICLE_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS production_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        desc TEXT,
        url TEXT,
        html TEXT,
        publish_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''

PRODUCTION_IMAGE_TEXT_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS production_image_text (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        media_ids TEXT NOT NULL,
        height INTEGER,
        width INTEGER,
        publish_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''

PRODUCTION_VIDEO_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS production_video (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        "desc" TEXT,
        keywords TEXT,
        video TEXT NOT NULL,
        publish_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''


def ensure_production_article_table(cursor: sqlite3.Cursor):
    """确保文章制作结果表存在"""
    # 先检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='production_articles'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        # 表不存在，直接创建新表
        cursor.execute(PRODUCTION_ARTICLE_TABLE_SQL)
    else:
        # 表已存在，检查并添加新字段
        # 检查并添加 publish_status 字段（如果不存在）
        try:
            cursor.execute("SELECT publish_status FROM production_articles LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE production_articles ADD COLUMN publish_status TEXT DEFAULT 'pending'")
        
        # 检查并添加新字段（如果不存在）
        new_fields = {
            'title': 'TEXT',
            'content': 'TEXT',
            'desc': 'TEXT',
            'url': 'TEXT',
            'html': 'TEXT'
        }
        for field_name, field_type in new_fields.items():
            try:
                cursor.execute(f"SELECT {field_name} FROM production_articles LIMIT 1")
            except sqlite3.OperationalError:
                # 字段不存在，添加字段
                cursor.execute(f"ALTER TABLE production_articles ADD COLUMN {field_name} {field_type}")
        
        # 兼容旧字段：如果新字段为空，尝试从旧字段迁移数据
        try:
            # 检查是否有旧字段
            cursor.execute("PRAGMA table_info(production_articles)")
            columns = [row[1] for row in cursor.fetchall()]
            has_old_fields = 'article_title' in columns
            
            if has_old_fields:
                # 迁移旧数据到新字段
                cursor.execute('''
                    UPDATE production_articles 
                    SET title = COALESCE(NULLIF(title, ''), article_title, ''),
                        content = COALESCE(NULLIF(content, ''), article_content, ''),
                        desc = COALESCE(NULLIF(desc, ''), article_desc, ''),
                        url = COALESCE(NULLIF(url, ''), article_media_url, '')
                    WHERE (title IS NULL OR title = '') AND article_title IS NOT NULL
                ''')
        except sqlite3.OperationalError as e:
            # 旧字段不存在或迁移失败，跳过
            print(f"数据迁移跳过: {e}")
            pass


def ensure_production_image_text_table(cursor: sqlite3.Cursor):
    """确保图文制作结果表存在"""
    cursor.execute(PRODUCTION_IMAGE_TEXT_TABLE_SQL)
    # 检查并添加 publish_status 字段（如果不存在）
    try:
        cursor.execute("SELECT publish_status FROM production_image_text LIMIT 1")
    except sqlite3.OperationalError:
        # 字段不存在，添加字段
        cursor.execute("ALTER TABLE production_image_text ADD COLUMN publish_status TEXT DEFAULT 'pending'")
    # 检查并添加 url 字段（如果不存在）
    try:
        cursor.execute("SELECT url FROM production_image_text LIMIT 1")
    except sqlite3.OperationalError:
        # 字段不存在，添加字段
        cursor.execute("ALTER TABLE production_image_text ADD COLUMN url TEXT")


def ensure_production_video_table(cursor: sqlite3.Cursor):
    """确保视频制作结果表存在"""
    cursor.execute(PRODUCTION_VIDEO_TABLE_SQL)
    # 检查并添加 publish_status 字段（如果不存在）
    try:
        cursor.execute("SELECT publish_status FROM production_video LIMIT 1")
    except sqlite3.OperationalError:
        # 字段不存在，添加字段
        cursor.execute("ALTER TABLE production_video ADD COLUMN publish_status TEXT DEFAULT 'pending'")
    # 检查并添加 material_url 字段（如果不存在）
    try:
        cursor.execute("SELECT material_url FROM production_video LIMIT 1")
    except sqlite3.OperationalError:
        # 字段不存在，添加字段
        cursor.execute("ALTER TABLE production_video ADD COLUMN material_url TEXT")
    # 检查并添加 content 字段（如果不存在，用于存储视频内容/文案）
    try:
        cursor.execute("SELECT content FROM production_video LIMIT 1")
    except sqlite3.OperationalError:
        # 字段不存在，添加字段
        cursor.execute("ALTER TABLE production_video ADD COLUMN content TEXT")


@app.route('/production/articles', methods=['POST'])
def save_production_article():
    """接收制作中心生成的文章内容
    入参：title, content, desc, url, html
    """
    data = request.get_json(silent=True) or {}

    required_fields = ['title', 'content']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "code": 400,
            "msg": f"缺少必要字段: {', '.join(missing_fields)}",
            "data": None
        }), 400

    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(production_articles)")
            columns = [row[1] for row in cursor.fetchall()]
            has_new_fields = 'title' in columns and 'content' in columns
            has_old_fields = 'article_title' in columns and 'article_content' in columns
            
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            desc = data.get('desc', '').strip()
            url = data.get('url', '').strip()
            html = data.get('html', '').strip()
            
            # 获取中国时区时间
            china_time = get_china_time()
            
            if has_new_fields and has_old_fields:
                # 同时更新新旧字段（兼容）
                try:
                    cursor.execute('''
                        INSERT INTO production_articles (
                            title,
                            content,
                            desc,
                            url,
                            html,
                            article_title,
                            article_content,
                            article_desc,
                            article_media_url,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        title, content, desc, url, html,
                        title, content, desc, url,  # 旧字段也填充相同值
                        china_time
                    ))
                except sqlite3.OperationalError as e:
                    # 如果旧字段不存在，回退到只使用新字段
                    print(f"尝试插入新旧字段失败（可能旧字段不存在），回退到只使用新字段: {e}")
                    cursor.execute('''
                        INSERT INTO production_articles (
                            title,
                            content,
                            desc,
                            url,
                            html,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (title, content, desc, url, html, china_time))
            elif has_new_fields:
                # 只使用新字段
                print(f"[save_production_article] 使用新字段插入，数据: title={title[:50] if title else 'None'}, content长度={len(content) if content else 0}, desc={desc[:50] if desc else 'None'}")
                cursor.execute('''
                    INSERT INTO production_articles (
                        title,
                        content,
                        desc,
                        url,
                        html,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, content, desc, url, html, china_time))
                print(f"[save_production_article] 插入语句执行成功")
            else:
                # 只使用旧字段（兼容）
                print(f"[save_production_article] 使用旧字段插入")
                cursor.execute('''
                    INSERT INTO production_articles (
                        article_title,
                        article_content,
                        article_desc,
                        article_media_url,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (title, content, desc, url, china_time))
            
            conn.commit()
            record_id = cursor.lastrowid
            print(f"[save_production_article] 提交成功，记录ID: {record_id}")
            
            # 验证插入是否成功
            cursor.execute('SELECT id, title FROM production_articles WHERE id = ?', (record_id,))
            verify_row = cursor.fetchone()
            if verify_row:
                print(f"[save_production_article] ✅ 验证成功，找到记录: ID={verify_row[0]}, title={verify_row[1][:50] if verify_row[1] else 'None'}")
            else:
                print(f"[save_production_article] ⚠️ 警告：插入后验证失败，未找到记录ID={record_id}")

        return jsonify({
            "code": 200,
            "msg": "文章制作结果已保存",
            "data": {
                "id": record_id
            }
        }), 200

    except Exception as e:
        print(f"保存文章制作结果失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"保存失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/video', methods=['POST'])
def save_production_video():
    """
    新增视频信息接口
    参数: title, desc, keywords, video
    """
    data = request.get_json(silent=True) or {}
    
    # 验证必填字段
    required_fields = ['title', 'video']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "code": 400,
            "msg": f"缺少必要字段: {', '.join(missing_fields)}",
            "data": None
        }), 400
    
    try:
        import json
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_video_table(cursor)
            
            # 处理 keywords：如果是数组，转换为 JSON 字符串；如果是字符串，直接使用
            keywords = data.get('keywords', '')
            if isinstance(keywords, list):
                keywords = json.dumps(keywords, ensure_ascii=False)
            elif keywords:
                keywords = str(keywords).strip()
            else:
                keywords = None
            
            # 获取中国时区时间
            china_time = get_china_time()
            
            cursor.execute('''
                INSERT INTO production_video (
                    title,
                    "desc",
                    keywords,
                    video,
                    material_url,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('title', '').strip(),
                data.get('desc', '').strip() if data.get('desc') else None,
                keywords,
                data.get('video', '').strip(),
                data.get('material_url', '').strip() if data.get('material_url') else None,
                china_time
            ))
            conn.commit()
            record_id = cursor.lastrowid
        
        return jsonify({
            "code": 200,
            "msg": "视频信息已保存",
            "data": {
                "id": record_id
            }
        }), 200
    
    except Exception as e:
        print(f"保存视频信息失败: {e}")
        return jsonify({
            "code": 500,
            "msg": f"保存失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/video-from-n8n', methods=['POST'])
def save_production_video_from_n8n():
    """
    从n8n调用，保存生成的视频到制作中心列表
    参数: title, content, desc, material_url (原始素材URL), url (生成素材URL)
    同时将生成的视频保存到素材库，标记为"生成素材"
    """
    data = request.get_json(silent=True) or {}
    
    # 验证必填字段
    required_fields = ['title', 'url']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "code": 400,
            "msg": f"缺少必要字段: {', '.join(missing_fields)}",
            "data": None
        }), 400
    
    try:
        import uuid
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_video_table(cursor)
            
            # 保存到制作中心
            material_url = data.get('material_url', '').strip() if data.get('material_url') else None
            generated_url = data.get('url', '').strip()  # 生成素材URL
            
            # 获取中国时区时间
            china_time = get_china_time()
            
            cursor.execute('''
                INSERT INTO production_video (
                    title,
                    content,
                    "desc",
                    video,
                    material_url,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('title', '').strip(),
                data.get('content', '').strip() if data.get('content') else None,
                data.get('desc', '').strip() if data.get('desc') else None,
                generated_url,  # url 对应 video 字段（生成内容链接）
                material_url,  # 原始素材URL
                china_time
            ))
            conn.commit()
            record_id = cursor.lastrowid
            
            # 将生成的视频保存到素材库（file_records表）
            # 确保表中有 source 和 uri 字段
            try:
                cursor.execute("SELECT source FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN source TEXT DEFAULT '本地上传'")
            try:
                cursor.execute("SELECT uri FROM file_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE file_records ADD COLUMN uri TEXT")
            
            # 从URL中提取文件名
            url_parts = generated_url.split('/')
            filename = url_parts[-1] if url_parts else f"generated_video_{record_id}.mp4"
            # 如果文件名包含查询参数，去掉
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # 生成UUID和file_path
            uuid_v1 = uuid.uuid1()
            file_path = f"{uuid_v1}_{filename}"
            
            # 插入到素材库，标记为"生成素材"
            cursor.execute('''
                INSERT INTO file_records (filename, filesize, file_path, source, uri)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                filename,
                0,  # 生成素材大小未知，设为0
                file_path,
                '生成素材',  # 标记为生成素材
                generated_url  # 保存完整URL到uri字段
            ))
            conn.commit()
            print(f"✅ 生成素材已保存到素材库: {filename}")
        
        return jsonify({
            "code": 200,
            "msg": "视频信息已保存",
            "data": {
                "id": record_id
            }
        }), 200
    
    except Exception as e:
        print(f"保存视频信息失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"保存失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/image-text', methods=['POST'])
def save_production_image_text():
    """
    新增图文信息接口
    参数: title, content, urls (URL数组)
    """
    import json as json_module  # 导入json模块用于日志
    data = request.get_json(silent=True) or {}
    
    # 📝 调试日志：记录接收到的完整数据
    print(f"\n[图文保存] 收到请求，完整数据: {json_module.dumps(data, ensure_ascii=False, indent=2)}")
    print(f"[图文保存] urls字段类型: {type(data.get('urls'))}")
    print(f"[图文保存] urls字段值: {data.get('urls')}")
    if isinstance(data.get('urls'), list):
        print(f"[图文保存] urls数组长度: {len(data.get('urls'))}")
        print(f"[图文保存] urls数组内容: {data.get('urls')}")
    
    # ⚠️ 重要：检查是否错误使用了 media_ids 字段（防止重复出现的问题）
    if 'media_ids' in data and 'urls' not in data:
        return jsonify({
            "code": 400,
            "msg": "错误：请使用 'urls' 字段而不是 'media_ids' 字段。接口期望参数：title, content, urls (URL数组)",
            "data": None
        }), 400
    
    # 验证必填字段
    required_fields = ['title', 'content', 'urls']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "code": 400,
            "msg": f"缺少必要字段: {', '.join(missing_fields)}。注意：请使用 'urls' 字段（数组），不是 'media_ids'",
            "data": None
        }), 400
    
    # 验证 urls 是否为数组
    urls = data.get('urls', [])
    if not isinstance(urls, list):
        return jsonify({
            "code": 400,
            "msg": "urls 必须是数组",
            "data": None
        }), 400
    
    # 过滤空值
    urls = [url.strip() for url in urls if url and url.strip()]
    if not urls:
        return jsonify({
            "code": 400,
            "msg": "urls 数组不能为空",
            "data": None
        }), 400
    
    try:
        import json
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_image_text_table(cursor)
            
            # 将 urls 数组转换为 JSON 字符串存储到 media_ids 字段（保持数据库兼容）
            media_ids_json = json.dumps(urls, ensure_ascii=False)
            print(f"[图文保存] 转换后的JSON字符串: {media_ids_json}")
            print(f"[图文保存] JSON字符串长度: {len(media_ids_json)}")
            
            # 将第一个 URL 存储到 url 字段（用于快速访问）
            first_url = urls[0] if urls else None
            print(f"[图文保存] 第一个URL: {first_url}")
            
            # 获取中国时区时间
            china_time = get_china_time()
            
            cursor.execute('''
                INSERT INTO production_image_text (
                    title,
                    content,
                    media_ids,
                    url,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('title', '').strip(),
                data.get('content', '').strip(),
                media_ids_json,
                first_url,
                china_time
            ))
            conn.commit()
            record_id = cursor.lastrowid
            print(f"[图文保存] ✅ 保存成功，记录ID: {record_id}")
            print(f"[图文保存] 保存的urls数量: {len(urls)}")
        
        return jsonify({
            "code": 200,
            "msg": "图文信息已保存",
            "data": {
                "id": record_id
            }
        }), 200
    
    except Exception as e:
        print(f"保存图文信息失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"保存失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/records', methods=['GET'])
def list_production_records():
    """
    获取制作中心产出的统一列表，可按 content_type 过滤
    支持 article、image-text 和 video 类型
    注意：已成功发布的记录（publish_status = 'success'）不会出现在制作中心列表中，
    它们只会在发布中心列表中显示
    """
    content_type = (request.args.get('content_type') or '').strip().lower()
    supported_types = {'', 'all', 'article', 'image-text', 'video'}

    if content_type and content_type not in supported_types:
        # 不支持的类型直接返回空数组，方便前端兼容
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": {
                "items": [],
                "total": 0
            }
        }), 200

    records = []

    try:
        import json
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            ensure_production_video_table(cursor)

            # 获取文章记录
            if not content_type or content_type in ('all', 'article'):
                # 检查表结构，优先使用新字段
                cursor.execute("PRAGMA table_info(production_articles)")
                columns = [row[1] for row in cursor.fetchall()]
                has_new_fields = 'title' in columns and 'content' in columns
                has_old_fields = 'article_title' in columns and 'article_content' in columns
                
                if has_new_fields and has_old_fields:
                    # 同时有新字段和旧字段，使用 COALESCE 兼容
                    cursor.execute('''
                        SELECT id,
                               COALESCE(NULLIF(title, ''), article_title, '') as title,
                               COALESCE(NULLIF(content, ''), article_content, '') as content,
                               COALESCE(NULLIF(desc, ''), article_desc, '') as desc,
                               COALESCE(NULLIF(url, ''), article_media_url, '') as url,
                               COALESCE(html, '') as html,
                               COALESCE(publish_status, 'pending') as publish_status,
                               created_at
                        FROM production_articles
                        WHERE COALESCE(publish_status, 'pending') != 'success'
                        ORDER BY created_at DESC, id DESC
                    ''')
                elif has_new_fields:
                    # 只有新字段
                    cursor.execute('''
                        SELECT id,
                               title,
                               content,
                               desc,
                               url,
                               COALESCE(html, '') as html,
                               COALESCE(publish_status, 'pending') as publish_status,
                               created_at
                        FROM production_articles
                        WHERE COALESCE(publish_status, 'pending') != 'success'
                        ORDER BY created_at DESC, id DESC
                    ''')
                else:
                    # 只有旧字段（兼容）
                    cursor.execute('''
                        SELECT id,
                               article_title as title,
                               article_content as content,
                               article_desc as desc,
                               article_media_url as url,
                               '' as html,
                               COALESCE(publish_status, 'pending') as publish_status,
                               created_at
                        FROM production_articles
                        WHERE COALESCE(publish_status, 'pending') != 'success'
                        ORDER BY created_at DESC, id DESC
                    ''')
                
                article_rows = cursor.fetchall()

                for row in article_rows:
                    records.append({
                        "id": row["id"],
                        "content_type": "article",
                        "title": row["title"] or "",
                        "content": row["content"] or "",
                        "desc": row["desc"] or "",
                        "url": row["url"] or "",
                        "html": row["html"] or "",
                        "summary": row["desc"] or "",  # 兼容字段
                        "publish_status": row["publish_status"] or "pending",
                        "created_at": row["created_at"]
                    })

            # 获取图文记录
            if not content_type or content_type in ('all', 'image-text'):
                cursor.execute('''
                    SELECT id,
                           title,
                           content,
                           media_ids,
                           height,
                           width,
                           url,
                           COALESCE(publish_status, 'pending') as publish_status,
                           created_at
                    FROM production_image_text
                    WHERE COALESCE(publish_status, 'pending') != 'success'
                    ORDER BY created_at DESC, id DESC
                ''')
                image_text_rows = cursor.fetchall()

                for row in image_text_rows:
                    # 解析 media_ids JSON 字符串为数组
                    try:
                        media_ids = json.loads(row["media_ids"]) if row["media_ids"] else []
                    except:
                        media_ids = []
                    
                    records.append({
                        "id": row["id"],
                        "content_type": "image-text",
                        "title": row["title"],
                        "summary": "",  # 图文类型没有摘要字段
                        "content": row["content"],
                        "media_ids": media_ids,
                        "height": row["height"],
                        "width": row["width"],
                        "url": row["url"],  # 添加 url 字段
                        "publish_status": row["publish_status"] or "pending",  # 发布状态
                        "created_at": row["created_at"]
                    })

            # 获取视频记录
            if not content_type or content_type in ('all', 'video'):
                cursor.execute('''
                    SELECT id,
                           title,
                           content,
                           "desc",
                           keywords,
                           video,
                           material_url,
                           COALESCE(publish_status, 'pending') as publish_status,
                           created_at
                    FROM production_video
                    WHERE COALESCE(publish_status, 'pending') != 'success'
                    ORDER BY created_at DESC, id DESC
                ''')
                video_rows = cursor.fetchall()

                for row in video_rows:
                    # 解析 keywords JSON 字符串为数组（如果是JSON格式）
                    keywords = row["keywords"] or ""
                    try:
                        keywords_list = json.loads(keywords) if keywords else []
                    except:
                        # 如果不是JSON格式，尝试按逗号分割
                        keywords_list = [k.strip() for k in keywords.split(',')] if keywords else []
                    
                    records.append({
                        "id": row["id"],
                        "content_type": "video",
                        "title": row["title"],
                        "summary": row["desc"] or "",  # 使用 desc 作为摘要
                        "content": row["content"] or "",  # 视频内容/文案
                        "keywords": keywords_list,  # 关键词列表
                        "video": row["video"],  # 视频URL或路径（生成内容链接）
                        "material_url": row["material_url"] or "",  # 素材网址
                        "publish_status": row["publish_status"] or "pending",  # 发布状态
                        "created_at": row["created_at"]
                    })

    except Exception as e:
        print(f"获取制作记录失败: {e}")
        return jsonify({
            "code": 500,
            "msg": f"获取制作记录失败: {str(e)}",
            "data": None
        }), 500

    # 按创建时间倒序排序（最新的在前）
    # 如果 created_at 为空，则按 id 倒序
    records.sort(key=lambda x: (x.get('created_at') or '', x.get('id', 0)), reverse=True)
    
    # 可按 content_type 过滤
    if content_type and content_type not in ('all', ''):
        filtered = [record for record in records if record["content_type"] == content_type]
    else:
        filtered = records

    return jsonify({
        "code": 200,
        "msg": "success",
        "data": {
            "items": filtered,
            "total": len(filtered)
        }
    }), 200


# 公众号监测号主表SQL
WECHAT_MONITOR_ACCOUNTS_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS wechat_monitor_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_id TEXT NOT NULL UNIQUE,
        account_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''

# 公众号爬取文章表SQL
WECHAT_HOTSPOT_ARTICLES_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS wechat_hotspot_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nick_name TEXT,
        biz TEXT,
        create_time TEXT,
        title TEXT,
        url TEXT UNIQUE,
        content TEXT,
        content_multi_text TEXT,
        pubtime TEXT,
        read_count INTEGER DEFAULT 0,
        zan INTEGER DEFAULT 0,
        looking INTEGER DEFAULT 0,
        share_num INTEGER DEFAULT 0,
        collect_num INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        summary TEXT,
        headline TEXT,
        keywords TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''

def ensure_wechat_monitor_accounts_table(cursor: sqlite3.Cursor):
    """确保公众号监测号主表存在"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wechat_monitor_accounts'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        cursor.execute(WECHAT_MONITOR_ACCOUNTS_TABLE_SQL)

def ensure_wechat_hotspot_articles_table(cursor: sqlite3.Cursor):
    """确保公众号爬取文章表存在"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wechat_hotspot_articles'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        cursor.execute(WECHAT_HOTSPOT_ARTICLES_TABLE_SQL)

@app.route('/hotspot/wechat/accounts', methods=['POST'])
def add_wechat_monitor_account():
    """添加公众号监测号主"""
    data = request.get_json(silent=True) or {}
    
    # 支持新参数 biz 和 name，也兼容旧的 media_id
    biz = data.get('biz', '').strip() or data.get('media_id', '').strip()
    name = data.get('name', '').strip() or data.get('account_name', '').strip()
    
    if not biz:
        return jsonify({
            "code": 400,
            "msg": "biz不能为空",
            "data": None
        }), 400
    
    if not name:
        return jsonify({
            "code": 400,
            "msg": "name不能为空",
            "data": None
        }), 400
    
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_wechat_monitor_accounts_table(cursor)
            
            # 检查是否已存在（根据biz/media_id）
            cursor.execute('SELECT id, account_name FROM wechat_monitor_accounts WHERE media_id = ?', (biz,))
            existing = cursor.fetchone()
            
            if existing:
                return jsonify({
                    "code": 400,
                    "msg": "该号主已存在",
                    "data": {
                        "id": existing[0],
                        "media_id": biz,
                        "account_name": existing[1]
                    }
                }), 400
            
            # 插入新记录
            china_time = get_china_time()
            cursor.execute('''
                INSERT INTO wechat_monitor_accounts (media_id, account_name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (biz, name, china_time, china_time))
            
            conn.commit()
            record_id = cursor.lastrowid
            
            return jsonify({
                "code": 200,
                "msg": "添加成功",
                "data": {
                    "id": record_id,
                    "media_id": biz,
                    "account_name": name
                }
            }), 200
            
    except sqlite3.IntegrityError:
        return jsonify({
            "code": 400,
            "msg": "该号主已存在",
            "data": None
        }), 400
    except Exception as e:
        print(f"添加公众号监测号主失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"添加失败: {str(e)}",
            "data": None
        }), 500

@app.route('/hotspot/wechat/accounts', methods=['GET'])
def list_wechat_monitor_accounts():
    """获取公众号监测号主列表"""
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            ensure_wechat_monitor_accounts_table(cursor)
            
            cursor.execute('''
                SELECT id, media_id, account_name, created_at, updated_at
                FROM wechat_monitor_accounts
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            accounts = []
            for row in rows:
                accounts.append({
                    "id": row["id"],
                    "media_id": row["media_id"],
                    "account_name": row["account_name"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return jsonify({
                "code": 200,
                "msg": "success",
                "data": {
                    "items": accounts,
                    "total": len(accounts)
                }
            }), 200
            
    except Exception as e:
        print(f"获取公众号监测号主列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"获取失败: {str(e)}",
            "data": None
        }), 500

@app.route('/hotspot/wechat/accounts/<int:account_id>', methods=['DELETE'])
def delete_wechat_monitor_account(account_id):
    """删除公众号监测号主"""
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_wechat_monitor_accounts_table(cursor)
            
            cursor.execute('DELETE FROM wechat_monitor_accounts WHERE id = ?', (account_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return jsonify({
                    "code": 200,
                    "msg": "删除成功",
                    "data": None
                }), 200
            else:
                return jsonify({
                    "code": 404,
                    "msg": "记录不存在",
                    "data": None
                }), 404
            
    except Exception as e:
        print(f"删除公众号监测号主失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"删除失败: {str(e)}",
            "data": None
        }), 500

@app.route('/hotspot/wechat/articles', methods=['POST'])
def save_wechat_hotspot_articles():
    """保存公众号爬取文章列表（从n8n调用）"""
    data = request.get_json(silent=True) or {}
    
    # 支持多种数据格式：
    # 1. rss_list 格式（新格式）
    # 2. articles 格式（旧格式）
    # 3. 直接是数组
    if 'rss_list' in data:
        # 新格式：从n8n RSS列表传入
        raw_articles = data.get('rss_list', [])
        articles = []
        
        for item in raw_articles:
            # 处理日期格式转换：ISO格式 -> 数据库格式
            pub_date = item.get('pubDate', '') or item.get('isoDate', '')
            pubtime_str = ''
            create_time_str = ''
            
            # 尝试转换ISO日期格式为数据库格式
            try:
                if pub_date:
                    # 处理ISO格式日期: 2025-12-02T07:01:05.000Z
                    if 'T' in pub_date:
                        # 替换Z为+00:00以便parse
                        date_str = pub_date.replace('Z', '+00:00')
                        # 如果已经是+00:00格式，直接解析
                        if '+' in date_str or '-' in date_str[-6:]:
                            dt = datetime.fromisoformat(date_str)
                        else:
                            # 尝试其他格式
                            dt = datetime.strptime(pub_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                            from datetime import timezone
                            dt = dt.replace(tzinfo=timezone.utc)
                        
                        # 转换为中国时区
                        from datetime import timezone, timedelta
                        china_tz = timezone(timedelta(hours=8))
                        dt_china = dt.astimezone(china_tz)
                        # 格式化为: 2025-12-02 15:01:05
                        pubtime_str = dt_china.strftime('%Y-%m-%d %H:%M:%S')
                        create_time_str = pubtime_str
                    else:
                        # 如果不是ISO格式，直接使用
                        pubtime_str = pub_date
                        create_time_str = pub_date
            except Exception as e:
                print(f"日期格式转换失败: {pub_date}, 错误: {e}")
                # 使用原始值或当前时间
                if pub_date:
                    pubtime_str = pub_date
                    create_time_str = pub_date
                else:
                    pubtime_str = get_china_time()
                    create_time_str = get_china_time()
            
            # 转换格式：从RSS格式转换为数据库格式
            article = {
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'pubtime': pubtime_str,
                'nick_name': item.get('name', ''),
                'content': '',  # RSS列表可能没有content
                'summary': item.get('title', ''),  # 使用title作为summary
                'biz': '',  # RSS列表可能没有biz
                'create_time': create_time_str,
                'read_count': 0,
                'zan': 0,
                'looking': 0,
                'share_num': 0,
                'collect_num': 0,
                'comment_count': 0,
            }
            # 如果有type字段，存储到keywords中（作为JSON数组）
            account_type = item.get('type', '')
            if account_type:
                # 将type信息存储到keywords字段（作为数组）
                article['keywords'] = [account_type]
            articles.append(article)
    elif 'articles' in data:
        # 旧格式
        articles = data.get('articles', [])
    elif isinstance(data, list):
        # 直接是数组
        articles = data
    else:
        articles = []
    
    if not isinstance(articles, list) or len(articles) == 0:
        return jsonify({
            "code": 400,
            "msg": "rss_list或articles必须是非空数组",
            "data": None
        }), 400
    
    try:
        import json
        china_time = get_china_time()
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_wechat_hotspot_articles_table(cursor)
            
            for idx, article in enumerate(articles):
                try:
                    # 提取字段
                    nick_name = article.get('nick_name', '').strip() if article.get('nick_name') else None
                    biz = article.get('biz', '').strip() if article.get('biz') else None
                    create_time = article.get('create_time', '').strip() if article.get('create_time') else None
                    title = article.get('title', '').strip() if article.get('title') else None
                    url = article.get('url', '').strip() if article.get('url') else None
                    content = article.get('content', '').strip() if article.get('content') else None
                    content_multi_text = article.get('content_multi_text', '').strip() if article.get('content_multi_text') else None
                    pubtime = article.get('pubtime', '').strip() if article.get('pubtime') else None
                    read_count = article.get('read', 0) or 0
                    zan = article.get('zan', 0) or 0
                    looking = article.get('looking', 0) or 0
                    share_num = article.get('share_num', 0) or 0
                    collect_num = article.get('collect_num', 0) or 0
                    comment_count = article.get('comment_count', 0) or 0
                    summary = article.get('summary', '').strip() if article.get('summary') else None
                    headline = article.get('headline', '').strip() if article.get('headline') else None
                    
                    # 处理keywords：如果是数组，转换为JSON字符串
                    keywords = article.get('keywords', None)
                    if isinstance(keywords, list):
                        keywords = json.dumps(keywords, ensure_ascii=False)
                    elif keywords:
                        keywords = str(keywords).strip()
                    else:
                        keywords = None
                    
                    # URL是唯一标识，如果已存在则更新，否则插入
                    if url:
                        # 检查是否已存在
                        cursor.execute('SELECT id FROM wechat_hotspot_articles WHERE url = ?', (url,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE wechat_hotspot_articles SET
                                    nick_name = ?,
                                    biz = ?,
                                    create_time = ?,
                                    title = ?,
                                    content = ?,
                                    content_multi_text = ?,
                                    pubtime = ?,
                                    read_count = ?,
                                    zan = ?,
                                    looking = ?,
                                    share_num = ?,
                                    collect_num = ?,
                                    comment_count = ?,
                                    summary = ?,
                                    headline = ?,
                                    keywords = ?,
                                    updated_at = ?
                                WHERE url = ?
                            ''', (
                                nick_name, biz, create_time, title, content, content_multi_text,
                                pubtime, read_count, zan, looking, share_num, collect_num,
                                comment_count, summary, headline, keywords, china_time, url
                            ))
                            updated_count += 1
                        else:
                            # 插入新记录
                            cursor.execute('''
                                INSERT INTO wechat_hotspot_articles (
                                    nick_name, biz, create_time, title, url, content, content_multi_text,
                                    pubtime, read_count, zan, looking, share_num, collect_num,
                                    comment_count, summary, headline, keywords, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                nick_name, biz, create_time, title, url, content, content_multi_text,
                                pubtime, read_count, zan, looking, share_num, collect_num,
                                comment_count, summary, headline, keywords, china_time, china_time
                            ))
                            inserted_count += 1
                    else:
                        skipped_count += 1
                        errors.append(f"第{idx+1}条记录缺少url字段，已跳过")
                        
                except Exception as e:
                    skipped_count += 1
                    error_msg = f"第{idx+1}条记录处理失败: {str(e)[:100]}"
                    errors.append(error_msg)
                    print(f"处理公众号文章失败: {error_msg}")
                    continue
            
            conn.commit()
            
            result_msg = f"保存完成：新增{inserted_count}条，更新{updated_count}条"
            if skipped_count > 0:
                result_msg += f"，跳过{skipped_count}条"
            
            return jsonify({
                "code": 200,
                "msg": result_msg,
                "data": {
                    "inserted": inserted_count,
                    "updated": updated_count,
                    "skipped": skipped_count,
                    "total": len(articles),
                    "errors": errors if errors else None
                }
            }), 200
            
    except Exception as e:
        print(f"保存公众号爬取文章失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"保存失败: {str(e)}",
            "data": None
        }), 500

@app.route('/hotspot/wechat/articles', methods=['GET'])
def list_wechat_hotspot_articles():
    """获取公众号爬取文章列表"""
    try:
        import json
        from datetime import datetime, timedelta
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            ensure_wechat_hotspot_articles_table(cursor)
            
            # 获取查询参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 20))
            offset = (page - 1) * page_size
            
            # 获取筛选参数
            # 支持多个nick_name参数（多选）
            nick_names = request.args.getlist('nick_name')  # 获取所有nick_name参数值
            nick_name = request.args.get('nick_name', '').strip()  # 兼容单个参数
            title = request.args.get('title', '').strip()
            create_time_start = request.args.get('create_time_start', '').strip()
            create_time_end = request.args.get('create_time_end', '').strip()
            pubtime_start = request.args.get('pubtime_start', '').strip()
            pubtime_end = request.args.get('pubtime_end', '').strip()
            
            # 构建WHERE条件
            where_conditions = []
            where_params = []
            
            # 处理nick_name筛选（支持多选）
            if nick_names and len(nick_names) > 0:
                # 过滤掉空值，同时处理URL解码
                import urllib.parse
                valid_nick_names = []
                for n in nick_names:
                    if n and n.strip():
                        # 处理URL编码的参数
                        decoded = urllib.parse.unquote(n.strip())
                        valid_nick_names.append(decoded)
                if valid_nick_names:
                    # 使用IN查询支持多个值
                    placeholders = ','.join(['?' for _ in valid_nick_names])
                    where_conditions.append(f'nick_name IN ({placeholders})')
                    where_params.extend(valid_nick_names)
            elif nick_name:
                # 兼容单个nick_name参数（向后兼容），处理URL解码
                import urllib.parse
                decoded_nick_name = urllib.parse.unquote(nick_name)
                where_conditions.append('nick_name = ?')
                where_params.append(decoded_nick_name)
            
            if title:
                where_conditions.append('title LIKE ?')
                where_params.append(f'%{title}%')
            
            if create_time_start:
                where_conditions.append('created_at >= ?')
                where_params.append(create_time_start)
            
            if create_time_end:
                where_conditions.append('created_at <= ?')
                where_params.append(create_time_end)
            
            if pubtime_start:
                where_conditions.append('pubtime >= ?')
                where_params.append(pubtime_start)
            
            if pubtime_end:
                where_conditions.append('pubtime <= ?')
                where_params.append(pubtime_end)
            
            # 构建WHERE子句
            where_clause = ''
            if where_conditions:
                where_clause = 'WHERE ' + ' AND '.join(where_conditions)
            
            # 查询总数
            count_sql = f'SELECT COUNT(*) as total FROM wechat_hotspot_articles {where_clause}'
            cursor.execute(count_sql, where_params)
            total = cursor.fetchone()['total']
            
            # 查询列表
            query_sql = f'''
                SELECT 
                    id, nick_name, biz, create_time, title, url, content, content_multi_text,
                    pubtime, read_count, zan, looking, share_num, collect_num,
                    comment_count, summary, headline, keywords, created_at, updated_at
                FROM wechat_hotspot_articles
                {where_clause}
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
            '''
            query_params = where_params + [page_size, offset]
            cursor.execute(query_sql, query_params)
            
            rows = cursor.fetchall()
            articles = []
            for row in rows:
                # 解析keywords JSON
                keywords = None
                if row['keywords']:
                    try:
                        keywords = json.loads(row['keywords'])
                    except:
                        keywords = row['keywords']
                
                articles.append({
                    "id": row["id"],
                    "nick_name": row["nick_name"],
                    "biz": row["biz"],
                    "create_time": row["create_time"],
                    "title": row["title"],
                    "url": row["url"],
                    "content": row["content"],
                    "content_multi_text": row["content_multi_text"],
                    "pubtime": row["pubtime"],
                    "read": row["read_count"],
                    "zan": row["zan"],
                    "looking": row["looking"],
                    "share_num": row["share_num"],
                    "collect_num": row["collect_num"],
                    "comment_count": row["comment_count"],
                    "summary": row["summary"],
                    "headline": row["headline"],
                    "keywords": keywords,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return jsonify({
                "code": 200,
                "msg": "success",
                "data": {
                    "items": articles,
                    "total": total,
                    "page": page,
                    "page_size": page_size
                }
            }), 200
            
    except Exception as e:
        print(f"获取公众号爬取文章列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"获取失败: {str(e)}",
            "data": None
        }), 500

@app.route('/hotspot/records', methods=['GET'])
def list_hotspot_records():
    """
    获取热点中心列表，支持按平台过滤
    支持 article 和 image-text 类型，所有记录都包含 media_ids 字段
    """
    platform = (request.args.get('platform') or '').strip().lower()
    content_type = (request.args.get('content_type') or '').strip().lower()
    
    records = []

    try:
        import json
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            ensure_production_video_table(cursor)

            # 获取文章记录
            if not content_type or content_type in ('all', 'article'):
                cursor.execute('''
                    SELECT id,
                           article_title,
                           article_content,
                           article_desc,
                           article_media_id,
                           article_media_url,
                           COALESCE(publish_status, 'pending') as publish_status,
                           created_at
                    FROM production_articles
                    ORDER BY created_at DESC, id DESC
                ''')
                article_rows = cursor.fetchall()

                for row in article_rows:
                    # 将 media_id 转换为 media_ids 数组格式
                    media_id = row["article_media_id"] or ""
                    media_ids = [media_id] if media_id else []
                    
                    records.append({
                        "id": row["id"],
                        "content_type": "article",
                        "title": row["article_title"],
                        "summary": row["article_desc"] or "",
                        "content": row["article_content"],
                        "media_id": row["article_media_id"],
                        "media_url": row["article_media_url"],
                        "media_ids": media_ids,  # 包含 media_ids 字段
                        "publish_status": row["publish_status"] or "pending",  # 发布状态
                        "created_at": row["created_at"]
                    })

            # 获取图文记录
            if not content_type or content_type in ('all', 'image-text'):
                cursor.execute('''
                    SELECT id,
                           title,
                           content,
                           media_ids,
                           height,
                           width,
                           url,
                           COALESCE(publish_status, 'pending') as publish_status,
                           created_at
                    FROM production_image_text
                    ORDER BY created_at DESC, id DESC
                ''')
                image_text_rows = cursor.fetchall()

                for row in image_text_rows:
                    # 解析 media_ids JSON 字符串为数组
                    try:
                        media_ids = json.loads(row["media_ids"]) if row["media_ids"] else []
                    except:
                        media_ids = []
                    
                    records.append({
                        "id": row["id"],
                        "content_type": "image-text",
                        "title": row["title"],
                        "summary": "",  # 图文类型没有摘要字段
                        "content": row["content"],
                        "media_ids": media_ids,  # 包含 media_ids 字段
                        "height": row["height"],
                        "width": row["width"],
                        "url": row["url"],  # 添加 url 字段
                        "publish_status": row["publish_status"] or "pending",  # 发布状态
                        "created_at": row["created_at"]
                    })

    except Exception as e:
        print(f"获取热点记录失败: {e}")
        return jsonify({
            "code": 500,
            "msg": f"获取热点记录失败: {str(e)}",
            "data": None
        }), 500

    # 按创建时间倒序排序（最新的在前）
    records.sort(key=lambda x: (x.get('created_at') or '', x.get('id', 0)), reverse=True)
    
    # 可按 content_type 过滤
    if content_type and content_type not in ('all', ''):
        filtered = [record for record in records if record["content_type"] == content_type]
    else:
        filtered = records

    return jsonify({
        "code": 200,
        "msg": "success",
        "data": {
            "items": filtered,
            "total": len(filtered)
        }
    }), 200


@app.route('/production/records/<int:record_id>', methods=['DELETE'])
def delete_production_record(record_id):
    """
    删除指定的制作记录（支持文章、图文和视频记录）
    查询参数: content_type (可选，如果提供则直接操作对应表，否则尝试三张表)
    支持: article, image-text, video
    """
    try:
        content_type = (request.args.get('content_type') or '').strip().lower()
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            ensure_production_video_table(cursor)

            # 如果提供了 content_type，直接操作对应的表（更高效）
            if content_type == 'article':
                cursor.execute('SELECT id FROM production_articles WHERE id = ?', (record_id,))
                if cursor.fetchone():
                    cursor.execute('DELETE FROM production_articles WHERE id = ?', (record_id,))
                    conn.commit()
                    return jsonify({
                        "code": 200,
                        "msg": "文章记录已删除",
                        "data": {"id": record_id, "content_type": "article"}
                    }), 200
                return jsonify({
                    "code": 404,
                    "msg": "文章记录不存在",
                    "data": None
                }), 404
            
            elif content_type == 'image-text':
                cursor.execute('SELECT id FROM production_image_text WHERE id = ?', (record_id,))
                if cursor.fetchone():
                    cursor.execute('DELETE FROM production_image_text WHERE id = ?', (record_id,))
                    conn.commit()
                    return jsonify({
                        "code": 200,
                        "msg": "图文记录已删除",
                        "data": {"id": record_id, "content_type": "image-text"}
                    }), 200
                return jsonify({
                    "code": 404,
                    "msg": "图文记录不存在",
                    "data": None
                }), 404
            
            elif content_type == 'video':
                cursor.execute('SELECT id FROM production_video WHERE id = ?', (record_id,))
                if cursor.fetchone():
                    cursor.execute('DELETE FROM production_video WHERE id = ?', (record_id,))
                    conn.commit()
                    return jsonify({
                        "code": 200,
                        "msg": "视频记录已删除",
                        "data": {"id": record_id, "content_type": "video"}
                    }), 200
                return jsonify({
                    "code": 404,
                    "msg": "视频记录不存在",
                    "data": None
                }), 404
            
            # 如果没有提供 content_type，尝试三张表（向后兼容）
            # 先尝试从文章表删除
            cursor.execute('SELECT id FROM production_articles WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('DELETE FROM production_articles WHERE id = ?', (record_id,))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "制作记录已删除",
                    "data": {"id": record_id, "content_type": "article"}
                }), 200
            
            # 再尝试从图文表删除
            cursor.execute('SELECT id FROM production_image_text WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('DELETE FROM production_image_text WHERE id = ?', (record_id,))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "制作记录已删除",
                    "data": {"id": record_id, "content_type": "image-text"}
                }), 200
            
            # 再尝试从视频表删除
            cursor.execute('SELECT id FROM production_video WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('DELETE FROM production_video WHERE id = ?', (record_id,))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "制作记录已删除",
                    "data": {"id": record_id, "content_type": "video"}
                }), 200
            
            # 都不存在
            return jsonify({
                "code": 404,
                "msg": "制作记录不存在",
                "data": None
            }), 404

    except Exception as e:
        print(f"删除制作记录失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"删除失败: {str(e)}",
            "data": None
        }), 500

@app.route('/production/records', methods=['DELETE'])
def batch_delete_production_records():
    """
    批量删除制作记录（支持文章、图文和视频记录）
    请求体格式1（推荐，更高效）: { "content_type": "article", "ids": [1, 2, 3] }
    请求体格式2（兼容）: { "ids": [1, 2, 3] } - 会自动从三张表中查找
    """
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({
                "code": 400,
                "msg": "请求参数错误，需要提供 ids 数组",
                "data": None
            }), 400
        
        ids = data.get('ids', [])
        if not isinstance(ids, list) or len(ids) == 0:
            return jsonify({
                "code": 400,
                "msg": "ids 必须是非空数组",
                "data": None
            }), 400
        
        content_type = (data.get('content_type') or '').strip().lower()
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            ensure_production_video_table(cursor)
            
            # 如果提供了 content_type，直接操作对应的表（更高效）
            if content_type == 'article':
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f'SELECT id FROM production_articles WHERE id IN ({placeholders})', ids)
                existing_ids = [row[0] for row in cursor.fetchall()]
                
                if len(existing_ids) != len(ids):
                    missing_ids = set(ids) - set(existing_ids)
                    return jsonify({
                        "code": 404,
                        "msg": f"部分文章记录不存在: {list(missing_ids)}",
                        "data": None
                    }), 404
                
                cursor.execute(f'DELETE FROM production_articles WHERE id IN ({placeholders})', ids)
                deleted_count = cursor.rowcount
                conn.commit()
                
                return jsonify({
                    "code": 200,
                    "msg": f"成功删除 {deleted_count} 条文章记录",
                    "data": {
                        "deleted_count": deleted_count,
                        "deleted_ids": ids,
                        "content_type": "article"
                    }
                }), 200
            
            elif content_type == 'image-text':
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f'SELECT id FROM production_image_text WHERE id IN ({placeholders})', ids)
                existing_ids = [row[0] for row in cursor.fetchall()]
                
                if len(existing_ids) != len(ids):
                    missing_ids = set(ids) - set(existing_ids)
                    return jsonify({
                        "code": 404,
                        "msg": f"部分图文记录不存在: {list(missing_ids)}",
                        "data": None
                    }), 404
                
                cursor.execute(f'DELETE FROM production_image_text WHERE id IN ({placeholders})', ids)
                deleted_count = cursor.rowcount
                conn.commit()
                
                return jsonify({
                    "code": 200,
                    "msg": f"成功删除 {deleted_count} 条图文记录",
                    "data": {
                        "deleted_count": deleted_count,
                        "deleted_ids": ids,
                        "content_type": "image-text"
                    }
                }), 200
            
            elif content_type == 'video':
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f'SELECT id FROM production_video WHERE id IN ({placeholders})', ids)
                existing_ids = [row[0] for row in cursor.fetchall()]
                
                if len(existing_ids) != len(ids):
                    missing_ids = set(ids) - set(existing_ids)
                    return jsonify({
                        "code": 404,
                        "msg": f"部分视频记录不存在: {list(missing_ids)}",
                        "data": None
                    }), 404
                
                cursor.execute(f'DELETE FROM production_video WHERE id IN ({placeholders})', ids)
                deleted_count = cursor.rowcount
                conn.commit()
                
                return jsonify({
                    "code": 200,
                    "msg": f"成功删除 {deleted_count} 条视频记录",
                    "data": {
                        "deleted_count": deleted_count,
                        "deleted_ids": ids,
                        "content_type": "video"
                    }
                }), 200
            
            # 如果没有提供 content_type，从三张表中查找（向后兼容）
            placeholders = ','.join(['?'] * len(ids))
            
            # 从文章表查找
            cursor.execute(f'SELECT id FROM production_articles WHERE id IN ({placeholders})', ids)
            article_ids = [row[0] for row in cursor.fetchall()]
            
            # 从图文表查找
            cursor.execute(f'SELECT id FROM production_image_text WHERE id IN ({placeholders})', ids)
            image_text_ids = [row[0] for row in cursor.fetchall()]
            
            # 从视频表查找
            cursor.execute(f'SELECT id FROM production_video WHERE id IN ({placeholders})', ids)
            video_ids = [row[0] for row in cursor.fetchall()]
            
            existing_ids = set(article_ids + image_text_ids + video_ids)
            
            if len(existing_ids) != len(ids):
                missing_ids = set(ids) - existing_ids
                return jsonify({
                    "code": 404,
                    "msg": f"部分记录不存在: {list(missing_ids)}",
                    "data": None
                }), 404
            
            # 批量删除文章记录
            deleted_article_count = 0
            if article_ids:
                article_placeholders = ','.join(['?'] * len(article_ids))
                cursor.execute(f'DELETE FROM production_articles WHERE id IN ({article_placeholders})', article_ids)
                deleted_article_count = cursor.rowcount
            
            # 批量删除图文记录
            deleted_image_text_count = 0
            if image_text_ids:
                image_text_placeholders = ','.join(['?'] * len(image_text_ids))
                cursor.execute(f'DELETE FROM production_image_text WHERE id IN ({image_text_placeholders})', image_text_ids)
                deleted_image_text_count = cursor.rowcount
            
            # 批量删除视频记录
            deleted_video_count = 0
            if video_ids:
                video_placeholders = ','.join(['?'] * len(video_ids))
                cursor.execute(f'DELETE FROM production_video WHERE id IN ({video_placeholders})', video_ids)
                deleted_video_count = cursor.rowcount
            
            conn.commit()
            total_deleted = deleted_article_count + deleted_image_text_count + deleted_video_count
        
        return jsonify({
            "code": 200,
            "msg": f"成功删除 {total_deleted} 条记录（文章: {deleted_article_count}, 图文: {deleted_image_text_count}, 视频: {deleted_video_count}）",
            "data": {
                "deleted_count": total_deleted,
                "deleted_ids": ids,
                "details": {
                    "article": deleted_article_count,
                    "image_text": deleted_image_text_count,
                    "video": deleted_video_count
                }
            }
        }), 200
    
    except Exception as e:
        print(f"批量删除制作记录失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"批量删除失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/records/<int:record_id>/status', methods=['PUT'])
def update_production_record_status(record_id):
    """
    更新制作中心记录的发布状态
    请求体: { "status": "pending" | "processing" | "creating" | "success" | "failed", "content_type": "article" | "image-text" | "video" (可选) }
    如果提供了 content_type，直接操作对应的表（更高效）
    """
    try:
        data = request.get_json(silent=True) or {}
        status = data.get('status', '').strip().lower()
        content_type = (data.get('content_type') or '').strip().lower()
        
        # 验证状态值
        valid_statuses = ['pending', 'processing', 'creating', 'success', 'failed']
        if status not in valid_statuses:
            return jsonify({
                "code": 400,
                "msg": f"无效的状态值，必须是: {', '.join(valid_statuses)}",
                "data": None
            }), 400
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            ensure_production_video_table(cursor)
            
            # 如果提供了 content_type，直接操作对应的表（更高效）
            if content_type == 'article':
                cursor.execute('SELECT id FROM production_articles WHERE id = ?', (record_id,))
                if cursor.fetchone():
                    cursor.execute('''
                        UPDATE production_articles 
                        SET publish_status = ? 
                        WHERE id = ?
                    ''', (status, record_id))
                    conn.commit()
                    return jsonify({
                        "code": 200,
                        "msg": "文章记录状态已更新",
                        "data": {
                            "id": record_id,
                            "status": status,
                            "content_type": "article"
                        }
                    }), 200
                return jsonify({
                    "code": 404,
                    "msg": "文章记录不存在",
                    "data": None
                }), 404
            
            elif content_type == 'image-text':
                cursor.execute('SELECT id FROM production_image_text WHERE id = ?', (record_id,))
                if cursor.fetchone():
                    cursor.execute('''
                        UPDATE production_image_text 
                        SET publish_status = ? 
                        WHERE id = ?
                    ''', (status, record_id))
                    conn.commit()
                    return jsonify({
                        "code": 200,
                        "msg": "图文记录状态已更新",
                        "data": {
                            "id": record_id,
                            "status": status,
                            "content_type": "image-text"
                        }
                    }), 200
                return jsonify({
                    "code": 404,
                    "msg": "图文记录不存在",
                    "data": None
                }), 404
            
            elif content_type == 'video':
                cursor.execute('SELECT id FROM production_video WHERE id = ?', (record_id,))
                if cursor.fetchone():
                    cursor.execute('''
                        UPDATE production_video 
                        SET publish_status = ? 
                        WHERE id = ?
                    ''', (status, record_id))
                    conn.commit()
                    return jsonify({
                        "code": 200,
                        "msg": "视频记录状态已更新",
                        "data": {
                            "id": record_id,
                            "status": status,
                            "content_type": "video"
                        }
                    }), 200
                return jsonify({
                    "code": 404,
                    "msg": "视频记录不存在",
                    "data": None
                }), 404
            
            # 如果没有提供 content_type，尝试三张表（向后兼容）
            # 先尝试更新文章表
            cursor.execute('SELECT id FROM production_articles WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE production_articles 
                    SET publish_status = ? 
                    WHERE id = ?
                ''', (status, record_id))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "制作中心记录状态已更新",
                    "data": {
                        "id": record_id,
                        "status": status,
                        "content_type": "article"
                    }
                }), 200
            
            # 再尝试更新图文表
            cursor.execute('SELECT id FROM production_image_text WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE production_image_text 
                    SET publish_status = ? 
                    WHERE id = ?
                ''', (status, record_id))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "制作中心记录状态已更新",
                    "data": {
                        "id": record_id,
                        "status": status,
                        "content_type": "image-text"
                    }
                }), 200
            
            # 再尝试更新视频表
            cursor.execute('SELECT id FROM production_video WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE production_video 
                    SET publish_status = ? 
                    WHERE id = ?
                ''', (status, record_id))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "制作中心记录状态已更新",
                    "data": {
                        "id": record_id,
                        "status": status,
                        "content_type": "video"
                    }
                }), 200
            
            # 记录不存在
            return jsonify({
                "code": 404,
                "msg": "记录不存在",
                "data": None
            }), 404
    
    except Exception as e:
        print(f"更新制作中心记录状态失败: {e}")
        return jsonify({
            "code": 500,
            "msg": f"更新状态失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/image-text/<int:record_id>', methods=['PUT'])
def update_production_image_text(record_id):
    """
    更新图文记录内容
    参数: title, content, media_ids (数组), height, width, url (可选)
    """
    data = request.get_json(silent=True) or {}
    
    try:
        import json
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_image_text_table(cursor)
            
            # 检查记录是否存在
            cursor.execute('SELECT id FROM production_image_text WHERE id = ?', (record_id,))
            if not cursor.fetchone():
                return jsonify({
                    "code": 404,
                    "msg": "记录不存在",
                    "data": None
                }), 404
            
            # 将 media_ids 数组转换为 JSON 字符串存储
            media_ids = data.get('media_ids', [])
            if not isinstance(media_ids, list):
                return jsonify({
                    "code": 400,
                    "msg": "media_ids 必须是数组",
                    "data": None
                }), 400
            
            media_ids_json = json.dumps(media_ids, ensure_ascii=False)
            
            # 获取 url 参数（可选）
            url = data.get('url', '').strip() if data.get('url') else None
            
            # 更新记录
            cursor.execute('''
                UPDATE production_image_text
                SET title = ?,
                    content = ?,
                    media_ids = ?,
                    height = ?,
                    width = ?,
                    url = ?
                WHERE id = ?
            ''', (
                data.get('title', '').strip(),
                data.get('content', '').strip(),
                media_ids_json,
                data.get('height'),
                data.get('width'),
                url,
                record_id
            ))
            conn.commit()
        
        return jsonify({
            "code": 200,
            "msg": "图文信息已更新",
            "data": {
                "id": record_id
            }
        }), 200
    
    except Exception as e:
        print(f"更新图文信息失败: {e}")
        return jsonify({
            "code": 500,
            "msg": f"更新失败: {str(e)}",
            "data": None
        }), 500


@app.route('/production/articles/<int:record_id>', methods=['PUT'])
def update_production_article(record_id):
    """
    更新文章记录内容
    参数: title, content, desc, url, html
    """
    data = request.get_json(silent=True) or {}
    
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            
            # 检查记录是否存在
            cursor.execute('SELECT id FROM production_articles WHERE id = ?', (record_id,))
            if not cursor.fetchone():
                return jsonify({
                    "code": 404,
                    "msg": "记录不存在",
                    "data": None
                }), 404
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(production_articles)")
            columns = [row[1] for row in cursor.fetchall()]
            has_new_fields = 'title' in columns and 'content' in columns
            has_old_fields = 'article_title' in columns and 'article_content' in columns
            
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            desc = data.get('desc', '').strip()
            url = data.get('url', '').strip()
            html = data.get('html', '').strip()
            
            if has_new_fields and has_old_fields:
                # 同时更新新旧字段（兼容）
                cursor.execute('''
                    UPDATE production_articles
                    SET title = ?,
                        content = ?,
                        desc = ?,
                        url = ?,
                        html = ?,
                        article_title = ?,
                        article_content = ?,
                        article_desc = ?,
                        article_media_url = ?
                    WHERE id = ?
                ''', (
                    title, content, desc, url, html,
                    title, content, desc, url,  # 旧字段也更新
                    record_id
                ))
            elif has_new_fields:
                # 只更新新字段
                cursor.execute('''
                    UPDATE production_articles
                    SET title = ?,
                        content = ?,
                        desc = ?,
                        url = ?,
                        html = ?
                    WHERE id = ?
                ''', (title, content, desc, url, html, record_id))
            else:
                # 只更新旧字段（兼容）
                cursor.execute('''
                    UPDATE production_articles
                    SET article_title = ?,
                        article_content = ?,
                        article_desc = ?,
                        article_media_url = ?
                    WHERE id = ?
                ''', (title, content, desc, url, record_id))
            
            conn.commit()
        
        return jsonify({
            "code": 200,
            "msg": "文章信息已更新",
            "data": {
                "id": record_id
            }
        }), 200
    
    except Exception as e:
        print(f"更新文章信息失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"更新失败: {str(e)}",
            "data": None
        }), 500


@app.route('/publish/records', methods=['GET'])
def list_publish_records():
    """
    获取发布中心记录列表，可按 content_type 过滤
    返回所有发布状态为 success 的记录
    """
    content_type = (request.args.get('content_type') or '').strip().lower()
    supported_types = {'', 'all', 'article', 'image-text', 'video'}
    
    if content_type and content_type not in supported_types:
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": []
        }), 200
    
    records = []
    
    try:
        import json
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            ensure_production_video_table(cursor)
            
            # 获取文章记录（只返回发布成功的）
            if not content_type or content_type in ('all', 'article'):
                # 检查表结构，优先使用新字段
                cursor.execute("PRAGMA table_info(production_articles)")
                columns = [row[1] for row in cursor.fetchall()]
                has_new_fields = 'title' in columns and 'content' in columns
                has_old_fields = 'article_title' in columns
                
                if has_new_fields:
                    # 使用新字段（优先），只在旧字段存在时才尝试兼容
                    if has_old_fields:
                        cursor.execute('''
                            SELECT id,
                                   COALESCE(NULLIF(title, ''), article_title, '') as title,
                                   COALESCE(NULLIF(content, ''), article_content, '') as content,
                                   COALESCE(NULLIF(desc, ''), article_desc, '') as desc,
                                   COALESCE(NULLIF(url, ''), article_media_url, '') as url,
                                   COALESCE(html, '') as html,
                                   COALESCE(publish_status, 'pending') as publish_status,
                                   created_at
                            FROM production_articles
                            WHERE publish_status = 'success'
                            ORDER BY created_at DESC, id DESC
                        ''')
                    else:
                        # 只有新字段，直接使用
                        cursor.execute('''
                            SELECT id,
                                   COALESCE(title, '') as title,
                                   COALESCE(content, '') as content,
                                   COALESCE(desc, '') as desc,
                                   COALESCE(url, '') as url,
                                   COALESCE(html, '') as html,
                                   COALESCE(publish_status, 'pending') as publish_status,
                                   created_at
                            FROM production_articles
                            WHERE publish_status = 'success'
                            ORDER BY created_at DESC, id DESC
                        ''')
                    article_rows = cursor.fetchall()
                else:
                    # 兼容旧字段
                    if has_old_fields:
                        cursor.execute('''
                            SELECT id,
                                   article_title as title,
                                   article_content as content,
                                   article_desc as desc,
                                   article_media_url as url,
                                   '' as html,
                                   COALESCE(publish_status, 'pending') as publish_status,
                                   created_at
                            FROM production_articles
                            WHERE publish_status = 'success'
                            ORDER BY created_at DESC, id DESC
                        ''')
                        article_rows = cursor.fetchall()
                    else:
                        # 既没有新字段也没有旧字段，跳过查询
                        article_rows = []
                
                # 处理查询结果
                for row in article_rows:
                    records.append({
                        "id": row["id"],
                        "content_type": "article",
                        "title": row["title"] or "",
                        "content": row["content"] or "",
                        "desc": row["desc"] or "",
                        "url": row["url"] or "",
                        "html": row["html"] or "",
                        "summary": row["desc"] or "",  # 兼容字段
                        "publish_status": row["publish_status"] or "pending",
                        "created_at": row["created_at"] or ""
                    })
            
            # 获取图文记录（只返回发布成功的）
            if not content_type or content_type in ('all', 'image-text'):
                try:
                    cursor.execute('''
                        SELECT id,
                               title,
                               content,
                               media_ids,
                               height,
                               width,
                               url,
                               COALESCE(publish_status, 'pending') as publish_status,
                               created_at
                        FROM production_image_text
                        WHERE publish_status = 'success'
                        ORDER BY created_at DESC, id DESC
                    ''')
                except sqlite3.OperationalError:
                    # 如果字段不存在，使用简化查询
                    cursor.execute('''
                        SELECT id,
                               title,
                               content,
                               media_ids,
                               url,
                               COALESCE(publish_status, 'pending') as publish_status,
                               created_at
                        FROM production_image_text
                        WHERE publish_status = 'success'
                        ORDER BY created_at DESC, id DESC
                    ''')
                
                image_text_rows = cursor.fetchall()
                
                for row in image_text_rows:
                    try:
                        media_ids = json.loads(row["media_ids"]) if row["media_ids"] else []
                    except:
                        media_ids = []
                    
                    # 安全获取可选字段
                    height = row["height"] if "height" in row.keys() else None
                    width = row["width"] if "width" in row.keys() else None
                    
                    records.append({
                        "id": row["id"],
                        "content_type": "image-text",
                        "title": row["title"] or "",
                        "summary": "",
                        "content": row["content"] or "",
                        "media_ids": media_ids,
                        "height": height,
                        "width": width,
                        "url": row["url"] or "",
                        "publish_status": row["publish_status"] or "pending",
                        "created_at": row["created_at"] or ""
                    })
            
            # 获取视频记录（只返回发布成功的）
            if not content_type or content_type in ('all', 'video'):
                try:
                    cursor.execute('''
                        SELECT id,
                               title,
                               content,
                               "desc",
                               keywords,
                               video,
                               material_url,
                               COALESCE(publish_status, 'pending') as publish_status,
                               created_at
                        FROM production_video
                        WHERE publish_status = 'success'
                        ORDER BY created_at DESC, id DESC
                    ''')
                except sqlite3.OperationalError:
                    # 如果字段不存在，使用简化查询
                    try:
                        cursor.execute('''
                            SELECT id,
                                   title,
                                   content,
                                   keywords,
                                   video,
                                   material_url,
                                   COALESCE(publish_status, 'pending') as publish_status,
                                   created_at
                            FROM production_video
                            WHERE publish_status = 'success'
                            ORDER BY created_at DESC, id DESC
                        ''')
                    except sqlite3.OperationalError:
                        # 如果material_url也不存在，使用最简查询
                        cursor.execute('''
                            SELECT id,
                                   title,
                                   content,
                                   keywords,
                                   video,
                                   COALESCE(publish_status, 'pending') as publish_status,
                                   created_at
                            FROM production_video
                            WHERE publish_status = 'success'
                            ORDER BY created_at DESC, id DESC
                        ''')
                
                video_rows = cursor.fetchall()
                
                for row in video_rows:
                    keywords = row["keywords"] or ""
                    try:
                        keywords_list = json.loads(keywords) if keywords else []
                    except:
                        keywords_list = [k.strip() for k in keywords.split(',')] if keywords else []
                    
                    # 安全获取desc字段
                    desc_value = ""
                    row_keys = [k.lower() for k in row.keys()]
                    if 'desc' in row_keys:
                        for key in row.keys():
                            if key.lower() == 'desc':
                                desc_value = row[key] or ""
                                break
                    
                    # 安全获取material_url字段
                    material_url = row["material_url"] if "material_url" in row.keys() else ""
                    
                    records.append({
                        "id": row["id"],
                        "content_type": "video",
                        "title": row["title"] or "",
                        "summary": desc_value,
                        "content": row["content"] or "",
                        "keywords": keywords_list,
                        "video": row["video"] or "",
                        "material_url": material_url,
                        "publish_status": row["publish_status"] or "pending",
                        "created_at": row["created_at"] or ""
                    })
    
    except Exception as e:
        print(f"获取发布记录失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"获取发布记录失败: {str(e)}",
            "data": None
        }), 500
    
    # 按创建时间倒序排序
    records.sort(key=lambda x: (x.get('created_at') or '', x.get('id', 0)), reverse=True)
    
    # 可按 content_type 过滤
    if content_type and content_type not in ('all', ''):
        filtered = [record for record in records if record["content_type"] == content_type]
    else:
        filtered = records
    
    return jsonify({
        "code": 200,
        "msg": "success",
        "data": filtered
    }), 200


@app.route('/publish/records/<int:record_id>/status', methods=['PUT'])
def update_publish_record_status(record_id):
    """
    更新发布中心记录的发布状态
    请求体: { "status": "pending" | "processing" | "success" | "failed" }
    """
    try:
        data = request.get_json(silent=True) or {}
        status = data.get('status', '').strip().lower()
        
        # 验证状态值
        valid_statuses = ['pending', 'processing', 'success', 'failed']
        if status not in valid_statuses:
            return jsonify({
                "code": 400,
                "msg": f"无效的状态值，必须是: {', '.join(valid_statuses)}",
                "data": None
            }), 400
        
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            ensure_production_article_table(cursor)
            ensure_production_image_text_table(cursor)
            
            # 先尝试更新文章表
            cursor.execute('SELECT id FROM production_articles WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE production_articles 
                    SET publish_status = ? 
                    WHERE id = ?
                ''', (status, record_id))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "发布中心记录状态已更新",
                    "data": {
                        "id": record_id,
                        "status": status
                    }
                }), 200
            
            # 再尝试更新图文表
            cursor.execute('SELECT id FROM production_image_text WHERE id = ?', (record_id,))
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE production_image_text 
                    SET publish_status = ? 
                    WHERE id = ?
                ''', (status, record_id))
                conn.commit()
                return jsonify({
                    "code": 200,
                    "msg": "发布中心记录状态已更新",
                    "data": {
                        "id": record_id,
                        "status": status
                    }
                }), 200
            
            # 记录不存在
            return jsonify({
                "code": 404,
                "msg": "记录不存在",
                "data": None
            }), 404
    
    except Exception as e:
        print(f"更新发布中心记录状态失败: {e}")
        return jsonify({
            "code": 500,
            "msg": f"更新状态失败: {str(e)}",
            "data": None
        }), 500

@app.route('/deleteFile', methods=['GET'])
def delete_file():
    file_id = request.args.get('id')

    if not file_id or not file_id.isdigit():
        return jsonify({
            "code": 400,
            "msg": "Invalid or missing file ID",
            "data": None
        }), 400

    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询要删除的记录
            cursor.execute("SELECT * FROM file_records WHERE id = ?", (file_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "File not found",
                    "data": None
                }), 404

            record = dict(record)

            # 获取文件路径并删除实际文件
            file_path = Path(BASE_DIR / "videoFile" / record['file_path'])
            if file_path.exists():
                try:
                    file_path.unlink()  # 删除文件
                    print(f"✅ 实际文件已删除: {file_path}")
                except Exception as e:
                    print(f"⚠️ 删除实际文件失败: {e}")
                    # 即使删除文件失败，也要继续删除数据库记录，避免数据不一致
            else:
                print(f"⚠️ 实际文件不存在: {file_path}")

            # 删除数据库记录
            cursor.execute("DELETE FROM file_records WHERE id = ?", (file_id,))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "File deleted successfully",
            "data": {
                "id": record['id'],
                "filename": record['filename']
            }
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("delete failed!"),
            "data": None
        }), 500

@app.route('/deleteAccount', methods=['GET'])
def delete_account():
    account_id = int(request.args.get('id'))

    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询要删除的记录
            cursor.execute("SELECT * FROM user_info WHERE id = ?", (account_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "account not found",
                    "data": None
                }), 404

            record = dict(record)

            # 删除数据库记录
            cursor.execute("DELETE FROM user_info WHERE id = ?", (account_id,))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "account deleted successfully",
            "data": None
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("delete failed!"),
            "data": None
        }), 500

@app.route('/manualConfirmLogin', methods=['POST'])
def manual_confirm_login():
    """手动确认登录（用于视频号等需要手动确认的平台）"""
    try:
        type = request.args.get('type')  # 平台类型：1 小红书 2 视频号 3 抖音 4 快手
        id = request.args.get('id')  # 账号名称
        
        if not type or not id:
            return jsonify({
                "code": 400,
                "msg": "参数不完整",
                "data": None
            }), 400
        
        # 只支持视频号（type=2）
        if type != '2':
            return jsonify({
                "code": 400,
                "msg": "手动确认登录仅支持视频号",
                "data": None
            }), 400
        
        # 检查是否有保存的浏览器上下文
        if id not in active_browser_contexts:
            print(f"[手动确认登录] ❌ 未找到登录会话: {id}，当前活跃会话: {list(active_browser_contexts.keys())}", flush=True)
            return jsonify({
                "code": 404,
                "msg": "未找到登录会话，请重新开始登录流程",
                "data": None
            }), 404
        
        browser_context = active_browser_contexts[id]
        print(f"[手动确认登录] ✅ 找到浏览器上下文: {id}", flush=True)
        print(f"[手动确认登录] 浏览器上下文内容: {list(browser_context.keys())}", flush=True)
        
        # 异步保存Cookie并验证
        import asyncio
        from myUtils.auth import check_cookie
        from pathlib import Path
        import uuid
        
        async def save_and_verify():
            try:
                # 优先使用已保存的cookies（在同一个事件循环中读取的）
                cookies = browser_context.get('cookies')
                cookies_ready = browser_context.get('cookies_ready', False)
                
                if not cookies_ready or not cookies:
                    return False, "Cookies未准备好，请确保已扫码登录"
                
                # 保存Cookie到文件
                uuid_v1 = uuid.uuid1()
                cookies_dir = Path(BASE_DIR / "cookiesFile")
                cookies_dir.mkdir(exist_ok=True)
                cookie_path = cookies_dir / f"{uuid_v1}.json"
                
                # 手动构建 storage_state 格式的 JSON
                import json
                storage_state = {
                    "cookies": cookies,
                    "origins": []
                }
                
                # 保存到文件
                with open(cookie_path, 'w', encoding='utf-8') as f:
                    json.dump(storage_state, f, ensure_ascii=False, indent=2)
                
                print(f"💾 Cookie已保存到: {cookie_path}", flush=True)
                
                # 验证Cookie
                result = await check_cookie(2, f"{uuid_v1}.json")
                if not result:
                    return False, "Cookie验证失败"
                
                # 保存到数据库
                with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO user_info (type, filePath, userName, status)
                        VALUES (?, ?, ?, ?)
                    ''', (2, f"{uuid_v1}.json", id, 1))
                    conn.commit()
                
                # 清理浏览器上下文（不需要关闭，因为可能还在使用中）
                # 只从字典中删除引用
                pass
                
                if id in active_browser_contexts:
                    del active_browser_contexts[id]
                
                return True, f"{uuid_v1}.json"
            except Exception as e:
                import traceback
                traceback.print_exc()
                return False, str(e)
        
        # 运行异步函数
        # 优先使用已保存的cookies，如果没有则尝试从临时Cookie文件读取，最后尝试从浏览器上下文主动获取
        import json
        cookies = browser_context.get('cookies')
        cookies_ready = browser_context.get('cookies_ready', False)
        temp_cookie_path = browser_context.get('temp_cookie_path')
        
        print(f"[手动确认登录] 当前状态 - cookies_ready: {cookies_ready}, cookies数量: {len(cookies) if cookies else 0}, temp_cookie_path: {temp_cookie_path}", flush=True)
        
        # 如果cookies未准备好，等待一小段时间后重试（给登录流程时间保存cookies）
        if (not cookies_ready or not cookies) and 'context' in browser_context:
            print(f"[手动确认登录] ⏳ Cookies未准备好，等待2秒后重试...", flush=True)
            import time
            time.sleep(2)
            # 重新读取状态
            cookies = browser_context.get('cookies')
            cookies_ready = browser_context.get('cookies_ready', False)
            temp_cookie_path = browser_context.get('temp_cookie_path')
            print(f"[手动确认登录] 重试后状态 - cookies_ready: {cookies_ready}, cookies数量: {len(cookies) if cookies else 0}", flush=True)
        
        # 如果cookies未准备好，尝试从临时Cookie文件读取
        if (not cookies_ready or not cookies) and temp_cookie_path:
            try:
                import os
                from pathlib import Path
                if os.path.exists(temp_cookie_path):
                    with open(temp_cookie_path, 'r', encoding='utf-8') as f:
                        temp_cookie_data = json.load(f)
                        cookies = temp_cookie_data.get('cookies', [])
                        if cookies:
                            cookies_ready = True
                            browser_context['cookies'] = cookies
                            browser_context['cookies_ready'] = True
                            print(f"[+] 从临时Cookie文件读取cookies成功（共{len(cookies)}个cookies）", flush=True)
            except Exception as e:
                print(f"⚠️ 从临时Cookie文件读取失败: {e}", flush=True)
        
        # 如果cookies仍未准备好，尝试主动从浏览器上下文读取（这是关键修复）
        if (not cookies_ready or not cookies) and 'context' in browser_context:
            try:
                print(f"[手动确认登录] ========== 开始主动获取Cookies ==========", flush=True)
                print(f"[手动确认登录] [+] 步骤0: 检查浏览器上下文...", flush=True)
                context = browser_context.get('context')
                if context:
                    print(f"[手动确认登录] ✅ 步骤0: 浏览器上下文存在", flush=True)
                    # 创建新的事件循环来运行异步函数
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        # 步骤1: 先保存storage_state到临时文件，然后从文件中读取
                        print(f"[手动确认登录] [+] 步骤1: 准备临时Cookie文件路径...", flush=True)
                        if not temp_cookie_path:
                            temp_uuid = uuid.uuid1()
                            cookies_dir = Path(BASE_DIR / "cookiesFile")
                            cookies_dir.mkdir(exist_ok=True)
                            temp_cookie_path = cookies_dir / f"{temp_uuid}.json"
                            browser_context['temp_cookie_path'] = str(temp_cookie_path)
                            print(f"[手动确认登录] ✅ 步骤1-1: 创建新的临时Cookie文件路径: {temp_cookie_path}", flush=True)
                        else:
                            print(f"[手动确认登录] ✅ 步骤1-1: 使用已有临时Cookie文件路径: {temp_cookie_path}", flush=True)
                        
                        # 步骤2: 先保存storage_state（包含所有cookies和localStorage）
                        print(f"[手动确认登录] [+] 步骤2: 开始保存storage_state到临时文件...", flush=True)
                        print(f"[手动确认登录]    目标文件: {temp_cookie_path}", flush=True)
                        loop.run_until_complete(context.storage_state(path=str(temp_cookie_path)))
                        print(f"[手动确认登录] ✅ 步骤2: storage_state已保存到临时文件", flush=True)
                        
                        # 验证文件是否成功保存
                        if temp_cookie_path.exists():
                            file_size = temp_cookie_path.stat().st_size
                            print(f"[手动确认登录]    文件大小: {file_size} 字节", flush=True)
                        else:
                            print(f"[手动确认登录] ⚠️ 步骤2: 警告 - 文件保存后不存在！", flush=True)
                        
                        # 等待一小段时间确保文件写入完成
                        import time
                        print(f"[手动确认登录] [+] 等待0.5秒确保文件写入完成...", flush=True)
                        time.sleep(0.5)
                        
                        # 步骤3: 从文件中读取cookies
                        print(f"[手动确认登录] [+] 步骤3: 开始从storage_state文件读取cookies...", flush=True)
                        cookies_from_file = []
                        storage_data = None
                        if temp_cookie_path.exists():
                            print(f"[手动确认登录]    文件存在，开始读取...", flush=True)
                            with open(temp_cookie_path, 'r', encoding='utf-8') as f:
                                storage_data = json.load(f)
                                cookies_from_file = storage_data.get('cookies', [])
                                origins_data = storage_data.get('origins', [])
                                print(f"[手动确认登录]    文件内容 - cookies数量: {len(cookies_from_file)}, origins数量: {len(origins_data)}", flush=True)
                                
                                if cookies_from_file and len(cookies_from_file) > 0:
                                    cookies = cookies_from_file
                                    cookies_ready = True
                                    browser_context['cookies'] = cookies
                                    browser_context['cookies_ready'] = True
                                    print(f"[手动确认登录] ✅ 步骤3: 从storage_state文件读取cookies成功！", flush=True)
                                    print(f"[手动确认登录]    Cookie数量: {len(cookies)}", flush=True)
                                    print(f"[手动确认登录]    前3个Cookie名称: {[c.get('name', 'N/A') for c in cookies[:3]]}", flush=True)
                                else:
                                    print(f"[手动确认登录] ⚠️ 步骤3: 文件中cookies数组为空", flush=True)
                                    if origins_data and len(origins_data) > 0:
                                        print(f"[手动确认登录]    但发现 {len(origins_data)} 个origins数据（可能包含localStorage）", flush=True)
                        else:
                            print(f"[手动确认登录] ❌ 步骤3: 临时Cookie文件不存在，无法读取", flush=True)
                        
                        # 步骤4: 如果文件中没有cookies，尝试直接从context读取
                        if not cookies or len(cookies) == 0:
                            print(f"[手动确认登录] [+] 步骤4: 文件中cookies为空，尝试直接从context.cookies()读取...", flush=True)
                            try:
                                cookies_from_context = loop.run_until_complete(context.cookies())
                                print(f"[手动确认登录]    context.cookies()返回结果: {len(cookies_from_context) if cookies_from_context else 0} 个cookies", flush=True)
                                
                                if cookies_from_context and len(cookies_from_context) > 0:
                                    cookies = cookies_from_context
                                    cookies_ready = True
                                    browser_context['cookies'] = cookies
                                    browser_context['cookies_ready'] = True
                                    print(f"[手动确认登录] ✅ 步骤4: 从浏览器上下文读取cookies成功！", flush=True)
                                    print(f"[手动确认登录]    Cookie数量: {len(cookies)}", flush=True)
                                    print(f"[手动确认登录]    前3个Cookie名称: {[c.get('name', 'N/A') for c in cookies[:3]]}", flush=True)
                                    
                                    # 更新临时文件
                                    print(f"[手动确认登录] [+] 步骤4-1: 更新临时Cookie文件...", flush=True)
                                    if storage_data is None:
                                        storage_data = {}
                                    storage_data['cookies'] = cookies
                                    if 'origins' not in storage_data:
                                        storage_data['origins'] = []
                                    
                                    with open(temp_cookie_path, 'w', encoding='utf-8') as f:
                                        json.dump(storage_data, f, ensure_ascii=False, indent=2)
                                    
                                    updated_file_size = temp_cookie_path.stat().st_size
                                    print(f"[手动确认登录] ✅ 步骤4-1: 临时Cookie文件已更新", flush=True)
                                    print(f"[手动确认登录]    更新后文件大小: {updated_file_size} 字节", flush=True)
                                else:
                                    print(f"[手动确认登录] ❌ 步骤4: context.cookies()返回的cookies也为空", flush=True)
                            except Exception as context_error:
                                print(f"[手动确认登录] ❌ 步骤4: 从context读取cookies失败: {context_error}", flush=True)
                                import traceback
                                traceback.print_exc()
                        
                        # 最终检查
                        print(f"[手动确认登录] ========== Cookies获取结果 ==========", flush=True)
                        print(f"[手动确认登录]    cookies_ready: {cookies_ready}", flush=True)
                        print(f"[手动确认登录]    cookies数量: {len(cookies) if cookies else 0}", flush=True)
                        if cookies and len(cookies) > 0:
                            print(f"[手动确认登录] ✅ 成功获取到Cookies！", flush=True)
                        else:
                            print(f"[手动确认登录] ❌ 未能获取到Cookies", flush=True)
                        print(f"[手动确认登录] ========================================", flush=True)
                    finally:
                        loop.close()
                else:
                    print(f"[手动确认登录] ⚠️ 步骤0: 浏览器上下文中的context为None", flush=True)
            except Exception as e:
                print(f"[手动确认登录] ❌ 主动从浏览器上下文读取cookies失败: {e}", flush=True)
                import traceback
                traceback.print_exc()
        elif (not cookies_ready or not cookies) and 'context' not in browser_context:
            print(f"[手动确认登录] ⚠️ 浏览器上下文中没有context对象，无法主动读取cookies", flush=True)
        
        if not cookies_ready or not cookies:
            print(f"[手动确认登录] ❌ Cookies未准备好 - cookies_ready: {cookies_ready}, cookies: {len(cookies) if cookies else 0}", flush=True)
            return jsonify({
                "code": 500,
                "msg": "Cookies未准备好，请确保已扫码登录",
                "data": None
            }), 500
        
        try:
            # 保存Cookie到文件
            print(f"[手动确认登录] ========== 开始保存Cookie到最终文件 ==========", flush=True)
            print(f"[手动确认登录] [+] 步骤5: 生成UUID和文件路径...", flush=True)
            uuid_v1 = uuid.uuid1()
            cookies_dir = Path(BASE_DIR / "cookiesFile")
            cookies_dir.mkdir(exist_ok=True)
            cookie_path = cookies_dir / f"{uuid_v1}.json"
            print(f"[手动确认登录] ✅ 步骤5: UUID生成成功: {uuid_v1}", flush=True)
            print(f"[手动确认登录] ✅ 步骤5: Cookie文件路径: {cookie_path}", flush=True)
            
            print(f"[手动确认登录] [+] 步骤6: 准备Cookie数据...", flush=True)
            print(f"[手动确认登录]    账号: {id}", flush=True)
            print(f"[手动确认登录]    Cookie数量: {len(cookies) if cookies else 0}", flush=True)
            if cookies and len(cookies) > 0:
                print(f"[手动确认登录]    前5个Cookie名称: {[c.get('name', 'N/A') for c in cookies[:5]]}", flush=True)
                print(f"[手动确认登录]    Cookie域名列表: {list(set([c.get('domain', 'N/A') for c in cookies[:10]]))}", flush=True)
            
            # 手动构建 storage_state 格式的 JSON
            storage_state = {
                "cookies": cookies,
                "origins": []
            }
            print(f"[手动确认登录] ✅ 步骤6: Cookie数据准备完成", flush=True)
            
            # 保存到文件
            print(f"[手动确认登录] [+] 步骤7: 开始写入Cookie文件...", flush=True)
            with open(cookie_path, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, ensure_ascii=False, indent=2)
            
            # 验证文件是否成功保存
            if cookie_path.exists():
                file_size = cookie_path.stat().st_size
                print(f"[手动确认登录] ✅ 步骤7: Cookie文件写入成功", flush=True)
                print(f"[手动确认登录]    文件大小: {file_size} 字节", flush=True)
                
                # 验证文件内容
                with open(cookie_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    saved_cookies_count = len(saved_data.get('cookies', []))
                    print(f"[手动确认登录]    验证: 文件中包含 {saved_cookies_count} 个cookies", flush=True)
                    if saved_cookies_count != len(cookies):
                        print(f"[手动确认登录] ⚠️ 警告: 保存的Cookie数量({saved_cookies_count})与原始数量({len(cookies) if cookies else 0})不一致", flush=True)
                    else:
                        print(f"[手动确认登录] ✅ 验证通过: Cookie数量一致", flush=True)
            else:
                print(f"[手动确认登录] ❌ 步骤7: Cookie文件写入失败 - 文件不存在！", flush=True)
            
            print(f"[手动确认登录] ========== Cookie文件保存完成 ==========", flush=True)
            
            # 验证Cookie（使用异步方式，但同步调用）
            from myUtils.auth import check_cookie
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(check_cookie(2, f"{uuid_v1}.json"))
            finally:
                loop.close()
            
            if not result:
                return jsonify({
                    "code": 500,
                    "msg": "Cookie验证失败",
                    "data": None
                }), 500
            
            # 保存到数据库
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_info (type, filePath, userName, status)
                    VALUES (?, ?, ?, ?)
                ''', (2, f"{uuid_v1}.json", id, 1))
                conn.commit()
            
            # 清理浏览器上下文
            if id in active_browser_contexts:
                del active_browser_contexts[id]
            
            print(f"[手动确认登录] ✅ 登录确认成功 - 接口: /manualConfirmLogin (POST)", flush=True)
            print(f"[手动确认登录] 📤 返回Cookie数据 - 账号: {id}, Cookie文件路径: {uuid_v1}.json, Cookie数量: {len(cookies) if cookies else 0}", flush=True)
            print(f"[手动确认登录] 返回JSON数据: {{'code': 200, 'msg': '登录确认成功', 'data': {{'filePath': '{uuid_v1}.json'}}}}", flush=True)
            
            return jsonify({
                "code": 200,
                "msg": "登录确认成功",
                "data": {
                    "filePath": f"{uuid_v1}.json"
                }
            }), 200
            
        except Exception as e:
            print(f"[手动确认登录] ❌ 手动确认登录失败: {str(e)}", flush=True)
            import traceback
            error_trace = traceback.format_exc()
            print(f"[手动确认登录] 错误堆栈:\n{error_trace}", flush=True)
            return jsonify({
                "code": 500,
                "msg": f"登录确认失败: {str(e)}",
                "data": None
            }), 500
            return jsonify({
                "code": 200,
                "msg": "登录确认成功",
                "data": {
                    "filePath": result
                }
            }), 200
        else:
            return jsonify({
                "code": 500,
                "msg": f"登录确认失败: {result}",
                "data": None
            }), 500
            
    except Exception as e:
        print(f"❌ 手动确认登录失败: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"登录确认失败: {str(e)}",
            "data": None
        }), 500

@app.route('/addAccountDirect', methods=['POST'])
def add_account_direct():
    """直接创建账号（不通过登录流程，用于本地上传Cookie）"""
    try:
        data = request.get_json(silent=True) or {}
        type = data.get('type')  # 平台类型：1 小红书 2 视频号 3 抖音 4 快手
        userName = data.get('userName', '').strip()
        platform = data.get('platform', '')  # 平台名称（用于日志）

        if not type:
            return jsonify({
                "code": 400,
                "msg": "平台类型不能为空",
                "data": None
            }), 400

        if not userName:
            return jsonify({
                "code": 400,
                "msg": "账号名称不能为空",
                "data": None
            }), 400

        # 检查账号是否已存在（根据用户名和平台类型）
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM user_info WHERE userName = ? AND type = ?', (userName, type))
            existing = cursor.fetchone()
            
            if existing:
                return jsonify({
                    "code": 400,
                    "msg": "该账号已存在",
                    "data": None
                }), 400

            # 创建一个占位符文件路径（用户后续可以上传Cookie文件）
            import uuid
            uuid_v1 = uuid.uuid1()
            filePath = f"{uuid_v1}.json"
            
            # 插入账号记录，status设为0（异常状态，因为还没有Cookie）
            cursor.execute('''
                INSERT INTO user_info (type, filePath, userName, status)
                VALUES (?, ?, ?, ?)
            ''', (type, filePath, userName, 0))
            conn.commit()
            
            # 获取新创建的账号ID
            account_id = cursor.lastrowid
            
            print(f"✅ 直接创建账号成功 - 平台: {platform}, 账号名称: {userName}, ID: {account_id}")

        return jsonify({
            "code": 200,
            "msg": "账号创建成功，请后续上传Cookie文件",
            "data": {
                "id": account_id,
                "userName": userName,
                "type": type,
                "filePath": filePath
            }
        }), 200

    except Exception as e:
        print(f"❌ 直接创建账号失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"创建账号失败: {str(e)}",
            "data": None
        }), 500


# SSE 登录接口
@app.route('/login')
def login():
    # 1 小红书 2 视频号 3 抖音 4 快手
    type = request.args.get('type')
    # 账号名
    id = request.args.get('id')
    # 自动化框架选择（仅视频号使用）
    automation_tool = request.args.get('automation_tool', 'playwright')
    
    print(f"\n[登录API] 收到登录请求 - 平台类型: {type}, 账号名称: {id}, 自动化框架: {automation_tool}", flush=True)
    print(f"[登录API] 账号名称参数值: {repr(id)}", flush=True)  # 使用repr显示原始字符串，包括特殊字符

    # 如果该账号已有正在进行的登录请求，先清理旧的队列
    if id in active_queues:
        print(f"[登录API] 警告：账号 {id} 已有正在进行的登录请求，将清理旧队列")
        old_queue = active_queues[id]
        # 尝试清空旧队列
        while not old_queue.empty():
            try:
                old_queue.get_nowait()
            except:
                pass

    # 模拟一个用于异步通信的队列
    status_queue = Queue()
    active_queues[id] = status_queue
    print(f"[登录API] 已创建新队列，当前活跃队列数: {len(active_queues)}", flush=True)

    # 如果是视频号登录，创建浏览器上下文存储
    browser_context_storage = None
    if type == '2':  # 视频号
        browser_context_storage = {}
        active_browser_contexts[id] = browser_context_storage
        print(f"[登录API] 已创建浏览器上下文存储: {id}", flush=True)

    def on_close():
        print(f"[登录API] 清理队列: {id}")
        if id in active_queues:
            del active_queues[id]
        # 清理浏览器上下文（延迟清理，给手动确认留时间）
        if id in active_browser_contexts:
            # 延迟30秒清理，给手动确认留时间
            def delayed_cleanup():
                import time
                time.sleep(30)
                if id in active_browser_contexts:
                    # 尝试关闭浏览器
                    try:
                        ctx = active_browser_contexts[id]
                        if 'browser' in ctx and ctx['browser']:
                            pass  # 浏览器会在登录流程中关闭
                    except:
                        pass
                    del active_browser_contexts[id]
                    print(f"[登录API] 已清理浏览器上下文: {id}", flush=True)
            threading.Thread(target=delayed_cleanup, daemon=True).start()
    
    # 启动异步任务线程
    print(f"[登录API] 启动登录线程，传递参数 - type: {type}, id: {repr(id)}, automation_tool: {automation_tool}", flush=True)
    print(f"[登录API] Cookie将通过SSE流返回 - 接口: /login (SSE流)", flush=True)
    thread = threading.Thread(target=run_async_function, args=(type,id,status_queue,browser_context_storage,automation_tool), daemon=True)
    thread.start()
    response = Response(sse_stream(status_queue,), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # 关键：禁用 Nginx 缓冲
    response.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'  # 确保CORS支持
    response.headers['Access-Control-Allow-Headers'] = 'Cache-Control'
    return response

def download_video_from_url(url, output_dir=None, max_retries=3):
    """
    从URL下载视频到本地（带重试机制）
    Args:
        url: 视频URL（如谷歌云存储链接）
        output_dir: 输出目录，默认为 videoFile 目录
        max_retries: 最大重试次数，默认3次
    Returns:
        下载后的本地文件名（相对于videoFile目录）
    """
    if output_dir is None:
        output_dir = Path(BASE_DIR / "videoFile")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 从URL中提取文件名
    parsed_url = urlparse(url)
    url_filename = os.path.basename(parsed_url.path)
    # 如果URL中没有文件名，使用UUID生成
    if not url_filename or '.' not in url_filename:
        url_filename = f"downloaded_{uuid.uuid1()}.mp4"
    # 去掉查询参数
    if '?' in url_filename:
        url_filename = url_filename.split('?')[0]
    
    # 生成唯一文件名
    uuid_v1 = uuid.uuid1()
    local_filename = f"{uuid_v1}_{url_filename}"
    local_filepath = output_dir / local_filename
        
    # 设置请求头，模拟浏览器请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Range': 'bytes=0-',  # 支持断点续传
    }
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            print(f"📥 开始从URL下载视频 (尝试 {attempt + 1}/{max_retries}): {url}")
            
            # 创建会话以保持连接，配置重试和连接池
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            import urllib3
            
            # 禁用 SSL 警告（因为国内服务器访问 Google 服务可能需要禁用 SSL 验证）
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            session = requests.Session()
            session.headers.update(headers)
            
            # 配置代理（用于访问 Google 服务）
            proxies = {}
            if HTTP_PROXY or HTTPS_PROXY:
                if HTTP_PROXY:
                    proxies['http'] = HTTP_PROXY
                if HTTPS_PROXY:
                    proxies['https'] = HTTPS_PROXY
                elif HTTP_PROXY:
                    # 如果只设置了 HTTP_PROXY，HTTPS 也使用它
                    proxies['https'] = HTTP_PROXY
                if proxies:
                    print(f"🌐 使用代理: {proxies}")
                    session.proxies = proxies
            else:
                print("⚠️ 未配置代理，将尝试直接连接（可能失败）")
            
            # 配置重试策略
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "HEAD"]
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=10
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # 下载文件（增加超时时间，使用连接池）
            print(f"📥 下载中: {url} -> {local_filepath}")
            
            # 对于 Google Cloud Storage 或国内服务器，默认禁用 SSL 验证
            # 因为国内服务器访问 Google 服务经常遇到 SSL/网络问题
            verify_ssl = False  # 默认禁用 SSL 验证，避免网络问题
            if 'storage.googleapis.com' in url or 'googleapis.com' in url:
                print("⚠️ 检测到 Google Cloud Storage URL，使用禁用 SSL 验证模式（国内服务器访问需要）")
                verify_ssl = False
            
            response = session.get(
                url, 
                stream=True, 
                timeout=(60, 900),  # (连接超时60秒, 读取超时900秒=15分钟)
                allow_redirects=True,
                verify=verify_ssl
            )
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            if total_size > 0:
                print(f"📦 文件大小: {total_size / (1024*1024):.2f} MB")
            
            # 写入文件（使用更大的chunk size以提高下载速度）
            downloaded_size = 0
            chunk_size = 64 * 1024  # 64KB chunks
            
            with open(local_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            # 每10MB打印一次进度
                            if downloaded_size % (10 * 1024 * 1024) < chunk_size:
                                print(f"📥 下载进度: {progress:.1f}% ({downloaded_size / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")
            
            # 验证文件是否完整下载
            if total_size > 0 and downloaded_size != total_size:
                raise Exception(f"文件下载不完整: 已下载 {downloaded_size} 字节，期望 {total_size} 字节")
            
            print(f"✅ 视频下载完成: {local_filename} ({downloaded_size / (1024*1024):.2f} MB)")
            session.close()
            return local_filename
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, 
                ConnectionResetError, requests.exceptions.ChunkedEncodingError,
                requests.exceptions.SSLError) as e:
            # 连接相关错误，可以重试
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"⚠️ 下载失败 (尝试 {attempt + 1}/{max_retries}): {error_type}: {error_msg}")
            
            # 检查是否是 ProtocolError（来自 urllib3）
            is_protocol_error = 'ProtocolError' in error_msg or '10054' in error_msg or 'ConnectionResetError' in error_msg
            
            # 如果是 SSL 错误或协议错误，最后一次尝试时禁用 SSL 验证
            if attempt == max_retries - 1 and (is_protocol_error or 'SSL' in error_msg or 'ssl' in error_msg.lower()):
                print(f"🔄 最后一次尝试：禁用 SSL 验证...")
                try:
                    # 禁用 SSL 警告
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    
                    session = requests.Session()
                    session.headers.update(headers)
                    # 配置代理（如果设置了）
                    proxies = {}
                    if HTTP_PROXY or HTTPS_PROXY:
                        if HTTP_PROXY:
                            proxies['http'] = HTTP_PROXY
                        if HTTPS_PROXY:
                            proxies['https'] = HTTPS_PROXY
                        elif HTTP_PROXY:
                            proxies['https'] = HTTP_PROXY
                    if proxies:
                        session.proxies = proxies
                    response = session.get(
                        url, 
                        stream=True, 
                        timeout=(60, 900),
                        allow_redirects=True,
                        verify=False  # 禁用 SSL 验证（仅作为最后手段）
                    )
                    response.raise_for_status()
                    
                    # 继续下载流程
                    total_size = int(response.headers.get('content-length', 0))
                    if total_size > 0:
                        print(f"📦 文件大小: {total_size / (1024*1024):.2f} MB")
                    
                    downloaded_size = 0
                    chunk_size = 64 * 1024
                    with open(local_filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                    
                    if total_size > 0 and downloaded_size != total_size:
                        raise Exception(f"文件下载不完整: 已下载 {downloaded_size} 字节，期望 {total_size} 字节")
                    
                    print(f"✅ 视频下载完成: {local_filename} ({downloaded_size / (1024*1024):.2f} MB)")
                    session.close()
                    return local_filename
                except Exception as ssl_e:
                    print(f"❌ 即使禁用 SSL 验证也失败: {str(ssl_e)}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3  # 递增等待时间：3秒、6秒、9秒
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
                # 如果文件已部分下载，删除它以便重新下载
                if local_filepath.exists():
                    try:
                        local_filepath.unlink()
                        print(f"🗑️ 已删除不完整的文件: {local_filename}")
                    except:
                        pass
                continue
            else:
                # 最后一次尝试也失败了
                print(f"❌ 下载视频失败（已重试 {max_retries} 次）: {str(e)}")
                import traceback
                traceback.print_exc()
                raise Exception(f"从URL下载视频失败（已重试 {max_retries} 次）: {str(e)}")
        
        except Exception as e:
            # 其他错误，不重试
            print(f"❌ 下载视频失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 清理不完整的文件
            if local_filepath.exists():
                try:
                    local_filepath.unlink()
                except:
                    pass
        raise Exception(f"从URL下载视频失败: {str(e)}")


def download_google_storage_file(file_path_or_name, output_dir=None):
    """
    从谷歌存储下载文件到本地
    Args:
        file_path_or_name: 文件名或file_path（从数据库中查询）
        output_dir: 输出目录，默认为 videoFile 目录
    Returns:
        下载后的本地文件名（相对于videoFile目录），如果文件不是谷歌存储或已存在本地，返回原文件名
    """
    if output_dir is None:
        output_dir = Path(BASE_DIR / "videoFile")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 查询数据库，判断文件是否来自谷歌存储
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 尝试通过file_path查询
            cursor.execute('''
                SELECT source, uri, file_path, filename 
                FROM file_records 
                WHERE file_path = ? OR filename = ?
                LIMIT 1
            ''', (file_path_or_name, file_path_or_name))
            
            row = cursor.fetchone()
            
            if not row:
                # 文件不在数据库中，检查本地是否存在（尝试多个目录）
                possible_paths = [
                    output_dir / file_path_or_name,  # videoFile 目录
                    Path(BASE_DIR / "media" / file_path_or_name),  # media 目录
                    Path(BASE_DIR / file_path_or_name),  # 根目录
                ]
                
                for possible_path in possible_paths:
                    if possible_path.exists():
                        print(f"✅ 文件不在数据库中，但本地文件存在: {possible_path}")
                        # 如果文件不在 videoFile 目录，复制过去
                        if possible_path.parent != output_dir:
                            import shutil
                            target_path = output_dir / file_path_or_name
                            shutil.copy2(possible_path, target_path)
                            print(f"✅ 文件已复制到 videoFile 目录: {target_path}")
                        return file_path_or_name
                
                raise FileNotFoundError(f"文件不存在（数据库和本地都没有）: {file_path_or_name} (已尝试: videoFile, media, 根目录)")
            
            source = row['source'] if row else None
            uri = row['uri'] if row else None
            
            # 如果不是谷歌存储文件，检查本地是否存在
            if source != '谷歌存储上传':
                # 尝试多个可能的目录
                possible_paths = [
                    output_dir / file_path_or_name,  # videoFile 目录
                    Path(BASE_DIR / "media" / file_path_or_name),  # media 目录
                    Path(BASE_DIR / file_path_or_name),  # 根目录
                ]
                
                for possible_path in possible_paths:
                    if possible_path.exists():
                        print(f"✅ 文件已存在于本地: {possible_path}")
                        # 返回相对于 videoFile 目录的文件名
                        if possible_path.parent == output_dir:
                            return file_path_or_name
                        else:
                            # 如果文件在其他目录，需要复制到 videoFile 目录
                            import shutil
                            target_path = output_dir / file_path_or_name
                            shutil.copy2(possible_path, target_path)
                            print(f"✅ 文件已复制到 videoFile 目录: {target_path}")
                            return file_path_or_name
                
                raise FileNotFoundError(f"本地文件不存在: {file_path_or_name} (已尝试: videoFile, media, 根目录)")
            
            # 如果是谷歌存储文件，检查是否已经下载过
            local_filepath = output_dir / file_path_or_name
            if local_filepath.exists():
                print(f"✅ 谷歌存储文件已存在本地: {file_path_or_name}")
                return file_path_or_name
            
            # 需要从谷歌存储下载
            if not uri:
                raise Exception(f"谷歌存储文件缺少URI: {file_path_or_name}")
            
            print(f"📥 开始从谷歌存储下载文件: {file_path_or_name}")
            print(f"📋 URI: {uri}")
            
            # 从URI中提取文件ID
            # URI格式: https://generativelanguage.googleapis.com/v1beta/files/8kxw2l3kmzkh
            # 或者: files/8kxw2l3kmzkh
            file_id = None
            if '/files/' in uri:
                file_id = uri.split('/files/')[-1]
            elif uri.startswith('files/'):
                file_id = uri.replace('files/', '')
            
            if not file_id:
                raise Exception(f"无法从URI中提取文件ID: {uri}")
            
            # 使用Google Generative AI API下载文件
            api_key = 'AIzaSyBWj4raKG-ayYkKOVP9eHSdpZO7oT7TuWo'
            download_url = f'https://generativelanguage.googleapis.com/v1beta/files/{file_id}?key={api_key}&alt=media'
            
            # 下载文件
            print(f"📥 下载中: {uri} -> {local_filepath}")
            # 配置代理（如果设置了）
            proxies = {}
            if HTTP_PROXY or HTTPS_PROXY:
                if HTTP_PROXY:
                    proxies['http'] = HTTP_PROXY
                if HTTPS_PROXY:
                    proxies['https'] = HTTPS_PROXY
                elif HTTP_PROXY:
                    proxies['https'] = HTTP_PROXY
                print(f"🌐 使用代理下载: {proxies}")
            response = requests.get(download_url, stream=True, timeout=600, proxies=proxies, verify=False)  # 10分钟超时，禁用SSL验证
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            if total_size > 0:
                print(f"📦 文件大小: {total_size / (1024*1024):.2f} MB")
            
            # 写入文件
            downloaded_size = 0
            with open(local_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            if downloaded_size % (10 * 1024 * 1024) == 0:  # 每10MB打印一次
                                print(f"📥 下载进度: {progress:.1f}% ({downloaded_size / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")
            
            print(f"✅ 谷歌存储文件下载完成: {file_path_or_name} ({downloaded_size / (1024*1024):.2f} MB)")
            return file_path_or_name
            
    except Exception as e:
        print(f"❌ 下载谷歌存储文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"从谷歌存储下载文件失败: {str(e)}")


@app.route('/postVideo', methods=['POST'])
def postVideo():
    try:
        # 获取JSON数据
        data = request.get_json()

        # 从JSON数据中提取fileList和accountList
        file_list = data.get('fileList', [])
        account_list = data.get('accountList', [])
        type = data.get('type')
        title = data.get('title')
        tags = data.get('tags')
        content = data.get('content', '') or data.get('desc', '')  # 支持content和desc两种字段名
        category = data.get('category')
        enableTimer = data.get('enableTimer')
        if category == 0:
            category = None
        productLink = data.get('productLink', '')
        productTitle = data.get('productTitle', '')
        thumbnail_path = data.get('thumbnail', '')
        is_draft = data.get('isDraft', False)  # 新增参数：是否保存为草稿

        videos_per_day = data.get('videosPerDay')
        daily_times = data.get('dailyTimes')
        start_days = data.get('startDays')
        
        # 处理fileList：如果是URL或谷歌存储文件，先下载到本地
        processed_file_list = []
        downloaded_files = []  # 记录下载的文件，用于后续清理（可选）
        
        for file_item in file_list:
            # 判断是否是URL（http或https开头）
            if isinstance(file_item, str) and (file_item.startswith('http://') or file_item.startswith('https://')):
                print(f"🔗 检测到URL格式的视频: {file_item}")
                try:
                    # 下载视频到本地
                    local_filename = download_video_from_url(file_item)
                    processed_file_list.append(local_filename)
                    downloaded_files.append(local_filename)
                    print(f"✅ URL视频已下载并添加到发布列表: {local_filename}")
                except Exception as e:
                    print(f"❌ 下载URL视频失败: {str(e)}")
                    raise Exception(f"下载视频失败: {str(e)}")
            else:
                # 检查是否是谷歌存储文件，如果是则先下载到本地
                try:
                    print(f"📁 检查文件: {file_item}")
                    local_filename = download_google_storage_file(file_item)
                    processed_file_list.append(local_filename)
                    # 如果文件被下载，记录到下载列表
                    if local_filename in downloaded_files or file_item != local_filename:
                        downloaded_files.append(local_filename)
                    print(f"✅ 文件处理完成: {local_filename}")
                except FileNotFoundError as e:
                    # 文件不存在，抛出错误
                    print(f"❌ 文件不存在: {str(e)}")
                    raise Exception(f"文件不存在: {str(e)}")
                except Exception as e:
                    # 其他错误（可能是下载谷歌存储文件失败）
                    print(f"❌ 处理文件失败: {str(e)}")
                    raise Exception(f"处理文件失败: {str(e)}")
        
        # 打印处理后的文件列表
        print("=" * 50)
        print("[postVideo] 处理后的文件列表:", processed_file_list)
        print("[postVideo] 账号列表:", account_list)
        print("[postVideo] 平台类型 (type):", type)
        print("[postVideo] 标题:", title)
        print("[postVideo] 标签:", tags)
        print("[postVideo] 定时发布:", enableTimer)
        print("=" * 50)
        
        # 验证处理后的文件是否存在
        for file_item in processed_file_list:
            # 检查文件是否存在于 videoFile 目录
            video_file_path = Path(BASE_DIR / "videoFile" / file_item)
            if not video_file_path.exists():
                print(f"⚠️ [postVideo] 警告：文件不存在于 videoFile 目录: {video_file_path}")
                # 尝试其他目录
                media_file_path = Path(BASE_DIR / "media" / file_item)
                root_file_path = Path(BASE_DIR / file_item)
                if media_file_path.exists():
                    print(f"✅ [postVideo] 文件存在于 media 目录: {media_file_path}")
                elif root_file_path.exists():
                    print(f"✅ [postVideo] 文件存在于根目录: {root_file_path}")
                else:
                    print(f"❌ [postVideo] 文件在所有目录都不存在: {file_item}")
        
        # 执行发布任务（使用处理后的文件列表）
        if type == 1:
            post_video_xhs(title, processed_file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                              start_days, content=content)
        elif type == 2:
            post_video_tencent(title, processed_file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                              start_days, is_draft)
        elif type == 3:
            post_video_DouYin(title, processed_file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                      start_days, thumbnail_path, productLink, productTitle)
        elif type == 4:
            post_video_ks(title, processed_file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                      start_days)
        
        # 返回响应给客户端
        return jsonify(
            {
                "code": 200,
                "msg": "发布任务已提交",
                "data": None
            }), 200
    except Exception as e:
        print(f"发布视频时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(
            {
                "code": 500,
                "msg": f"发布失败: {str(e)}",
                "data": None
            }), 500


@app.route('/postImageText', methods=['POST'])
def postImageText():
    """小红书图文自动化发布接口"""
    try:
        # 获取JSON数据
        data = request.get_json()

        # 从JSON数据中提取参数
        image_list = data.get('imageList', [])  # 图片文件列表
        account_list = data.get('accountList', [])  # 账号列表
        title = data.get('title', '')  # 标题
        content = data.get('content', '')  # 内容/描述
        tags = data.get('tags', [])  # 标签列表
        enableTimer = data.get('enableTimer', False)  # 是否启用定时发布
        images_per_day = data.get('imagesPerDay', 1)  # 每天发布图文数
        daily_times = data.get('dailyTimes', [])  # 每日发布时间
        start_days = data.get('startDays', 0)  # 开始天数

        # 参数验证
        if not image_list:
            return jsonify({
                "code": 400,
                "msg": "图片列表不能为空",
                "data": None
            }), 400

        if not account_list:
            return jsonify({
                "code": 400,
                "msg": "账号列表不能为空",
                "data": None
            }), 400

        if not title:
            return jsonify({
                "code": 400,
                "msg": "标题不能为空",
                "data": None
            }), 400

        # 打印获取到的数据
        print("=" * 50)
        print("[postImageText] 接收到的数据:")
        print("Image List:", image_list)
        print("Account List:", account_list)
        print("Title:", title)
        print("Content:", content)
        print("Content Length:", len(content) if content else 0)
        print("Content Is Empty:", not content or not content.strip())
        print("Tags:", tags)
        print("Enable Timer:", enableTimer)
        print("=" * 50)

        # 执行发布任务
        post_image_text_xhs(
            title=title,
            content=content,
            image_files=image_list,
            tags=tags,
            account_file=account_list,
            enableTimer=enableTimer,
            images_per_day=images_per_day,
            daily_times=daily_times,
            start_days=start_days
        )

        # 返回响应给客户端
        return jsonify({
            "code": 200,
            "msg": "图文发布任务已提交",
            "data": None
        }), 200
    except Exception as e:
        print(f"发布图文时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"发布失败: {str(e)}",
            "data": None
        }), 500


@app.route('/updateUserinfo', methods=['POST'])
def updateUserinfo():
    # 获取JSON数据
    data = request.get_json()

    # 从JSON数据中提取 type 和 userName
    user_id = data.get('id')
    type = data.get('type')
    userName = data.get('userName')
    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 更新数据库记录
            cursor.execute('''
                           UPDATE user_info
                           SET type     = ?,
                               userName = ?
                           WHERE id = ?;
                           ''', (type, userName, user_id))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "account update successfully",
            "data": None
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("update failed!"),
            "data": None
        }), 500

@app.route('/postVideoBatch', methods=['POST'])
def postVideoBatch():
    data_list = request.get_json()

    if not isinstance(data_list, list):
        return jsonify({"error": "Expected a JSON array"}), 400
    for data in data_list:
        # 从JSON数据中提取fileList和accountList
        file_list = data.get('fileList', [])
        account_list = data.get('accountList', [])
        type = data.get('type')
        title = data.get('title')
        tags = data.get('tags')
        category = data.get('category')
        enableTimer = data.get('enableTimer')
        if category == 0:
            category = None
        productLink = data.get('productLink', '')
        productTitle = data.get('productTitle', '')

        videos_per_day = data.get('videosPerDay')
        daily_times = data.get('dailyTimes')
        start_days = data.get('startDays')
        # 打印获取到的数据（仅作为示例）
        print("File List:", file_list)
        print("Account List:", account_list)
        if type == 1:
            return
        elif type == 2:
            post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                              start_days)
        elif type == 3:
            post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                      start_days, productLink, productTitle)
        elif type == 4:
            post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                      start_days)
    # 返回响应给客户端
    return jsonify(
        {
            "code": 200,
            "msg": None,
            "data": None
        }), 200

# Cookie文件上传API
@app.route('/uploadCookie', methods=['POST'])
def upload_cookie():
    try:
        if 'file' not in request.files:
            return jsonify({
                "code": 500,
                "msg": "没有找到Cookie文件",
                "data": None
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "code": 500,
                "msg": "Cookie文件名不能为空",
                "data": None
            }), 400

        if not file.filename.endswith('.json'):
            return jsonify({
                "code": 500,
                "msg": "Cookie文件必须是JSON格式",
                "data": None
            }), 400

        # 获取账号信息
        account_id = request.form.get('id')
        platform = request.form.get('platform')

        if not account_id or not platform:
            return jsonify({
                "code": 500,
                "msg": "缺少账号ID或平台信息",
                "data": None
            }), 400

        # 从数据库获取账号的文件路径
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT filePath FROM user_info WHERE id = ?', (account_id,))
            result = cursor.fetchone()

        if not result:
            return jsonify({
                "code": 500,
                "msg": "账号不存在",
                "data": None
            }), 404

        # 保存上传的Cookie文件到对应路径
        cookie_file_path = Path(BASE_DIR / "cookiesFile" / result['filePath'])
        cookie_file_path.parent.mkdir(parents=True, exist_ok=True)

        file.save(str(cookie_file_path))

        # 更新数据库中的账号信息（可选，比如更新更新时间）
        # 这里可以根据需要添加额外的处理逻辑

        return jsonify({
            "code": 200,
            "msg": "Cookie文件上传成功",
            "data": None
        }), 200

    except Exception as e:
        print(f"上传Cookie文件时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"上传Cookie文件失败: {str(e)}",
            "data": None
        }), 500


# Cookie文件下载API
@app.route('/downloadCookie', methods=['GET'])
def download_cookie():
    try:
        file_path = request.args.get('filePath')
        if not file_path:
            return jsonify({
                "code": 500,
                "msg": "缺少文件路径参数",
                "data": None
            }), 400

        # 验证文件路径的安全性，防止路径遍历攻击
        cookie_file_path = Path(BASE_DIR / "cookiesFile" / file_path).resolve()
        base_path = Path(BASE_DIR / "cookiesFile").resolve()

        if not cookie_file_path.is_relative_to(base_path):
            return jsonify({
                "code": 500,
                "msg": "非法文件路径",
                "data": None
            }), 400

        if not cookie_file_path.exists():
            return jsonify({
                "code": 500,
                "msg": "Cookie文件不存在",
                "data": None
            }), 404

        # 返回文件
        return send_from_directory(
            directory=str(cookie_file_path.parent),
            path=cookie_file_path.name,
            as_attachment=True
        )

    except Exception as e:
        print(f"下载Cookie文件时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"下载Cookie文件失败: {str(e)}",
            "data": None
        }), 500


# 包装函数：在线程中运行异步函数
def run_async_function(type, id, status_queue, browser_context_storage=None, automation_tool='playwright'):
    print(f"[异步任务] 开始执行登录任务 - type: {type}, id: {repr(id)}, automation_tool: {automation_tool}", flush=True)
    try:
        if type == '1':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(xiaohongshu_cookie_gen(id, status_queue))
            loop.close()
        elif type == '2':
            # 视频号登录：使用 myUtils.login.get_tencent_cookie（与官方仓库保持一致）
            import os
            original_tool = os.environ.get('AUTOMATION_TOOL')
            os.environ['AUTOMATION_TOOL'] = automation_tool
            print(f"[异步任务] 为本次登录设置自动化工具: {automation_tool.upper()}", flush=True)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # 当前统一使用 Playwright 版本实现，不再依赖 login_wrapper
            loop.run_until_complete(get_tencent_cookie(id, status_queue))
            loop.close()
            
            # 恢复原来的环境变量
            if original_tool is not None:
                os.environ['AUTOMATION_TOOL'] = original_tool
            elif 'AUTOMATION_TOOL' in os.environ:
                del os.environ['AUTOMATION_TOOL']
        elif type == '3':
            print(f"[异步任务] 调用抖音登录函数，传递账号名称: {repr(id)}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(douyin_cookie_gen(id, status_queue))
            loop.close()
            print(f"[异步任务] 抖音登录任务完成")
        elif type == '4':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(get_ks_cookie(id, status_queue))
            loop.close()
        elif type == '5':
            print(f"[异步任务] 调用B站登录函数，传递账号名称: {repr(id)}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bilibili_cookie_gen(id, status_queue))
            loop.close()
            print(f"[异步任务] B站登录任务完成")
    except Exception as e:
        print(f"[异步任务] 登录任务执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        status_queue.put("500")

# SSE 流生成器函数
def sse_stream(status_queue):
    print(f"[SSE流] 开始SSE流生成器 - 接口: /login (SSE流)")
    final_status_sent = False
    last_heartbeat = time.time()
    heartbeat_interval = 15  # 每15秒发送一次心跳
    
    while True:
        current_time = time.time()
        
        # 发送心跳保持连接（每15秒一次）
        if current_time - last_heartbeat >= heartbeat_interval:
            try:
                yield f": heartbeat\n\n"  # SSE注释，用于保持连接
                last_heartbeat = current_time
                print(f"[SSE流] 发送心跳保持连接")
            except Exception as e:
                print(f"[SSE流] 发送心跳失败: {e}")
                break
        
        if not status_queue.empty():
            msg = status_queue.get()
            msg_str = str(msg)
            print(f"[SSE流] 从队列获取消息: {msg_str[:100] if len(msg_str) > 100 else msg_str}")
            
            # 检查是否是Cookie数据
            if msg_str.startswith("cookie:"):
                cookie_data_str = msg_str[7:]  # 去掉 'cookie:' 前缀
                print(f"[SSE流] 🍪 检测到Cookie数据，准备通过SSE流发送")
                print(f"[SSE流] Cookie数据大小: {len(cookie_data_str)} 字节")
                try:
                    import json
                    cookie_data = json.loads(cookie_data_str)
                    print(f"[SSE流] Cookie数据详情 - 账号: {cookie_data.get('userName', 'N/A')}, 文件路径: {cookie_data.get('filePath', 'N/A')}, Cookie数量: {len(cookie_data.get('cookies', []))}")
                except:
                    print(f"[SSE流] ⚠️ 无法解析Cookie数据JSON")
            
            try:
                yield f"data: {msg}\n\n"
                
                # 如果是Cookie数据，记录发送成功
                if msg_str.startswith("cookie:"):
                    print(f"[SSE流] ✅ Cookie数据已通过SSE流发送给客户端")
                
                # 如果收到最终状态码（200或500），标记已发送，但继续等待一段时间确保前端收到
                if msg_str == "200" or msg_str == "500":
                    print(f"[SSE流] 收到最终状态码 {msg_str}，已发送给客户端")
                    final_status_sent = True
                    # 继续等待一小段时间，确保消息被发送，然后结束
                    time.sleep(0.5)
                    break
            except Exception as e:
                print(f"[SSE流] 发送消息失败: {e}")
                if msg_str.startswith("cookie:"):
                    print(f"[SSE流] ❌ Cookie数据发送失败: {e}")
                break
        else:
            # 如果已经发送了最终状态码，且队列为空，可以结束
            if final_status_sent:
                print(f"[SSE流] 最终状态码已发送，队列为空，结束SSE流")
                break
            # 避免 CPU 占满，但不要阻塞太久，以便及时发送心跳
            time.sleep(0.5)

# 图文生成webhook代理接口
@app.route('/generateImageText', methods=['POST'])
def generate_image_text():
    """
    代理转发图文生成请求到webhook
    解决前端CORS跨域问题
    """
    try:
        # 获取前端发送的数据
        data = request.get_json()
        
        # webhook目标地址（测试模式 - 图文内容生成）
        webhook_url = 'https://aicode.ltd/webhook-test/c155e570-faf5-4351-b1bd-7b908cf6db36'
        
        # 转发POST请求到webhook（增加超时时间，因为AI生成需要较长时间）
        response = requests.post(
            webhook_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=120  # 120秒超时，适应AI生成内容的耗时
        )
        
        # 返回webhook的响应
        try:
            result = response.json()
        except:
            result = {'message': '请求成功', 'status': response.status_code}
        
        return jsonify({
            'code': 200,
            'data': result,
            'msg': '成功'
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': '请求超时，请重试'
        }), 500
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'请求失败: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器错误: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=5409)

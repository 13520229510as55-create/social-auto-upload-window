# -*- coding: utf-8 -*-
"""
微信公众号服务模块
处理微信读书账号管理、公众号订阅等功能
"""

import asyncio
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

import httpx
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models import WechatAccount, WechatFeed, WechatArticle
from database.db_session import get_async_engine, get_session
import os

# 微信读书平台 API 基础 URL
PLATFORM_URL = "https://weread.111965.xyz"

# 账号状态常量
STATUS_INVALID = 0  # 失效
STATUS_ENABLE = 1   # 启用
STATUS_DISABLE = 2   # 禁用

# 每日小黑屋账号（按日期存储）
blocked_accounts_map: Dict[str, List[str]] = {}


class WechatService:
    """微信公众号服务类"""
    
    def __init__(self):
        self.platform_url = PLATFORM_URL
        self.update_delay_time = 60  # 默认延迟60秒
        self.client = httpx.AsyncClient(
            base_url=self.platform_url,
            timeout=15.0,
            headers={
                'accept': 'application/json',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        # 微信公众号服务使用 MediaCrawler 的数据库配置
        # 如果 SAVE_DATA_OPTION 是 json 或 csv，则使用 sqlite 作为默认数据库
        import config
        save_option = getattr(config, 'SAVE_DATA_OPTION', 'json')
        if save_option in ['json', 'csv']:
            # json/csv 格式不需要数据库，但 wechat 服务需要，所以使用 sqlite
            self.db_type = 'sqlite'
        else:
            # 使用 MediaCrawler 配置的数据库类型
            self.db_type = save_option
    
    def get_today_date(self) -> str:
        """获取今天的日期字符串"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def get_blocked_account_ids(self) -> List[str]:
        """获取今日被禁用的账号ID列表"""
        today = self.get_today_date()
        return blocked_accounts_map.get(today, [])
    
    def remove_blocked_account(self, account_id: str):
        """从黑名单中移除账号"""
        today = self.get_today_date()
        if today in blocked_accounts_map:
            blocked_accounts_map[today] = [
                aid for aid in blocked_accounts_map[today] if aid != account_id
            ]
    
    @asynccontextmanager
    async def _get_wechat_session(self):
        """获取微信公众号服务的数据库会话（使用 MediaCrawler 的数据库配置）"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        from database.models import Base
        
        engine = get_async_engine(self.db_type)
        if not engine:
            # 如果指定的数据库类型不支持，尝试使用 sqlite
            if self.db_type != 'sqlite':
                self.db_type = 'sqlite'
                engine = get_async_engine('sqlite')
            
            if not engine:
                raise Exception('数据库未启用，请先配置数据库（建议在 config/base_config.py 中设置 SAVE_DATA_OPTION 为 sqlite 或 db/mysql）')
        
        # 确保表已创建
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        session = AsyncSessionFactory()
        
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    async def get_available_account(self) -> Optional[WechatAccount]:
        """获取可用的账号"""
        async with self._get_wechat_session() as session:
            
            blocked_ids = self.get_blocked_account_ids()
            
            stmt = select(WechatAccount).where(
                WechatAccount.status == STATUS_ENABLE
            )
            if blocked_ids:
                stmt = stmt.where(~WechatAccount.id.in_(blocked_ids))
            
            result = await session.execute(stmt)
            accounts = result.scalars().all()
            
            if not accounts:
                raise Exception('暂无可用读书账号!')
            
            # 随机选择一个账号
            import random
            return random.choice(accounts)
    
    async def create_login_url(self) -> Dict:
        """创建登录URL，返回二维码信息"""
        try:
            response = await self.client.get('/api/v2/login/platform')
            return response.json()
        except Exception as e:
            raise Exception(f"创建登录URL失败: {str(e)}")
    
    async def get_login_result(self, uuid: str) -> Dict:
        """获取登录结果"""
        try:
            response = await self.client.get(
                f'/api/v2/login/platform/{uuid}',
                timeout=120.0
            )
            return response.json()
        except Exception as e:
            raise Exception(f"获取登录结果失败: {str(e)}")
    
    async def add_account(self, account_id: str, name: str, token: str, status: int = STATUS_ENABLE) -> WechatAccount:
        """添加或更新账号"""
        async with self._get_wechat_session() as session:
            now = int(time.time())
            
            # 检查账号是否存在
            stmt = select(WechatAccount).where(WechatAccount.id == account_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if account:
                # 更新
                account.token = token
                account.name = name
                account.status = status
                account.updated_at = now
            else:
                # 创建
                account = WechatAccount(
                    id=account_id,
                    token=token,
                    name=name,
                    status=status,
                    created_at=now,
                    updated_at=now
                )
                session.add(account)
            
            await session.commit()
            await session.refresh(account)
            
            # 从黑名单移除
            self.remove_blocked_account(account_id)
            
            return account
    
    async def list_accounts(self) -> List[Dict]:
        """获取账号列表"""
        try:
            async with self._get_wechat_session() as session:
                stmt = select(WechatAccount)
                result = await session.execute(stmt)
                accounts = result.scalars().all()
                
                blocked_ids = self.get_blocked_account_ids()
                
                return [
                    {
                        'id': acc.id,
                        'name': acc.name,
                        'status': acc.status,
                        'is_blocked': acc.id in blocked_ids,
                        'created_at': acc.created_at,
                        'updated_at': acc.updated_at
                    }
                    for acc in accounts
                ]
        except Exception:
            return []
    
    async def update_account_status(self, account_id: str, status: int) -> bool:
        """更新账号状态"""
        async with self._get_wechat_session() as session:
            stmt = update(WechatAccount).where(
                WechatAccount.id == account_id
            ).values(status=status, updated_at=int(time.time()))
            
            await session.execute(stmt)
            await session.commit()
            
            if status == STATUS_ENABLE:
                self.remove_blocked_account(account_id)
            
            return True
    
    async def delete_account(self, account_id: str) -> bool:
        """删除账号"""
        async with self._get_wechat_session() as session:
            stmt = delete(WechatAccount).where(WechatAccount.id == account_id)
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def get_mp_info(self, wxs_link: str) -> List[Dict]:
        """通过分享链接获取公众号信息"""
        account = await self.get_available_account()
        
        try:
            response = await self.client.post(
                '/api/v2/platform/wxs2mp',
                json={'url': wxs_link.strip()},
                headers={
                    'xid': account.id,
                    'Authorization': f'Bearer {account.token}'
                }
            )
            return response.json()
        except Exception as e:
            # 如果是401错误，标记账号失效
            if '401' in str(e) or 'WeReadError401' in str(e):
                await self.update_account_status(account.id, STATUS_INVALID)
            # 如果是429错误，加入黑名单
            elif '429' in str(e) or 'WeReadError429' in str(e):
                today = self.get_today_date()
                if today not in blocked_accounts_map:
                    blocked_accounts_map[today] = []
                if account.id not in blocked_accounts_map[today]:
                    blocked_accounts_map[today].append(account.id)
            raise Exception(f"获取公众号信息失败: {str(e)}")
    
    async def get_mp_articles(self, mp_id: str, page: int = 1, retry_count: int = 3) -> List[Dict]:
        """获取公众号文章列表"""
        account = await self.get_available_account()
        
        try:
            response = await self.client.get(
                f'/api/v2/platform/mps/{mp_id}/articles',
                params={'page': page},
                headers={
                    'xid': account.id,
                    'Authorization': f'Bearer {account.token}'
                }
            )
            return response.json()
        except Exception as e:
            if retry_count > 0:
                await asyncio.sleep(2)
                return await self.get_mp_articles(mp_id, page, retry_count - 1)
            
            # 错误处理
            if '401' in str(e) or 'WeReadError401' in str(e):
                await self.update_account_status(account.id, STATUS_INVALID)
            elif '429' in str(e) or 'WeReadError429' in str(e):
                today = self.get_today_date()
                if today not in blocked_accounts_map:
                    blocked_accounts_map[today] = []
                if account.id not in blocked_accounts_map[today]:
                    blocked_accounts_map[today].append(account.id)
            
            raise Exception(f"获取文章列表失败: {str(e)}")
    
    async def add_feed(self, feed_id: str, mp_name: str, mp_cover: str, 
                      mp_intro: str, update_time: int, status: int = STATUS_ENABLE) -> WechatFeed:
        """添加或更新订阅源"""
        async with self._get_wechat_session() as session:
            now = int(time.time())
            
            stmt = select(WechatFeed).where(WechatFeed.id == feed_id)
            result = await session.execute(stmt)
            feed = result.scalar_one_or_none()
            
            if feed:
                feed.mp_name = mp_name
                feed.mp_cover = mp_cover
                feed.mp_intro = mp_intro
                feed.update_time = update_time
                feed.status = status
                feed.updated_at = now
            else:
                feed = WechatFeed(
                    id=feed_id,
                    mp_name=mp_name,
                    mp_cover=mp_cover,
                    mp_intro=mp_intro,
                    update_time=update_time,
                    status=status,
                    sync_time=0,
                    has_history=1,
                    created_at=now,
                    updated_at=now
                )
                session.add(feed)
            
            await session.commit()
            await session.refresh(feed)
            return feed
    
    async def list_feeds(self) -> List[Dict]:
        """获取订阅源列表"""
        try:
            async with self._get_wechat_session() as session:
                stmt = select(WechatFeed).order_by(WechatFeed.created_at.desc())
                result = await session.execute(stmt)
                feeds = result.scalars().all()
                
                return [
                    {
                        'id': feed.id,
                        'mp_name': feed.mp_name,
                        'mp_cover': feed.mp_cover,
                        'mp_intro': feed.mp_intro,
                        'status': feed.status,
                        'sync_time': feed.sync_time,
                        'update_time': feed.update_time,
                        'has_history': feed.has_history,
                        'created_at': feed.created_at,
                        'updated_at': feed.updated_at
                    }
                    for feed in feeds
                ]
        except Exception:
            return []
    
    async def refresh_mp_articles(self, mp_id: str, page: int = 1) -> Dict:
        """刷新公众号文章"""
        articles = await self.get_mp_articles(mp_id, page)
        
        if articles:
            async with self._get_wechat_session() as session:
                now = int(time.time())
                
                for article_data in articles:
                    article_id = article_data['id']
                    stmt = select(WechatArticle).where(WechatArticle.id == article_id)
                    result = await session.execute(stmt)
                    article = result.scalar_one_or_none()
                    
                    if article:
                        article.title = article_data['title']
                        article.publish_time = article_data['publishTime']
                        article.updated_at = now
                    else:
                        article = WechatArticle(
                            id=article_id,
                            mp_id=mp_id,
                            title=article_data['title'],
                            pic_url=article_data.get('picUrl', ''),
                            publish_time=article_data['publishTime'],
                            created_at=now,
                            updated_at=now
                        )
                        session.add(article)
                
                await session.commit()
        
        # 更新同步时间
        has_history = 1 if len(articles) >= 20 else 0  # 默认每页20条
        
        async with self._get_wechat_session() as session:
            stmt = update(WechatFeed).where(
                WechatFeed.id == mp_id
            ).values(
                sync_time=int(time.time()),
                has_history=has_history,
                updated_at=int(time.time())
            )
            await session.execute(stmt)
            await session.commit()
        
        return {'has_history': has_history}
    
    async def list_articles(self, mp_id: Optional[str] = None, limit: int = 20, 
                           offset: int = 0) -> List[Dict]:
        """获取文章列表"""
        try:
            async with self._get_wechat_session() as session:
                stmt = select(WechatArticle)
                
                if mp_id:
                    stmt = stmt.where(WechatArticle.mp_id == mp_id)
                
                stmt = stmt.order_by(WechatArticle.publish_time.desc())
                stmt = stmt.limit(limit).offset(offset)
                
                result = await session.execute(stmt)
                articles = result.scalars().all()
                
                return [
                    {
                        'id': art.id,
                        'mp_id': art.mp_id,
                        'title': art.title,
                        'pic_url': art.pic_url,
                        'publish_time': art.publish_time,
                        'created_at': art.created_at,
                        'updated_at': art.updated_at
                    }
                    for art in articles
                ]
        except Exception:
            return []
    
    async def update_feed_status(self, feed_id: str, status: int) -> bool:
        """更新订阅源状态"""
        async with self._get_wechat_session() as session:
            stmt = update(WechatFeed).where(
                WechatFeed.id == feed_id
            ).values(status=status, updated_at=int(time.time()))
            
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def delete_feed(self, feed_id: str) -> bool:
        """删除订阅源"""
        async with self._get_wechat_session() as session:
            stmt = delete(WechatFeed).where(WechatFeed.id == feed_id)
            await session.execute(stmt)
            await session.commit()
            return True
    
    # 正在获取历史文章的公众号信息
    in_progress_history_mp = {'id': '', 'page': 1}
    
    async def get_history_mp_articles(self, mp_id: str) -> Dict:
        """获取历史文章（分页获取）"""
        if self.in_progress_history_mp['id'] == mp_id:
            # 停止获取
            self.in_progress_history_mp = {'id': '', 'page': 1}
            return {'status': 'stopped'}
        
        # 检查是否有历史文章
        async with self._get_wechat_session() as session:
            stmt = select(WechatFeed).where(WechatFeed.id == mp_id)
            result = await session.execute(stmt)
            feed = result.scalar_one_or_none()
            
            if not feed:
                raise Exception('订阅源不存在')
            
            if feed.has_history == 0:
                return {'status': 'no_history', 'message': '该订阅源没有更多历史文章'}
        
        # 开始获取历史文章
        self.in_progress_history_mp = {'id': mp_id, 'page': 1}
        
        # 计算起始页码（根据已有文章数量）
        async with self._get_wechat_session() as session:
            stmt = select(WechatArticle).where(WechatArticle.mp_id == mp_id)
            result = await session.execute(stmt)
            total_articles = len(result.scalars().all())
            self.in_progress_history_mp['page'] = max(1, (total_articles // 20) + 1)
        
        try:
            # 最多尝试1000次
            max_iterations = 1000
            for i in range(max_iterations):
                if self.in_progress_history_mp['id'] != mp_id:
                    break
                
                page = self.in_progress_history_mp['page']
                result = await self.refresh_mp_articles(mp_id, page)
                
                if result.get('has_history', 0) == 0:
                    # 没有更多历史文章
                    break
                
                self.in_progress_history_mp['page'] += 1
                
                # 延迟，避免请求过快
                await asyncio.sleep(self.update_delay_time)
        finally:
            if self.in_progress_history_mp['id'] == mp_id:
                self.in_progress_history_mp = {'id': '', 'page': 1}
        
        return {'status': 'completed'}
    
    def get_in_progress_history_mp(self) -> Dict:
        """获取正在获取历史文章的公众号信息"""
        return self.in_progress_history_mp.copy()


# 创建全局服务实例
wechat_service = WechatService()


from DatabaseManager import *
from pydantic import BaseModel
from typing import List, Dict, Any

# 定義公告數據模型類
class BulletinRaw(BaseModel):
    rawid: int
    publisher: str
    title: str
    url: str
    content: str
    addtime: datetime
    processstatus: bool
        
# 定義公告管理類，繼承自數據庫管理類
class BulletinManager(DatabaseManager):
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Config should be a dictionary")
        super().__init__(config)  # 調用父類的初始化方法

    
    def get_unprocessed_bulletins(self) -> List[BulletinRaw]:
        query = """
            SELECT * FROM bulletinraw
            WHERE processstatus = false
        """
        data = self.execute_query(query)
        return [BulletinRaw(**row) for row in data]

    def update_bulletin_status(self) -> None:
        query = """
            UPDATE bulletinraw
            SET processstatus = true
            WHERE processstatus = false
        """
        self.execute_non_query(query)
        
    def save_bulletin(self, post: Dict[str, Any]) -> None:
        query = """
            INSERT INTO bulletinraw (publisher, title, url, content)
                VALUES (%s, %s, %s, %s)
            ON CONFLICT (title, url) DO NOTHING
            """
        self.execute_non_query(query, (post['publisher'], 
                                             post['title'], 
                                             post['url'], 
                                             post['content']))
    def reset_bulletin_status(self, count: int) -> None:
        """將指定數量的公告標記為未處理"""
        query = """
            UPDATE bulletinraw
            SET processstatus = false
            WHERE rawid IN (
                SELECT rawid FROM bulletinraw
                WHERE processstatus = true
                LIMIT %s
            )
        """
        self.execute_non_query(query, (count,))

class UserManager(DatabaseManager):
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("配置應為字典類型")
        super().__init__(config)  # 調用父類的初始化方法

    def add_user(self, username: str, chatid: str) -> None:
        """添加一個新用戶"""
        query = """
            INSERT INTO users (username, chatid)
            VALUES (%s, %s)
            ON CONFLICT (chatid) DO NOTHING
        """
        self.execute_non_query(query, (username, chatid))

    def get_user_by_chatid(self, chatid: str) -> Dict[str, Any]:
        """根據 chatid 查詢用戶"""
        query = """
            SELECT * FROM users WHERE chatid = %s
        """
        result = self.execute_query(query, (chatid,))
        return result[0] if result else None

    def delete_user(self, chatid: str) -> None:
        """根據 chatid 刪除用戶"""
        query = """
            DELETE FROM users WHERE chatid = %s
        """
        self.execute_non_query(query, (chatid,))

    def list_all_users(self) -> List[Dict[str, Any]]:
        """列出所有用戶"""
        query = """
            SELECT * FROM users
        """
        return self.execute_query(query)
    def user_exists(self, chatid: str) -> bool:
        """檢查用戶是否存在"""
        query = """
            SELECT 1 FROM users WHERE chatid = %s
        """
        result = self.execute_query(query, (chatid,))
        return bool(result)  # 如果 result 非空，返回 True，否則返回 False


class SubscriptionManager(DatabaseManager):
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Config should be a dictionary")
        super().__init__(config)  

    def add_subscription(self, chatid: str, topic_name: str) -> None:
        user_manager = UserManager(db_config)
        if not user_manager.user_exists(chatid):
            user_manager.add_user('testuser',chatid)

        """add new sub"""
        query = """
            INSERT INTO subscription (chatid, topic_name)
            VALUES (%s, %s)
            ON CONFLICT (chatid, topic_name) DO NOTHING
        """
        self.execute_non_query(query, (chatid, topic_name))

    def delete_subscription(self, chatid: str, topic_name: str) -> None:
        """delete sub"""
        query = """
            DELETE FROM subscription
            WHERE chatid = %s AND topic_name = %s
        """
        self.execute_non_query(query, (chatid, topic_name))

    def get_user_subscriptions(self, chatid: str) -> List[Dict[str, Any]]:
        """get spec user sub """
        query = """
            SELECT topic_name, join_date
            FROM subscription
            WHERE chatid = %s
        """
        data = self.execute_query(query, (chatid,))
        return [{'topic_name': row['topic_name'], 'join_date': row['join_date']} for row in data]

    def get_all_subscriptions(self) -> List[Dict[str, Any]]:
        """get all sub"""
        query = """
            SELECT chatid, topic_name, join_date
            FROM subscription
        """
        data = self.execute_query(query)
        return [{'chatid': row['chatid'], 'topic_name': row['topic_name'], 'join_date': row['join_date']} for row in data]


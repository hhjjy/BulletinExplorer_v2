from decimal import Decimal
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import BaseModel
from urllib.parse import urlparse
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from telegram.constants import ParseMode
from telegram import  Chat, ChatMember, ChatMemberUpdated, ForceReply, Update, Bot 
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Updater, Application, ContextTypes, filters, ChatMemberHandler
import json, os, requests, psycopg2, traceback, time, telegram, copy, pprint, asyncio, functools

db_config = {
    'dbname': 'mydb',
    'user': 'admin',
    'password': '12345',
    'host': '127.0.0.1',
    'port': '5432'
}

NTUST_LANG_URL = "https://lc.ntust.edu.tw/p/403-1070-1053-1.php?Lang=zh-tw"
NTUST_INSIDE_URL = "https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php?Lang=zh-tw"
NTUST_OUTSIDE_URL = "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw"

class Scraper(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrape(self):
        pass

# 靜態類別 輸入網址轉類別
class ScraperFactory:
    @staticmethod
    def get_scraper(url):
        # 根據不同的網址返回不同的爬蟲實例
        if "bulletin.ntust.edu.tw" in url:
            return NTUSTBulletinScraper(url)
        elif "lc.ntust.edu.tw" in url:
            return NTUSTLanguageCenterScraper(url)
        elif "www.ntust.edu.tw" in url:
            return NTUSTMajorAnnouncementScraper(url)
        else:
            raise ValueError(f"No scraper found for the given URL: {url}")

# 台科大公佈欄爬蟲
class NTUSTBulletinScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find("table")# 找table 標籤 
        thead = table.find("thead")# 從table 找第一個匹配的
        tbody = table.find("tbody")# 從table找第一個匹配的
        # # Process the table one row at a time
        i = 1
        
        for row in tbody.find_all("tr"):
            data_row = []       
            publisher = "台科大" + row.find("td",{"data-th":"發佈單位"}).get_text(strip=True)
            title = row.find("td",{"data-th":"標題"}).get_text(strip=True)
            a_tag = row.find("a")
            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
            content = "" # 從url去爬連結內文
            if url != None:
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.content, 'html.parser')
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    content += p.get_text(strip=True)
            yield {"publisher":publisher,"title":title,"url":url,"content":content}

# 台科大語言中心爬蟲
class NTUSTLanguageCenterScraper(Scraper):
    def scrape(self):
        print("Scraping NTUST Language Center...")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 添加針對台科大語言中心的爬蟲邏輯
        divs = soup.find_all('div', attrs={'class': 'mtitle'})
        for tag in divs:
            a_tag = tag.find('a')
            url = a_tag.get('href')
            publisher = "台科大語言中心"
            title = ""
            content = ""
            if url:
                title = a_tag.get_text(strip=True) 
                # 取得標題的內文
                webpage = requests.get(url)
                webpage_soup = BeautifulSoup(webpage.content, 'html.parser')
                div = webpage_soup.find('div',attrs={'class':'mpgdetail'})
                p_tags = div.find_all('p')
                for p in p_tags:
                    content += p.get_text(strip=True)
            yield {"publisher":publisher,"title":title,"url":url,"content":content}  

# 台科大校網公布欄爬蟲
class NTUSTMajorAnnouncementScraper(Scraper):
    def scrape(self):
        print("Scraping NTUST Major Announcements...")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = soup.find_all('div', attrs={'class': 'mtitle'})
        title = ""
        url = ""
        content = ""
        publisher = "台科大主校網"
        for t in titles:
            title = t.get_text(strip=True)
            a_tag = t.find('a')
            url = a_tag.get('href')
            yield {"publisher":"publisher","title":title,"url":url,"content":content}  

def SaveBulletin(data):
    bulletin_manager = BulletinManager(db_config)
    for row in data:
        print(row)
        bulletin_manager.save_bulletin(row)

def scrape(context: ContextTypes.DEFAULT_TYPE) -> None:
    #should add running event
    for url in [NTUST_LANG_URL, NTUST_OUTSIDE_URL]: # NTUST_INSIDE_URL, 
        Scrape = ScraperFactory.get_scraper(url)
        data = Scrape.scrape()
        SaveBulletin(data)
    # Scrape = ScraperFactory.get_scraper(NTUST_INSIDE_URL)
    # data = Scrape.scrape()
    # SaveBulletin(data)

    # Scrape = ScraperFactory.get_scraper(NTUST_LANG_URL)
    # data = Scrape.scrape()
    # SaveBulletin(data)

    # Scrape = ScraperFactory.get_scraper(NTUST_OUTSIDE_URL)
    # data = Scrape.scrape()
    # SaveBulletin(data)

def print_bulletin_data():
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bulletinraw")
        rows = cursor.fetchall()
        
        # 打印每行數據
        for row in rows:
            print(row)
    
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        # error_traceback = traceback.format_exc()
    # finally:
    #     if connection:
    #         cursor.close()
    #         connection.close()

# 測試函數

def handle_db_exceptions(func):
    @functools.wraps(func)psycopg2
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.DatabaseError as e:
            print(f"Database error occurred: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
    return wrapper
    
def debug_info(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 獲取函數名稱
        func_name = func.__name__
        
        # 獲取位置參數和關鍵字參數的名稱和值
        func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
        params = {**dict(zip(func_args, args)), **kwargs}
        
        # 打印函數名稱和參數
        print(f"Executing function: {func_name}")
        print("Parameters:")
        for param_name, param_value in params.items():
            print(f"  {param_name} = {param_value}")
        
        # 執行函數並獲取返回值
        result = func(*args, **kwargs)
        
        # 打印返回值
        print(f"Function {func_name} returned: {result}")
        
        return result
    return wrapper
# 定義數據庫管理類
class DatabaseManager:
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Config should be a dictionary")
        self.config = config
        print(f"DatabaseManager Config: {self.config}")

    @handle_db_exceptions
    def _execute(self, query: str, params: tuple = None, fetch: bool = False):
        print(f"_execute: {self.config}")  # 打印配置以檢查
        connection = psycopg2.connect(**self.config)
        cursor = connection.cursor()
        cursor.execute(query, params)
        if fetch:
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            connection.close()
            return results, columns
        connection.commit()
        cursor.close()
        connection.close()
        return None, None

    @debug_info
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        results, columns = self._execute(query, params, fetch=True)
        if results:
            return [dict(zip(columns, row)) for row in results]
        return []

    def execute_non_query(self, query: str, params: tuple = ()) -> None:
        self._execute(query, params)

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
            """
        self.execute_non_query(query, (post['publisher'], 
                                             post['title'], 
                                             post['url'], 
                                             post['content']))



class SubscriptionManager(DatabaseManager):
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Config should be a dictionary")
        super().__init__(config)  

    def add_subscription(self, chatid: str, topic_name: str) -> None:
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


async def send_new_data(context: ContextTypes.DEFAULT_TYPE) -> None :
    # await context.bot.send_message(chat_id="940229605", text="hi", parse_mode=ParseMode.MARKDOWN_V2)
    # print("send_new_data called with context:", context)
    bulletin_manager = BulletinManager(db_config)
    # 讀資料庫
    data =  bulletin_manager.get_unprocessed_bulletins()
    # print(data)
    # [(1, 'test', 'test', 'test', 'test', datetime.datetime(2024, 6, 20, 15, 24, 47, 957529), False)]
    # 發送資料
    # pprint.pprint(data)

    for i in data:
        # pprint.pprint(i)
        # message = f"[{i.title}]({i.url})"
        # BUG : 目前MARKDOWN內不能包含 - 等特殊字元否則會抱錯 詳細的解法還要看後續升級
        # await context.bot.send_message(chat_id="940229605", text=f"[{i.title}]({i.url})", parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id="940229605", text = i.title ) # 超連結 怎麼做?
        await context.bot.send_message(chat_id="6904184189", text = i.title ) # 超連結 怎麼做?

    update_bulletin_status()
    
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        label_name = update.message.text.split(' ')[1:][0]#chinese not work
    except:
        await update.effective_message.reply_text("Please enter the topic name")
        return
    
    url = get_labelid
    data = {
        "labelname": label_name
    }
    response = requests.post(url, json=data)
    labelid = response.text[1:-1]

    if (labelid == "ul"):#bcs null[1] -> [u]
        await update.effective_message.reply_text("topic not exist")
    else:
        url = add_subscription
        data = {
            "chatid": str(chat_id),
            "labelid": str(labelid)
        }
        response = requests.post(url, json=data)
        await update.effective_message.reply_text("Subscribe topic successfully")


def main() -> None:
    chatid = "940229605"
    TOKEN = "6588891089:AAETxqnSzmn7WBqBsHQ5tPcBYuiK36Dc1a8"
    # application = Application.builder().token(TOKEN).post_init(post_init).post_stop(post_stop).build()
    application = Application.builder().token(TOKEN).build()
    job_queue = application.job_queue
    # job_minute = job_queue.run_repeating(update_user, interval=30, first=3)
    # job_minute = job_queue.run_repeating(llm, interval=15, first=3)
    job_minute = job_queue.run_repeating(send_new_data, interval=20, first=10)
    job_minute = job_queue.run_repeating(scrape, interval=15, first=3)

    # accuout 
    # userid 
    # labelids  
    # 
    # application.add_handler(CommandHandler(["start", "help"], start))
    # application.add_handler(CommandHandler("help", help))
    # application.add_handler(CommandHandler("search", search))
    # application.add_handler(CommandHandler("whereami", whereami))
    application.add_handler(CommandHandler("subscribe", subscribe))
    # application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    # application.add_handler(CommandHandler("list", list)) 

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__ == '__main__':
    manager = SubscriptionManager(db_config)
    # main()
    # bulletin_manager = BulletinManager(db_config)

    # # 獲取未處理的公告
    # unprocessed_bulletins = bulletin_manager.get_unprocessed_bulletins()
    # for bulletin in unprocessed_bulletins:
    #     pprint.pprint(bulletin)

    # 更新公告狀態
    # bulletin_manager.update_bulletin_status()

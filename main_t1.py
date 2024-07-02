# Abstract base class for scrapers
class Scraper(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrape(self):
        pass

# Decorator for saving bulletin data
def SaveBulletin(func):
    def wrapper(self, *args, **kwargs):
        data_generator = func(self, *args, **kwargs)
        for data in data_generator:
            # Here you would implement saving logic, for example:
            print("Saving bulletin data:", data)
            # Replace the print statement with actual saving code
    return wrapper

# Combined scraper class for NTUST
class NTUSTCombinedScraper(Scraper):
    def __init__(self, url):
        super().__init__(url)

    @SaveBulletin
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        if "bulletin.ntust.edu.tw" in self.url:
            yield from self._scrape_bulletin(soup)
        elif "lc.ntust.edu.tw" in self.url:
            yield from self._scrape_language_center(soup)
        elif "www.ntust.edu.tw" in self.url:
            yield from self._scrape_major_announcement(soup)
        else:
            raise ValueError(f"No scraper found for the given URL: {self.url}")

    def _scrape_bulletin(self, soup):
        table = soup.find("table")
        tbody = table.find("tbody")
        
        for row in tbody.find_all("tr"):
            publisher = "台科大" + row.find("td", {"data-th": "發佈單位"}).get_text(strip=True)
            title = row.find("td", {"data-th": "標題"}).get_text(strip=True)
            a_tag = row.find("a")
            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
            content = ""
            if url:
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.content, 'html.parser')
                paragraphs = soup.find_all("p")
                content = " ".join([p.get_text(strip=True) for p in paragraphs])
            yield {"publisher": publisher, "title": title, "url": url, "content": content}

    def _scrape_language_center(self, soup):
        divs = soup.find_all('div', attrs={'class': 'mtitle'})
        
        for tag in divs:
            a_tag = tag.find('a')
            url = a_tag.get('href')
            publisher = "台科大語言中心"
            title = a_tag.get_text(strip=True)
            content = ""
            if url:
                webpage = requests.get(url)
                webpage_soup = BeautifulSoup(webpage.content, 'html.parser')
                div = webpage_soup.find('div', attrs={'class': 'mpgdetail'})
                p_tags = div.find_all('p')
                content = " ".join([p.get_text(strip=True) for p in p_tags])
            yield {"publisher": publisher, "title": title, "url": url, "content": content}

    def _scrape_major_announcement(self, soup):
        titles = soup.find_all('div', attrs={'class': 'mtitle'})
        publisher = "台科大主校網"
        
        for t in titles:
            title = t.get_text(strip=True)
            a_tag = t.find('a')
            url = a_tag.get('href')
            content = ""  # No content retrieval logic provided in the original code
            yield {"publisher": publisher, "title": title, "url": url, "content": content}

def scrape():
    # Example usage of the combined scraper
    for url in [NTUST_LANG_URL, NTUST_OUTSIDE_URL]: # NTUST_INSIDE_URL, 
        scraper = NTUSTCombinedScraper(url)
        scraper.scrape()




#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================

import datetime
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Logger:
    name: str
    log_to_file: bool = False
    filename: Optional[str] = None

    def __post_init__(self):
        if self.log_to_file and not self.filename:
            raise ValueError("Filename must be provided if log_to_file is True")
    
    def _log(self, level: str, message: str):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{self.name}] [{level}] {message}"
        self._output(log_message)
    
    def _output(self, message: str):
        print(message)
        if self.log_to_file and self.filename:
            with open(self.filename, 'a') as f:
                f.write(message + '\n')
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warning(self, message: str):
        self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)



# 使用範例
logger = Logger("MyLogger", log_to_file=True, filename="log.txt")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")


#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================


import datetime
from typing import Optional
from functools import wraps
from dataclasses import dataclass

@dataclass
class Logger:
    name: str
    log_to_file: bool = False
    filename: Optional[str] = None

    def __post_init__(self):
        if self.log_to_file and not self.filename:
            raise ValueError("Filename must be provided if log_to_file is True")

    def _log(self, level: str, message: str):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{self.name}] [{level}] {message}"
        self._output(log_message)

    def _output(self, message: str):
        print(message)
        if self.log_to_file and self.filename:
            with open(self.filename, 'a') as f:
                f.write(message + '\n')

    def info(self, message: str):
        self._log("INFO", message)

    def warning(self, message: str):
        self._log("WARNING", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def log_method(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.info(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                self.info(f"Function {func.__name__} returned: {result}")
                return result
            except Exception as e:
                self.error(f"Function {func.__name__} raised an error: {e}")
                raise
        return wrapper


class Calculator:
    @Logger.log_method
    def add(self, a, b):
        return a + b

    @Logger.log_method
    def subtract(self, a, b):
        return a - b

@Logger(name="GreeterLogger", log_to_file=True, filename="greeter.log")
class Greeter:
    @Logger.log_method
    def greet(self, name, greeting="Hello"):
        return f"{greeting}, {name}!"







#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================


from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json, os
import psycopg2
import traceback
import time
from datetime import datetime
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Updater, Application, ContextTypes, filters, ChatMemberHandler
from telegram import  Chat, ChatMember, ChatMemberUpdated, ForceReply, Update, Bot 
from telegram.constants import ParseMode
import telegram
import copy
from decimal import Decimal
from dotenv import load_dotenv
from pydantic import BaseModel
import pprint 
import asyncio
from typing import List
import functools

# Database configuration
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

def handle_db_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print({"error": str(e), "detail": traceback.format_exc()})
            return None
    return wrapper

class DatabaseManager:
    def __init__(self, config: dict):
        self.config = config

    @handle_db_exceptions
    def _execute(self, query: str, params: tuple = None, fetch: bool = False):
        connection = psycopg2.connect(**self.config)
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def execute_query(self, query: str, params: tuple = None):
        return self._execute(query, params, fetch=True)

    def execute_update(self, query: str, params: tuple = None):
        self._execute(query, params)

class Bulletin(BaseModel):
    rawid: int
    publisher: str
    title: str
    url: str
    content: str
    addtime: datetime
    processstatus: bool

class BulletinManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_to_db(self, post: dict):
        if not self.db_manager.execute_query("SELECT 1 FROM bulletinraw WHERE publisher = %s AND title = %s", (post['publisher'], post['title'])):
            self.db_manager.execute_update("INSERT INTO bulletinraw (publisher, title, url, content) VALUES (%s, %s, %s, %s)", (post['publisher'], post['title'], post['url'], post['content']))

    def save_all(self, data: List[dict]):
        for post in data:
            self.save_to_db(post)

    def get_unprocessed(self) -> List[Bulletin]:
        rows = self.db_manager.execute_query("SELECT * FROM bulletinraw WHERE processstatus = false")
        return [Bulletin(**dict(zip([desc[0] for desc in cursor.description], row))) for row in rows]

    def update_status(self):
        self.db_manager.execute_update("UPDATE bulletinraw SET processstatus = true WHERE processstatus = false")

class Scraper(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrape(self):
        pass

class ScraperFactory:
    @staticmethod
    def get_scraper(url):
        if "bulletin.ntust.edu.tw" in url:
            return NTUSTBulletinScraper(url)
        elif "lc.ntust.edu.tw" in url:
            return NTUSTLanguageCenterScraper(url)
        elif "www.ntust.edu.tw" in url:
            return NTUSTMajorAnnouncementScraper(url)
        else:
            raise ValueError(f"No scraper found for the given URL: {url}")

class NTUSTBulletinScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for row in soup.find("table").find("tbody").find_all("tr"):
            publisher = "台科大" + row.find("td",{"data-th":"發佈單位"}).get_text(strip=True)
            title = row.find("td",{"data-th":"標題"}).get_text(strip=True)
            a_tag = row.find("a")
            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
            content = ""
            if url:
                content = ''.join(p.get_text(strip=True) for p in BeautifulSoup(requests.get(url).content, 'html.parser').find_all("p"))
            yield {"publisher":publisher,"title":title,"url":url,"content":content}

class NTUSTLanguageCenterScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup.find_all('div', attrs={'class': 'mtitle'}):
            a_tag = tag.find('a')
            url = a_tag.get('href')
            title, content = "", ""
            if url:
                title = a_tag.get_text(strip=True)
                content = ''.join(p.get_text(strip=True) for p in BeautifulSoup(requests.get(url).content, 'html.parser').find('div', attrs={'class':'mpgdetail'}).find_all('p'))
            yield {"publisher":"台科大語言中心", "title":title, "url":url, "content":content}

class NTUSTMajorAnnouncementScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for t in soup.find_all('div', attrs={'class': 'mtitle'}):
            yield {"publisher": "台科大主校網", "title": t.get_text(strip=True), "url": t.find('a').get('href'), "content": ""}

class ScraperManager:
    def __init__(self, scraper_factory, bulletin_manager: BulletinManager):
        self.scraper_factory = scraper_factory
        self.bulletin_manager = bulletin_manager

    def scrape_and_save(self, url: str):
        scraper = self.scraper_factory.get_scraper(url)
        self.bulletin_manager.save_all(scraper.scrape())

    def scrape_all(self, context: ContextTypes.DEFAULT_TYPE):
        for url in [NTUST_LANG_URL, NTUST_INSIDE_URL, NTUST_OUTSIDE_URL]:
            self.scrape_and_save(url)

async def send_new_data(context: ContextTypes.DEFAULT_TYPE, bulletin_manager: BulletinManager):
    for bulletin in bulletin_manager.get_unprocessed():
        await context.bot.send_message(chat_id="940229605", text=bulletin.title)
        await context.bot.send_message(chat_id="6904184189", text=bulletin.title)
    bulletin_manager.update_status()

def main():
    db_manager = DatabaseManager(db_config)
    bulletin_manager = BulletinManager(db_manager)
    scraper_manager = ScraperManager(ScraperFactory, bulletin_manager)
    TOKEN = "6588891089:AAETxqnSzmn7WBqBsHQ5tPcBYuiK36Dc1a8"

    application = Application.builder().token(TOKEN).build()
    job_queue = application.job_queue

    job_queue.run_repeating(scraper_manager.scrape_all, interval=15, first=3)
    job_queue.run_repeating(lambda context: send_new_data(context, bulletin_manager), interval=20, first=10)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
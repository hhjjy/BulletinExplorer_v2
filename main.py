from decimal import Decimal
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import BaseModel
from urllib.parse import urlparse
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import json, os, requests, psycopg2, traceback, time, copy, pprint, asyncio, functools,sys

# 設置 PYTHONPATH，使其包含當前目錄
from collections import defaultdict

# 匯入檔案
from Manager import *
from Scraper import *
from Broker import * 
from TelegramBot import * 

# main.py

def SaveBulletin(data):
    bulletin_manager = BulletinManager(db_config)
    try:
        bulletin_manager.save_bulletin(data)
        print(f"Successfully saved bulletin: {data['title']}")
    except Exception as e:
        print(f"儲存 {data['title']} 時發生錯誤：{e}")

lock = asyncio.Lock()
async def scrape(context: ContextTypes.DEFAULT_TYPE) -> None:
    async with lock:
        tasks = []
        for key in main_method:
            Scrape = ScraperFactory.get_scraper(key)
            tasks.append(asyncio.create_task(run_scrape(Scrape)))
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

async def run_scrape(Scrape):
    try:
        async for data in Scrape.scrape():
            SaveBulletin(data)  # 使用 await
    except Exception as e:
        print(f"在處理 {Scrape} 時發生錯誤：{e}")

def main() -> None:
 
    tgbot = TelegramBot("6588891089:AAETxqnSzmn7WBqBsHQ5tPcBYuiK36Dc1a8")
    tgbot.repeat_job(send_new_data, 5, 10)
    tgbot.repeat_job(scrape, 90, 3)
    tgbot.repeat_job(llm, interval=15, first=3)


    tgbot.command_handler(["start", "help"], start)
    tgbot.command_handler("subscribe", subscribe)
    tgbot.command_handler("unsubscribe", unsubscribe)
    tgbot.command_handler("list", list)


    # tgbot.command_handler("help", help)
    # tgbot.command_handler("search", search)
    # tgbot.command_handler("whereami", whereami)
    # tgbot.repeat_job(update_user, interval=30, first=3)


    tgbot.polling("Update.ALL_TYPES")

if __name__ == '__main__':
    user = UserManager(db_config)
    pprint.pprint(user.list_all_users())
    broker = Broker()
    main()


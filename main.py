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
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Updater, Application, ContextTypes, filters, ChatMemberHandler,CallbackContext
import json, os, requests, psycopg2, traceback, time, telegram, copy, pprint, asyncio, functools,sys

# 設置 PYTHONPATH，使其包含當前目錄
from collections import defaultdict

# 匯入檔案
from Manager import *
from Scraper import *
from Broker import * 
from TelegramBot import * 

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

broker = Broker()






def main() -> None:
 
    tgbot = TelegramBot("6588891089:AAETxqnSzmn7WBqBsHQ5tPcBYuiK36Dc1a8")
    tgbot.repeat_job(send_new_data, 20, 10)
    tgbot.repeat_job(scrape, 15, 3)


    tgbot.command_handler(["start", "help"], start)
    tgbot.command_handler("subscribe", subscribe)
    tgbot.command_handler("unsubscribe", unsubscribe)
    tgbot.command_handler("list", list)


# application = Application.builder().token(TOKEN).post_init(post_init).post_stop(post_stop).build()
# job_minute = job_queue.run_repeating(update_user, interval=30, first=3)
# job_minute = job_queue.run_repeating(llm, interval=15, first=3)
# application.add_handler(CommandHandler("help", help))
# application.add_handler(CommandHandler("search", search))
# application.add_handler(CommandHandler("whereami", whereami))


    # Run the bot until the user presses Ctrl-C
    tgbot.polling("Update.ALL_TYPES")

if __name__ == '__main__':
    # manager.add_subscription( "940229605", "便當")
    # manager.add_subscription( "940229605", "早餐")
    user = UserManager(db_config)
    pprint.pprint(user.list_all_users())
    # print(manager.get_all_subscriptions())
    main()


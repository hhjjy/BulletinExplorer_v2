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

async def send_new_data(context: ContextTypes.DEFAULT_TYPE) -> None :
    # await context.bot.send_message(chat_id="940229605", text="hi", parse_mode=ParseMode.MARKDOWN_V2)
    # print("send_new_data called with context:", context)
    bulletin_manager = BulletinManager(db_config)
    # 讀資料庫
    unprocessed_bulletins =  bulletin_manager.get_unprocessed_bulletins()
    # print(data)
    # [(1, 'test', 'test', 'test', 'test', datetime.datetime(2024, 6, 20, 15, 24, 47, 957529), False)]
    # 發送資料
    # pprint.pprint(data)

    for bulletin in unprocessed_bulletins:
        # pprint.pprint(i)
        # message = f"[{i.title}]({i.url})"
        # BUG : 目前MARKDOWN內不能包含 - 等特殊字元否則會抱錯 詳細的解法還要看後續升級
        # await context.bot.send_message(chat_id="940229605", text=f"[{i.title}]({i.url})", parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id="940229605", text = bulletin.title ) # 超連結 怎麼做?
        await context.bot.send_message(chat_id="6904184189", text = bulletin.title ) # 超連結 怎麼做?

    bulletin_manager.update_bulletin_status()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_manager = UserManager(db_config)

    """Sends explanation on how to use the bot."""
    chat_id = str(update.effective_message.chat_id)  # 確保 chat_id 是字符串
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    if not user_manager.user_exists(chat_id): #why it is not str?
        user_manager.add_user(user_name,chat_id)
        await update.message.reply_text("指令如下：\n/search [標籤名稱] - 搜尋標籤\n/subscribe [標籤名稱] - 訂閱標籤\n/unsubscribe [標籤名稱] - 取消訂閱標籤\n/list - 顯示正在追蹤的標籤")
    await update.message.reply_text("你已經註冊過了")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_message.chat_id)  # 確保 chat_id 是字符串
    try:
        label_name = update.message.text.split(' ')[1:][0]#chinese not work
    except:
        await update.effective_message.reply_text("Please enter the topic name")
        return
    broker.subscribe(chat_id,label_name)
    await update.effective_message.reply_text("Subscribe topic successfully")
           
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_message.chat_id)  # 確保 chat_id 是字符串
    try:
        label_name = update.message.text.split(' ')[1:][0]#chinese not work
    except:
        await update.effective_message.reply_text("Please enter the topic name")
        return
    broker.unsubscribe(chat_id,label_name)
    await update.effective_message.reply_text("UnSubscribe topic successfully")


async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    chat_id = str(update.effective_message.chat_id)  # 確保 chat_id 是字符串
    manager = SubscriptionManager(db_config)
    subscriptions = manager.get_user_subscriptions(chat_id)

    if subscriptions:
        response_text = "您的訂閱列表如下:\n"
        for sub in subscriptions:
            response_text += f"- {sub['topic_name']} (加入日期: {sub['join_date']})\n"
    else:
        response_text = "您目前沒有任何訂閱。"

    await update.effective_message.reply_text(response_text)



async def llm(context: ContextTypes.DEFAULT_TYPE) -> None :
    # 从 job context 中获取 chat_id
    # chat_id = job.context
    # 分類完 
    broker.push_message('午餐','好吃')
    # 取得消息
    users = broker.get_message()
    # 傳送 
    for user  in users :
        # self.memory.append({'chatid':f'{user}','topic_name':f'{topic}','message':f'{message}'})
        await context.bot.send_message(chat_id=user['chatid'], text=f"[{user['topic_name']}][{user['message']}]")

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

    application.add_handler(CommandHandler(["start", "help"], start))
    # application.add_handler(CommandHandler("help", help))
    # application.add_handler(CommandHandler("search", search))
    # application.add_handler(CommandHandler("whereami", whereami))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list)) 

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # manager.add_subscription( "940229605", "便當")
    # manager.add_subscription( "940229605", "早餐")
    user = UserManager(db_config)
    pprint.pprint(user.list_all_users())
    # print(manager.get_all_subscriptions())
    main()


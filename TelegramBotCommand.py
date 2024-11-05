from decimal import Decimal
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import BaseModel
from urllib.parse import urlparse
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import json, os, requests, psycopg2, traceback, time, copy, pprint, asyncio, functools,sys


# 匯入檔案
from Manager import *
from Broker import * 
from TelegramBot import * 

broker = Broker()

# async def send_new_data(context: ContextTypes.DEFAULT_TYPE) -> None :
#     # await context.bot.send_message(chat_id="940229605", text="hi", parse_mode=ParseMode.MARKDOWN_V2)
#     print("send_new_data called with context:", context)
#     bulletin_manager = BulletinManager(db_config)
#     # 讀資料庫
#     unprocessed_bulletins =  bulletin_manager.get_unprocessed_bulletins()
#     for bulletin in unprocessed_bulletins:
#         # pprint.pprint(i)
#         # message = f"[{i.title}]({i.url})"
#         # BUG : 目前MARKDOWN內不能包含 - 等特殊字元否則會抱錯 詳細的解法還要看後續升級
#         # await context.bot.send_message(chat_id="940229605", text=f"[{i.title}]({i.url})", parse_mode=ParseMode.MARKDOWN_V2)
#         await context.bot.send_message(chat_id="940229605", text = bulletin.title ) # 超連結 怎麼做?

#     bulletin_manager.update_bulletin_status()


async def send_new_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    print("send_new_data called with context:", context)
    bulletin_manager = BulletinManager(db_config)
    new_bulletins = bulletin_manager.get_unsent_bulletins()
    for bulletin in new_bulletins:
        print(f"Sending bulletin: {bulletin['title']}")
        # 傳送資料的邏輯
        # ...
        # 更新 sendstatus 為 True
        bulletin['sendstatus'] = True
        bulletin_manager.update_bulletin(bulletin)
        await context.bot.send_message(chat_id="940229605", text = bulletin['title'] ) # 超連結 怎麼做?


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


async def llm(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        bulletin_manager = BulletinManager(db_config)
        unclassified_bulletins = bulletin_manager.get_unclassified_bulletins()
        for bulletin in unclassified_bulletins:
            title = bulletin.get('title', '')
            # 檢查並提取【】中的分類
            if '【' in title and '】' in title:
                try:
                    category = title.split('【')[1].split('】')[0]
                    bulletin['category'] = category
                    print(category)
                    bulletin_manager.update_bulletin(bulletin)
                except IndexError:
                    print(f"無法解析分類: {title}")
                except Exception as e:
                    print(f"更新分類時發生錯誤: {str(e)}")
            else:
                print(f"找不到分類標記: {title}")
    except Exception as e:
        print(f"執行 llm 函數時發生錯誤: {str(e)}")

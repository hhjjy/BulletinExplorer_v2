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


# 匯入檔案
from Manager import *
from Scraper import *
from Broker import * 
from TelegramBot import * 

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




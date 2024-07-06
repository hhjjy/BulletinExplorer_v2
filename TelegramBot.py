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




from TelegramBotCommand import * 
class TelegramBot:
    def __init__(self, TOKEN):
        self.TOKEN = TOKEN
        self.application = Application.builder().token(TOKEN).build()
        self.job_queue = self.application.job_queue

    def repeat_job(self, function, interval, first):
        self.job_minute = self.job_queue.run_repeating(function, interval, first)

    def command_handler(self, command, function):
        self.application.add_handler(CommandHandler(command, function))

    def polling(self, update):
        self.application.run_polling(allowed_updates=update)




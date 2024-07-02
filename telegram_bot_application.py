import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

class TelegramBotApplication:
    def __init__(self, token: str, chat_ids: list):
        self.token = token
        self.chat_ids = chat_ids
        self.application = Application.builder().token(self.token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))

    async def send_new_data(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = self.get_unprocessed_bulletins()

        for i in data:
            for chat_id in self.chat_ids:
                await context.bot.send_message(chat_id=chat_id, text=i.title)

        self.update_bulletin_status()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Welcome! How can I assist you today?")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Here are the commands you can use:\n/start - Start the bot\n/help - Get help")

    async def scrape(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.Database.BulletinManager.save_bulletin(data)
        self.PubSubSystem.push_message(data)


    async def subscribe(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.PubSubSystem.subscribe(chat_id ,topic)

    def start_scheduled_tasks(self):
        self.application.job_queue.run_repeating(self.send_new_data, interval=20, first=10)
        self.application.job_queue.run_repeating(self.scrape, interval=15, first=3)

    def run(self):
        self.start_scheduled_tasks()
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def get_unprocessed_bulletins(self):
        # Placeholder function to simulate reading from a database
        return [(1, 'test', 'test', 'test', 'test', datetime.datetime(2024, 6, 20, 15, 24, 47, 957529), False)]

    def update_bulletin_status(self):
        # Placeholder function to simulate updating bulletin status in the database
        pass

from telegram_bot_application import TelegramBotApplication

class TelegramBot:
    def __init__(self, token: str, chat_ids: list):
        self.token = token
        self.chat_ids = chat_ids

    def run(self):
        bot_app = TelegramBotApplication(self.token, self.chat_ids)
        bot_app.run()

if __name__ == "__main__":
    TOKEN = "6588891089:AAETxqnSzmn7WBqBsHQ5tPcBYuiK36Dc1a8"
    CHAT_IDS = ["940229605", "6904184189"]
    
    bot = TelegramBot(token=TOKEN, chat_ids=CHAT_IDS)
    bot.run()

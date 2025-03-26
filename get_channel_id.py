from pyrogram import Client, filters
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("GetIDBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.channel)
def get_channel_info(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    print(f"Channel: {chat_title} | ID: {chat_id}")

bot.run()

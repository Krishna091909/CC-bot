from pyrogram import Client
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("GetIDBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def main():
    async with bot:
        async for dialog in bot.get_dialogs():
            if dialog.chat.type == "channel":
                print(f"Channel: {dialog.chat.title} | ID: {dialog.chat.id}")

bot.run(main())

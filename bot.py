import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, send_file
import threading

# Load environment variables
API_ID = int(os.getenv("API_ID", "26742257"))
API_HASH = os.getenv("API_HASH", "625a7410153e4222aa34b82b9cff2554")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7834981923:AAGYbPxyd3UWjjrDzwTvVScs0aAlf8B0eHk")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1002596681166"))
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "https://cc-link.onrender.com")

# Initialize bot
bot = Client("FileStreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app for serving files
app = Flask(__name__)

file_store = {}

@bot.on_message(filters.private & filters.document)
def receive_file(client, message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_store[file_id] = file_name
    file_link = f"{HOST}/download/{file_id}"
    stream_link = f"{HOST}/stream/{file_id}"
    message.reply_text(
        f"**File Uploaded Successfully!**\n\n📂 File Name: {file_name}\n🔗 [Download]({file_link}) | 🎥 [Stream]({stream_link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📥 Download", url=file_link)],
                [InlineKeyboardButton("🎥 Stream", url=stream_link)]
            ]
        ),
        disable_web_page_preview=True
    )
    client.send_message(LOG_CHANNEL, f"New file uploaded: {file_name}\n{file_link}\n{stream_link}")

@app.route("/download/<file_id>")
def download_file(file_id):
    if file_id in file_store:
        file_path = bot.download_media(file_id)
        return send_file(file_path, as_attachment=True)
    return "File Not Found!", 404

@app.route("/stream/<file_id>")
def stream_file(file_id):
    if file_id in file_store:
        file_path = bot.download_media(file_id)
        return send_file(file_path)
    return "File Not Found!", 404

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()

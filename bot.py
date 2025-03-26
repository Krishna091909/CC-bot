import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, send_file
import threading

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))  # Convert to int

# Initialize bot
bot = Client("FileStreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app for serving files
app = Flask(__name__)

file_store = {}  # Stores file IDs for quick access

@bot.on_message(filters.private & filters.document)
def receive_file(client, message):
    file_id = message.document.file_id
    file_name = message.document.file_name

    # Forward file to log channel instantly
    if LOG_CHANNEL:
        forwarded_message = message.forward(LOG_CHANNEL)
        log_message_id = forwarded_message.message_id
    else:
        log_message_id = None

    # Store file details
    file_store[file_id] = log_message_id

    # Generate fast access links using Telegram File ID
    file_link = f"{HOST}/download/{file_id}"
    stream_link = f"{HOST}/stream/{file_id}"

    # Send instant response to user
    message.reply_text(
        f"**File Received & Forwarded!**\n\n📂 File Name: {file_name}\n🔗 [Download]({file_link}) | 🎥 [Stream]({stream_link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📥 Download", url=file_link)],
                [InlineKeyboardButton("🎥 Stream", url=stream_link)]
            ]
        ),
        disable_web_page_preview=True
    )

@app.route("/download/<file_id>")
def download_file(file_id):
    if file_id in file_store:
        return send_file(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_id}", as_attachment=True)
    return "File Not Found!", 404

@app.route("/stream/<file_id>")
def stream_file(file_id):
    if file_id in file_store:
        return send_file(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_id}")
    return "File Not Found!", 404

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()

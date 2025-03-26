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
LOG_CHANNEL = os.getenv("LOG_CHANNEL")

if LOG_CHANNEL:
    LOG_CHANNEL = int(LOG_CHANNEL)
else:
    LOG_CHANNEL = None  # Set to None explicitly

# Initialize bot
bot = Client("FileStreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app for serving files
app = Flask(__name__)

# Directory for storing files persistently
SAVE_DIR = "downloads"
os.makedirs(SAVE_DIR, exist_ok=True)  # Ensure directory exists

file_store = {}  # Stores file paths

@bot.on_message(filters.private & filters.document)
def receive_file(client, message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_path = os.path.join(SAVE_DIR, file_name)  # Save file in persistent folder

    # Download file to the defined path
    client.download_media(message, file_path)
    file_store[file_id] = file_path  # Store the actual path

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

    try:
        if LOG_CHANNEL:
            client.send_message(LOG_CHANNEL, f"New file uploaded: {file_name}\n{file_link}\n{stream_link}")
    except Exception as e:
        logging.error(f"Failed to send log message: {e}")

@app.route("/download/<file_id>")
def download_file(file_id):
    file_path = file_store.get(file_id)
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File Not Found!", 404

@app.route("/stream/<file_id>")
def stream_file(file_id):
    file_path = file_store.get(file_id)
    if file_path and os.path.exists(file_path):
        return send_file(file_path)
    return "File Not Found!", 404

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()

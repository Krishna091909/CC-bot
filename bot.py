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
LOG_CHANNEL = -100xxxxxxxxxx  # Replace with the correct private channel ID

# Initialize bot
bot = Client("FileStreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app for serving files
app = Flask(__name__)

file_store = {}  # Stores file paths

@bot.on_message(filters.private & filters.document)
def receive_file(client, message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    
    # Forward the file to the log channel
    try:
        forwarded_message = message.forward(LOG_CHANNEL)
    except Exception as e:
        logging.error(f"Failed to forward message: {e}")
        message.reply_text("❌ Failed to forward file. Check log channel ID and bot permissions.")
        return
    
    # Download file
    file_path = client.download_media(message)
    file_store[file_id] = file_path

    # Generate links
    file_link = f"{HOST}/download/{file_id}"
    stream_link = f"{HOST}/stream/{file_id}"
    
    # Send response quickly
    message.reply_text(
        f"**File Uploaded Successfully!**\n\n📂 File Name: {file_name}\n🔗 [Download]({file_link}) | 🎥 [Stream]({stream_link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⬇️ Download", url=file_link)],
                [InlineKeyboardButton("▶️ Stream", url=stream_link)]
            ]
        ),
        disable_web_page_preview=True
    )

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

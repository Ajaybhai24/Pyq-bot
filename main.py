import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from threading import Thread
from flask import Flask

# लॉगिंग सेट अप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. छोटा सा Flask सर्वर ताकि Render की Web Service खुश रहे
app = Flask('')

@app.route('/')
def home():
    return "Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# 2. टेलीग्राम बॉट का कोड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"नमस्ते {user_name} जी! SSC और सरकारी परीक्षा के PYQ प्रैक्टिस बॉट में आपका स्वागत है। 🚀"
    )

def main():
    TOKEN = os.environ.get("TOKEN")
    if not TOKEN:
        print("Error: TOKEN not found!")
        return

    # वेब सर्वर को बैकग्राउंड में चलाना
    keep_alive()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("बॉट शुरू हो गया है...")
    application.run_polling()

if __name__ == '__main__':
    main()

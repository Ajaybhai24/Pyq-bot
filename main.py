import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# लॉगिंग सेट अप करते हैं
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# जब यूजर /start लिखेगा
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"नमस्ते {user_name} जी! SSC और सरकारी परीक्षा के PYQ प्रैक्टिस बॉट में आपका स्वागत है। 🚀\n\n"
        "जल्द ही यहाँ आपको Subject और Topic चुनने का विकल्प मिलेगा।"
    )

def main():
    # Render के Environment Variable से टोकन को सुरक्षित तरीके से उठाना
    TOKEN = os.environ.get("TOKEN")
    
    if not TOKEN:
        print("Error: TOKEN environment variable not found!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # /start कमांड जोड़ना
    application.add_handler(CommandHandler("start", start))

    print("बॉट शुरू हो गया है...")
    # बॉट को चलाना
    application.run_polling()

if __name__ == '__main__':
    main()

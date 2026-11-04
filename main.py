import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# लॉगिंग सेट अप करते हैं ताकि कोई एरर आए तो पता चल सके
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# जब यूजर /start लिखेगा, तब यह फंक्शन चलेगा
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"नमस्ते {user_name} जी! SSC और सरकारी परीक्षा के PYQ प्रैक्टिस बॉट में आपका स्वागत है। 🚀\n\n"
        "जल्द ही यहाँ आपको Subject और Topic चुनने का विकल्प मिलेगा।"
    )

if __name__ == '__main__':
    # यहाँ अपना BotFather वाला API Token डालना है
    TOKEN = "7280621712:AAGTzFS04PDZVHNTBL5_jqhPfmMiZTA-qCk"

    application = ApplicationBuilder().token(TOKEN).build()

    # /start कमांड को जोड़ने के लिए
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    print("बॉट शुरू हो गया है...")
    # बॉट को लगातार चालू रखने के लिए
    application.run_polling()

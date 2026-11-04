import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from threading import Thread
from flask import Flask

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Render web service ko active rakhne ke liye chhota Flask server
app = Flask('')

@app.route('/')
def home():
    return "SSC PYQ Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# /start command: Bhaasha (Language) chunne ka option dena
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome! Please select your preferred language / कृपया अपनी भाषा चुनेंस:",
        reply_markup=reply_markup
    )

# Button clicks ko handle karne ke liye (Language aur Subject selection)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_data = context.user_data

    # 1. Jab user language chun le
    if data.startswith("lang_"):
        lang = "Hindi" if data == "lang_hi" else "English"
        user_data['language'] = lang

        # Bhaasha chunne wala message delete kar dena
        await query.message.delete()

        # Subject select karne ka option bhejna
        if lang == "Hindi":
            sub_text = "बहुत बढ़िया! अब अपना पसंदीदा विषय (Subject) चुनें:"
            buttons = [
                [InlineKeyboardButton("इतिहास (History)", callback_data="sub_history")],
                [InlineKeyboardButton("भारतीय राजव्यवस्था (Indian Polity)", callback_data="sub_polity")],
                [InlineKeyboardButton("करेंट अफेयर्स (Current Affairs)", callback_data="sub_ca")],
                [InlineKeyboardButton("स्टैटिक जीके (Static GK)", callback_data="sub_static")]
            ]
        else:
            sub_text = "Great! Now select your preferred Subject:"
            buttons = [
                [InlineKeyboardButton("History", callback_data="sub_history")],
                [InlineKeyboardButton("Indian Polity & Constitution", callback_data="sub_polity")],
                [InlineKeyboardButton("Current Affairs", callback_data="sub_ca")],
                [InlineKeyboardButton("Static GK", callback_data="sub_static")]
            ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(sub_text, reply_markup=reply_markup)

    # 2. Jab user subject chun le
    elif data.startswith("sub_"):
        subject_code = data.replace("sub_", "")
        user_data['subject'] = subject_code

        # Subject select karne wala message delete kar dena
        await query.message.delete()

        lang = user_data.get('language', 'English')
        
        # Pehla AI generated sample question bhejna (Options ke sath)
        if lang == "Hindi":
            intro_msg = f"आपने विषय चुन लिया है। SSC PYQ पैटर्न के आधार पर AI पहला सवाल भेज रहा है:"
            question_text = (
                f"**प्रश्न 1:** निम्नलिखित में से किस अधिनियम के द्वारा भारत में द्वैध शासन (Dyarchy) की शुरुआत की गई थी?\n\n"
                f"A) 1909 का अधिनियम\n"
                f"B) 1919 का अधिनियम\n"
                f"C) 1935 का अधिनियम\n"
                f"D) 1892 का अधिनियम"
            )
        else:
            intro_msg = f"Subject selected. AI is generating the first question based on previous year trends:"
            question_text = (
                f"**Q1:** Which of the following acts introduced Dyarchy in India?\n\n"
                f"A) Government of India Act, 1909\n"
                f"B) Government of India Act, 1919\n"
                f"C) Government of India Act, 1935\n"
                f"D) Indian Councils Act, 1892"
            )

        await query.message.reply_text(intro_msg)
        
        # Question ke sath options ke buttons
        q_keyboard = [
            [InlineKeyboardButton("A", callback_data="ans_A"), InlineKeyboardButton("B", callback_data="ans_B")],
            [InlineKeyboardButton("C", callback_data="ans_C"), InlineKeyboardButton("D", callback_data="ans_D")]
        ]
        await query.message.reply_text(question_text, reply_markup=InlineKeyboardMarkup(q_keyboard))

    # 3. Jab user answer par click kare
    elif data.startswith("ans_"):
        selected_option = data.replace("ans_", "")
        lang = user_data.get('language', 'English')

        # Yahan question message delete NAHI hoga, bas user ko bataya jayega aur next question aayega
        if lang == "Hindi":
            await query.message.reply_text(f"✅ आपने विकल्प **{selected_option}** चुना। (सही उत्तर: B - 1919 का अधिनियम)\n\nअगला प्रश्न जल्द ही लोड हो रहा है...")
        else:
            await query.message.reply_text(f"✅ You selected option **{selected_option}**. (Correct Answer: B)\n\nLoading next question...")

        # Agla AI question bhejne ka logic yahan aage jod sakte hain

def main():
    TOKEN = os.environ.get("TOKEN")
    if not TOKEN:
        print("Error: TOKEN not found!")
        return

    keep_alive()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot shuru ho gaya hai...")
    application.run_polling()

if __name__ == '__main__':
    main()

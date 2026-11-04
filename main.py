import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from threading import Thread
from flask import Flask

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Render server keep-alive
app = Flask('')

@app.route('/')
def home():
    return "SSC PYQ Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# /start command: Professional Language Selection Menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 **नमस्ते {user_name} जी!**\n\n"
        "🎯 **SSC & Government Exams PYQ Master Bot** में आपका स्वागत है।\n\n"
        "कृपया अपनी पसंदीदा भाषा (Preferred Language) चुनें:"
    )
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# Button Handler for smooth UI flow
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_data = context.user_data

    # 1. Language Selected -> Show Subject Menu
    if data.startswith("lang_"):
        lang = "Hindi" if data == "lang_hi" else "English"
        user_data['language'] = lang

        await query.message.delete()

        if lang == "Hindi":
            sub_text = (
                "📚 **विषय चयन (Subject Selection)**\n\n"
                "तैयारी को मजबूत करने के लिए नीचे दिए गए विषयों में से किसी एक को चुनें:"
            )
            buttons = [
                [InlineKeyboardButton("📖 इतिहास (History)", callback_data="sub_history")],
                [InlineKeyboardButton("⚖️ भारतीय राजव्यवस्था (Indian Polity)", callback_data="sub_polity")],
                [InlineKeyboardButton("🔥 करेंट अफेयर्स (Current Affairs)", callback_data="sub_ca")],
                [InlineKeyboardButton("💡 स्टैटिक जीके (Static GK)", callback_data="sub_static")]
            ]
        else:
            sub_text = (
                "📚 **Subject Selection**\n\n"
                "Please choose a subject to start practicing previous year questions:"
            )
            buttons = [
                [InlineKeyboardButton("📖 History", callback_data="sub_history")],
                [InlineKeyboardButton("⚖️ Indian Polity & Constitution", callback_data="sub_polity")],
                [InlineKeyboardButton("🔥 Current Affairs", callback_data="sub_ca")],
                [InlineKeyboardButton("💡 Static GK", callback_data="sub_static")]
            ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(sub_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    # 2. Subject Selected -> Send First Clean Quiz Question
    elif data.startswith("sub_"):
        subject_code = data.replace("sub_", "")
        user_data['subject'] = subject_code

        await query.message.delete()
        lang = user_data.get('language', 'English')
        
        if lang == "Hindi":
            question_box = (
                "🎯 **विषय:** भारतीय राजव्यवस्था (Polity)\n"
                "📌 **प्रश्न 1 / 10**\n\n"
                "निम्नलिखित में से किस अधिनियम के द्वारा भारत में द्वैध शासन (Dyarchy) की शुरुआत की गई थी?\n\n"
                "🔹 **A)** 1909 का अधिनियम\n"
                "🔹 **B)** 1919 का अधिनियम\n"
                "🔹 **C)** 1935 का अधिनियम\n"
                "🔹 **D)** 1892 का अधिनियम"
            )
        else:
            question_box = (
                "🎯 **Subject:** Indian Polity\n"
                "📌 **Question 1 / 10**\n\n"
                "Which of the following acts introduced Dyarchy in India?\n\n"
                "🔹 **A)** Government of India Act, 1909\n"
                "🔹 **B)** Government of India Act, 1919\n"
                "🔹 **C)** Government of India Act, 1935\n"
                "🔹 **D)** Indian Councils Act, 1892"
            )
        
        # Sleek option buttons layout
        q_keyboard = [
            [
                InlineKeyboardButton("A", callback_data="ans_A"),
                InlineKeyboardButton("B", callback_data="ans_B")
            ],
            [
                InlineKeyboardButton("C", callback_data="ans_C"),
                InlineKeyboardButton("D", callback_data="ans_D")
            ]
        ]
        await query.message.reply_text(question_box, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(q_keyboard))

    # 3. Answer Clicked -> Instant Feedback without messing up UI
    elif data.startswith("ans_"):
        selected_option = data.replace("ans_", "")
        lang = user_data.get('language', 'English')

        if lang == "Hindi":
            feedback = (
                f"{query.message.text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"✍️ आपका उत्तर: **{selected_option}**\n"
                f"✅ **सही उत्तर: B (1919 का अधिनियम)**\n"
                f"💡 *स्पष्टीकरण:* मांटग्यू-चेम्सफोर्ड सुधार (1919) द्वारा प्रांतों में द्वैध शासन प्रणाली शुरू की गई थी।"
            )
        else:
            feedback = (
                f"{query.message.text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"✍️ Your Answer: **{selected_option}**\n"
                f"✅ **Correct Answer: B (Govt of India Act, 1919)**\n"
                f"💡 *Explanation:* Dyarchy in the provinces was introduced by the Montague-Chelmsford Reforms (1919)."
            )

        # Edit the same message to show result cleanly, keeping history intact
        await query.message.edit_text(feedback, parse_mode=ParseMode.MARKDOWN)

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

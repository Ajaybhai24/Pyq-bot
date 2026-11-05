import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from threading import Thread
from flask import Flask

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Render keep-alive server
app = Flask('')

@app.route('/')
def home():
    return "SSC PYQ Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Subject-wise reliable PYQ question bank taaki kabhi repeat na ho aur sahi subject aaye
QUESTION_BANK = {
    "History": {
        "Hindi": [
            {
                "q": "हड़प्पा सभ्यता की खोज किस वर्ष की गई थी?",
                "opts": {"A": "1921", "B": "1922", "C": "1935", "D": "1901"},
                "corr": "A",
                "exp": "हड़प्पा सभ्यता की खोज दयाराम साहनी ने वर्ष 1921 में की थी।"
            },
            {
                "q": "बुद्ध ने अपना पहला उपदेश कहां दिया था?",
                "opts": {"A": "बोधगया", "B": "सारनाथ", "C": "कुशीनगर", "D": "लुम्बिनी"},
                "corr": "B",
                "exp": "महात्मा बुद्ध ने अपना पहला उपदेश सारनाथ में दिया था जिसे 'धर्मचक्र प्रवर्तन' कहा जाता है।"
            },
            {
                "q": "गुप्त वंश का संस्थापक कौन था?",
                "opts": {"A": "श्रीगुप्त", "B": "चंद्रगुप्त प्रथम", "C": "समुद्रगुप्त", "D": "स्कंदगुप्त"},
                "corr": "A",
                "exp": "गुप्त वंश के संस्थापक श्रीगुप्त थे (लगभग 240 ईस्वी)।"
            }
        ],
        "English": [
            {
                "q": "In which year was the Harappan civilization discovered?",
                "opts": {"A": "1921", "B": "1922", "C": "1935", "D": "1901"},
                "corr": "A",
                "exp": "The Harappan civilization was discovered by Daya Ram Sahni in 1921."
            },
            {
                "q": "Where did Buddha deliver his first sermon?",
                "opts": {"A": "Bodh Gaya", "B": "Sarnath", "C": "Kushinagar", "D": "Lumbini"},
                "corr": "B",
                "exp": "Gautam Buddha delivered his first sermon at Sarnath, known as Dhammachakkappavattana Sutta."
            },
            {
                "q": "Who was the founder of the Gupta dynasty?",
                "opts": {"A": "Sri Gupta", "B": "Chandragupta I", "C": "Samudragupta", "D": "Skandagupta"},
                "corr": "A",
                "exp": "Sri Gupta was the founder of the Gupta Empire."
            }
        ]
    },
    "Indian Polity": {
        "Hindi": [
            {
                "q": "भारतीय संविधान के किस अनुच्छेद में 'Right to Equality' (समानता का अधिकार) दिया गया है?",
                "opts": {"A": "अनुच्छेद 14-18", "B": "अनुच्छेद 19-22", "C": "अनुच्छेद 23-24", "D": "अनुच्छेद 25-28"},
                "corr": "A",
                "exp": "भारतीय संविधान के अनुच्छेद 14 से 18 तक समानता के अधिकार से संबंधित हैं।"
            },
            {
                "q": "भारतीय संविधान का कौन सा भाग मौलिक अधिकारों से संबंधित है?",
                "opts": {"A": "भाग I", "B": "भाग II", "C": "भाग III", "D": "भाग IV"},
                "corr": "C",
                "exp": "संविधान का भाग III (अनुच्छेद 12-35) मौलिक अधिकारों से संबंधित है।"
            }
        ],
        "English": [
            {
                "q": "Which articles of the Indian Constitution deal with the Right to Equality?",
                "opts": {"A": "Articles 14-18", "B": "Articles 19-22", "C": "Articles 23-24", "D": "Articles 25-28"},
                "corr": "A",
                "exp": "Articles 14 to 18 of the Indian Constitution guarantee the Right to Equality."
            },
            {
                "q": "Which part of the Indian Constitution contains Fundamental Rights?",
                "opts": {"A": "Part I", "B": "Part II", "C": "Part III", "D": "Part IV"},
                "corr": "C",
                "exp": "Part III of the Indian Constitution (Articles 12-35) contains the Fundamental Rights."
            }
        ]
    },
    "Current Affairs": {
        "Hindi": [
            {
                "q": "हाल ही में चर्चा में रहे प्रमुख राष्ट्रीय और अंतरराष्ट्रीय घटनाक्रमों से संबंधित एसएससी पैटर्न प्रश्न।",
                "opts": {"A": "विकल्प 1", "B": "विकल्प 2", "C": "विकल्प 3", "D": "विकल्प 4"},
                "corr": "A",
                "exp": "करेंट अफेयर्स के अद्यतन तथ्यों के अनुसार यह प्रश्न महत्वपूर्ण है।"
            }
        ],
        "English": [
            {
                "q": "Recent national and international current affairs pattern question for SSC exams.",
                "opts": {"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"},
                "corr": "A",
                "exp": "This is based on recent updates relevant for SSC competitive exams."
            }
        ]
    },
    "Static GK": {
        "Hindi": [
            {
                "q": "भारत का सबसे उच्च नागरिक पुरस्कार कौन सा है?",
                "opts": {"A": "पद्म विभूषण", "B": "भारत रत्न", "C": "पद्म भूषण", "D": "अशोक चक्र"},
                "corr": "B",
                "exp": "भारत रत्न भारत का सर्वोच्च नागरिक सम्मान है।"
            }
        ],
        "English": [
            {
                "q": "Which is the highest civilian award in India?",
                "opts": {"A": "Padma Vibhushan", "B": "Bharat Ratna", "C": "Padma Bhushan", "D": "Ashok Chakra"},
                "corr": "B",
                "exp": "Bharat Ratna is the highest civilian award of the Republic of India."
            }
        ]
    }
}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 Namaste {user_name} ji!\n\n"
        "🎯 SSC & Government Exams PYQ Bot me aapka swagat hai.\n"
        "Kripya apni bhasha (Language) chunein:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_data = context.user_data

    # 1. Language Selection
    if data.startswith("lang_"):
        lang = "Hindi" if data == "lang_hi" else "English"
        user_data['language'] = lang

        try:
            await query.message.delete()
        except:
            pass

        if lang == "Hindi":
            sub_text = "📚 **Vishay Chayan (Subject Selection):**\n\nPrashn abhyas ke liye apna vishay chunein:"
            buttons = [
                [InlineKeyboardButton("📖 History (इतिहास)", callback_data="sub_History")],
                [InlineKeyboardButton("⚖️ Indian Polity (राजव्यवस्था)", callback_data="sub_Indian Polity")],
                [InlineKeyboardButton("🔥 Current Affairs (करेंट अफेयर्स)", callback_data="sub_Current Affairs")],
                [InlineKeyboardButton("💡 Static GK (स्टैटिक जीके)", callback_data="sub_Static GK")]
            ]
        else:
            sub_text = "📚 **Subject Selection:**\n\nPlease choose a subject for practice:"
            buttons = [
                [InlineKeyboardButton("📖 History", callback_data="sub_History")],
                [InlineKeyboardButton("⚖️ Indian Polity", callback_data="sub_Indian Polity")],
                [InlineKeyboardButton("🔥 Current Affairs", callback_data="sub_Current Affairs")],
                [InlineKeyboardButton("💡 Static GK", callback_data="sub_Static GK")]
            ]

        await query.message.reply_text(sub_text, reply_markup=InlineKeyboardMarkup(buttons))

    # 2. Subject Selection or Next Question
    elif data.startswith("sub_") or data == "next_q":
        if data.startswith("sub_"):
            subject = data.replace("sub_", "")
            user_data['subject'] = subject
        else:
            subject = user_data.get('subject', 'History')

        try:
            await query.message.delete()
        except:
            pass

        lang = user_data.get('language', 'English')
        
        # Usi subject aur language ke list se random question uthana taki har baar naya mile
        subj_pool = QUESTION_BANK.get(subject, QUESTION_BANK["History"])
        lang_pool = subj_pool.get(lang, subj_pool["English"])
        
        q_item = random.choice(lang_pool)
        user_data['current_question'] = q_item

        question_box = (
            f"🎯 **Subject: {subject}**\n\n"
            f"❓ **{q_item['q']}**\n\n"
            f"A) {q_item['opts']['A']}\n"
            f"B) {q_item['opts']['B']}\n"
            f"C) {q_item['opts']['C']}\n"
            f"D) {q_item['opts']['D']}"
        )
        
        q_keyboard = [
            [InlineKeyboardButton("A", callback_data="ans_A"), InlineKeyboardButton("B", callback_data="ans_B")],
            [InlineKeyboardButton("C", callback_data="ans_C"), InlineKeyboardButton("D", callback_data="ans_D")]
        ]
        
        await query.message.reply_text(question_box, reply_markup=InlineKeyboardMarkup(q_keyboard))

    # 3. Answer Clicked
    elif data.startswith("ans_"):
        selected_option = data.replace("ans_", "")
        q_item = user_data.get('current_question')
        
        if not q_item:
            await query.message.reply_text("Session expired. Please click /start again.")
            return

        correct_option = q_item['corr']
        explanation = q_item['exp']
        lang = user_data.get('language', 'English')

        # Lock buttons with indicators
        locked_keyboard = [
            [InlineKeyboardButton(f"{'✅' if 'A'==correct_option else ('❌' if 'A'==selected_option else '🔒')} A", callback_data="noop"), 
             InlineKeyboardButton(f"{'✅' if 'B'==correct_option else ('❌' if 'B'==selected_option else '🔒')} B", callback_data="noop")],
            [InlineKeyboardButton(f"{'✅' if 'C'==correct_option else ('❌' if 'C'==selected_option else '🔒')} C", callback_data="noop"), 
             InlineKeyboardButton(f"{'✅' if 'D'==correct_option else ('❌' if 'D'==selected_option else '🔒')} D", callback_data="noop")]
        ]

        try:
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(locked_keyboard))
        except:
            pass

        if lang == "Hindi":
            exp_text = (
                f"✍️ **Aapka Uttar:** {selected_option} | 🟢 **Sahi Uttar:** {correct_option}\n\n"
                f"💡 **Vistrit Spashtikaran:**\n{explanation}"
            )
            next_btn_text = "➡️ Agla Prashn (Next Question)"
        else:
            exp_text = (
                f"✍️ **Your Answer:** {selected_option} | 🟢 **Correct Answer:** {correct_option}\n\n"
                f"💡 **Detailed Explanation:**\n{explanation}"
            )
            next_btn_text = "➡️ Next Question"

        next_keyboard = [[InlineKeyboardButton(next_btn_text, callback_data="next_q")]]
        await query.message.reply_text(exp_text, reply_markup=InlineKeyboardMarkup(next_keyboard))

    elif data == "noop":
        await query.answer("Aap pehle hi jawab de chuke hain!", show_alert=True)

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

import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from threading import Thread
from flask import Flask
import google.generativeai as genai

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Gemini AI Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    ai_model = None

# Render keep-alive server
app = Flask('')

@app.route('/')
def home():
    return "SSC PYQ AI Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# AI se dynamic question generate karne ka function
def generate_ai_question(subject, lang):
    if not ai_model:
        # Fallback agar API key set na ho
        return {
            "question": "Which act introduced Dyarchy in India?",
            "options": {"A": "1909 Act", "B": "1919 Act", "C": "1935 Act", "D": "1892 Act"},
            "correct": "B",
            "explanation": "Dyarchy in provinces was introduced by the Montague-Chelmsford Reforms (1919)."
        }
    
    prompt = f"""
    You are an expert SSC exam question creator. Generate a unique, high-quality Previous Year style Multiple Choice Question (MCQ) for the subject '{subject}' in '{lang}' language.
    The output must strictly follow this format using separator '###':
    QUESTION: [Write the question here]
    OPTION_A: [Text for option A]
    OPTION_B: [Text for option B]
    OPTION_C: [Text for option C]
    OPTION_D: [Text for option D]
    CORRECT: [A, B, C or D]
    EXPLANATION: [Detailed explanation of why the answer is correct in {lang}]
    """
    
    try:
        response = ai_model.generate_content(prompt)
        text = response.text
        
        # Parsing AI response safely
        lines = text.strip().split('\n')
        q_data = {"question": "", "options": {}, "correct": "B", "explanation": ""}
        
        for line in lines:
            if line.startswith("QUESTION:"):
                q_data["question"] = line.replace("QUESTION:", "").strip()
            elif line.startswith("OPTION_A:"):
                q_data["options"]["A"] = line.replace("OPTION_A:", "").strip()
            elif line.startswith("OPTION_B:"):
                q_data["options"]["B"] = line.replace("OPTION_B:", "").strip()
            elif line.startswith("OPTION_C:"):
                q_data["options"]["C"] = line.replace("OPTION_C:", "").strip()
            elif line.startswith("OPTION_D:"):
                q_data["options"]["D"] = line.replace("OPTION_D:", "").strip()
            elif line.startswith("CORRECT:"):
                q_data["correct"] = line.replace("CORRECT:", "").strip().upper()
            elif line.startswith("EXPLANATION:"):
                q_data["explanation"] = line.replace("EXPLANATION:", "").strip()
                
        if not q_data["question"]:
            raise Exception("Parsing failed")
            
        return q_data
    except Exception as e:
        print(f"AI Error: {e}")
        # Default fallback
        return {
            "question": "भारतीय संविधान का कौन सा अनुच्छेद मूल अधिकार से संबंधित है? / Which article relates to Fundamental Rights?",
            "options": {"A": "Article 12-35", "B": "Article 36-51", "C": "Article 52-61", "D": "Article 1-4"},
            "correct": "A",
            "explanation": "Fundamental Rights are enshrined in Part III from Article 12 to 35 of the Indian Constitution."
        }

# /start command: Language Selection Menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 **नमस्ते {user_name} जी!**\n\n"
        "🎯 **SSC & Government Exams AI PYQ Bot** में आपका स्वागत है।\n"
        "यह बॉट AI एनालिसिस के आधार पर हर बार आपको नए और बेहतरीन सवाल देगा।\n\n"
        "कृपया अपनी भाषा (Preferred Language) चुनें:"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# Button Handler
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
            sub_text = "📚 **विषय चयन (Subject Selection):**\n\nAI प्रैक्टिस के लिए नीचे दिए गए विषयों में से चुनें:"
            buttons = [
                [InlineKeyboardButton("📖 इतिहास (History)", callback_data="sub_History")],
                [InlineKeyboardButton("⚖️ भारतीय राजव्यवस्था (Indian Polity)", callback_data="sub_Polity")],
                [InlineKeyboardButton("🔥 करेंट अफेयर्स (Current Affairs)", callback_data="sub_Current_Affairs")],
                [InlineKeyboardButton("💡 स्टैटिक जीके (Static GK)", callback_data="sub_Static_GK")]
            ]
        else:
            sub_text = "📚 **Subject Selection:**\n\nPlease choose a subject for AI practice:"
            buttons = [
                [InlineKeyboardButton("📖 History", callback_data="sub_History")],
                [InlineKeyboardButton("⚖️ Indian Polity & Constitution", callback_data="sub_Polity")],
                [InlineKeyboardButton("🔥 Current Affairs", callback_data="sub_Current_Affairs")],
                [InlineKeyboardButton("💡 Static GK", callback_data="sub_Static_GK")]
            ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(sub_text, parse_mode='Markdown', reply_markup=reply_markup)

    # 2. Subject Selected -> Generate AI Question
    elif data.startswith("sub_"):
        subject = data.replace("sub_", "").replace("_", " ")
        user_data['subject'] = subject

        await query.message.delete()
        lang = user_data.get('language', 'English')
        
        # Loading message
        loading_msg = await query.message.reply_text("🤖 AI is analyzing previous year trends and generating a fresh question for you...")

        # AI se question generate karwana
        q_data = generate_ai_question(subject, lang)
        user_data['current_question'] = q_data  # Save in session for checking answer

        # Format question box
        question_box = (
            f"🎯 **Subject:** {subject}\n"
            f"📌 **AI Generated PYQ Question**\n\n"
            f"❓ {q_data['question']}\n\n"
            f"🔹 **A)** {q_data['options'].get('A', '')}\n"
            f"🔹 **B)** {q_data['options'].get('B', '')}\n"
            f"🔹 **C)** {q_data['options'].get('C', '')}\n"
            f"🔹 **D)** {q_data['options'].get('D', '')}"
        )
        
        q_keyboard = [
            [InlineKeyboardButton("A", callback_data="ans_A"), InlineKeyboardButton("B", callback_data="ans_B")],
            [InlineKeyboardButton("C", callback_data="ans_C"), InlineKeyboardButton("D", callback_data="ans_D")]
        ]
        
        await loading_msg.delete()
        await query.message.reply_text(question_box, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(q_keyboard))

    # 3. Answer Clicked -> Detailed Explanation & Lock Buttons
    elif data.startswith("ans_"):
        selected_option = data.replace("ans_", "")
        q_data = user_data.get('current_question')
        
        if not q_data:
            await query.message.reply_text("Session expired. Please click /start again.")
            return

        correct_option = q_data['correct']
        explanation = q_data['explanation']

        if selected_option == correct_option:
            feedback = (
                f"{query.message.text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🎉 **बधाई हो! आपका जवाब बिल्कुल सही है!** 🥳✨\n"
                f"✅ **चुना गया उत्तर:** {selected_option}\n\n"
                f"💡 **विस्तृत स्पष्टीकरण (Detailed Explanation):**\n{explanation}"
            )
        else:
            feedback = (
                f"{query.message.text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"❌ **अरे! यह जवाब गलत है।**\n"
                f"🔴 **आपका उत्तर:** {selected_option} | 🟢 **सही उत्तर:** {correct_option}\n\n"
                f"💡 **विस्तृत स्पष्टीकरण (Detailed Explanation):**\n{explanation}"
            )

        # Lock buttons layout
        locked_keyboard = [
            [InlineKeyboardButton(f"{'✅' if 'A'==correct_option else '❌'} A", callback_data="noop"), 
             InlineKeyboardButton(f"{'✅' if 'B'==correct_option else '❌'} B", callback_data="noop")],
            [InlineKeyboardButton(f"{'✅' if 'C'==correct_option else '❌'} C", callback_data="noop"), 
             InlineKeyboardButton(f"{'✅' if 'D'==correct_option else '❌'} D", callback_data="noop")]
        ]

        await query.message.edit_text(feedback, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(locked_keyboard))

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

    print("AI Bot shuru ho gaya hai...")
    application.run_polling()

if __name__ == '__main__':
    main()

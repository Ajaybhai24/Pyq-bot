import os
import logging
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

# AI se question generate karne ka surakshit tareeqa
def generate_ai_question(subject, lang):
    if not ai_model:
        return {
            "question": f"Sample Question for {subject}",
            "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            "correct": "A",
            "explanation": "This is a default explanation because AI model is not configured properly."
        }
    
    prompt = f"""
    Generate a multiple-choice question (MCQ) for SSC exam on the subject '{subject}' in '{lang}' language.
    Give the output strictly in the following format without extra symbols:
    Q: [Your question here]
    A: [Option A]
    B: [Option B]
    C: [Option C]
    D: [Option D]
    CORRECT: [A, B, C, or D]
    EXP: [Detailed explanation of the answer in {lang}]
    """
    
    try:
        response = ai_model.generate_content(prompt)
        text = response.text.strip()
        
        # Simple line-by-line parsing
        lines = text.split('\n')
        q_data = {"question": "", "options": {}, "correct": "A", "explanation": ""}
        
        for line in lines:
            if line.startswith("Q:"):
                q_data["question"] = line.replace("Q:", "").strip()
            elif line.startswith("A:"):
                q_data["options"]["A"] = line.replace("A:", "").strip()
            elif line.startswith("B:"):
                q_data["options"]["B"] = line.replace("B:", "").strip()
            elif line.startswith("C:"):
                q_data["options"]["C"] = line.replace("C:", "").strip()
            elif line.startswith("D:"):
                q_data["options"]["D"] = line.replace("D:", "").strip()
            elif line.startswith("CORRECT:"):
                q_data["correct"] = line.replace("CORRECT:", "").strip().upper()[:1]
            elif line.startswith("EXP:"):
                q_data["explanation"] = line.replace("EXP:", "").strip()
                
        if not q_data["question"] or not q_data["options"].get("A"):
            raise Exception("Parsing error")
            
        return q_data
    except Exception as e:
        print(f"AI Generation Error: {e}")
        # Subject wise safe fallback
        if "History" in subject:
            return {
                "question": "Who was the founder of the Maurya Empire?",
                "options": {"A": "Ashoka", "B": "Chandragupta Maurya", "C": "Bindusara", "D": "Samudragupta"},
                "correct": "B",
                "explanation": "Chandragupta Maurya founded the Maurya Empire in 322 BCE with the help of Chanakya."
            }
        else:
            return {
                "question": "Which article of the Indian Constitution deals with the Right to Equality?",
                "options": {"A": "Article 14-18", "B": "Article 19-22", "C": "Article 23-24", "D": "Article 25-28"},
                "correct": "A",
                "explanation": "Articles 14 to 18 of the Indian Constitution guarantee the Right to Equality."
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
        "🎯 SSC & Government Exams AI PYQ Bot me aapka swagat hai.\n"
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
        loading_text = "🤖 Generating question..." if lang == "English" else "🤖 AI naya prashn taiyar kar raha hai..."
        loading_msg = await query.message.reply_text(loading_text)

        # Generate AI question
        q_data = generate_ai_question(subject, lang)
        user_data['current_question'] = q_data

        question_box = (
            f"🎯 **Subject: {subject}**\n\n"
            f"❓ **{q_data['question']}**\n\n"
            f"A) {q_data['options'].get('A', '')}\n"
            f"B) {q_data['options'].get('B', '')}\n"
            f"C) {q_data['options'].get('C', '')}\n"
            f"D) {q_data['options'].get('D', '')}"
        )
        
        q_keyboard = [
            [InlineKeyboardButton("A", callback_data="ans_A"), InlineKeyboardButton("B", callback_data="ans_B")],
            [InlineKeyboardButton("C", callback_data="ans_C"), InlineKeyboardButton("D", callback_data="ans_D")]
        ]
        
        try:
            await loading_msg.delete()
        except:
            pass
            
        await query.message.reply_text(question_box, reply_markup=InlineKeyboardMarkup(q_keyboard))

    # 3. Answer Clicked
    elif data.startswith("ans_"):
        selected_option = data.replace("ans_", "")
        q_data = user_data.get('current_question')
        
        if not q_data:
            await query.message.reply_text("Session expired. Please click /start again.")
            return

        correct_option = q_data.get('correct', 'A')
        explanation = q_data.get('explanation', 'No explanation provided.')
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

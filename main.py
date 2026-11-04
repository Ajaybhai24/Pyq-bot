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

# AI se 100% selected subject ke anusaar question generate karne ka function
def generate_ai_question(subject, lang):
    if not ai_model:
        return {
            "question": "Sample Question",
            "options": {"A": "Opt A", "B": "Opt B", "C": "Opt C", "D": "Opt D"},
            "correct": "A",
            "explanation": "Sample explanation."
        }
    
    # Unique seed taaki AI har baar bilkul naya question de
    random_seed = random.randint(10000, 99999)
    
    prompt = f"""
    You are an expert SSC exam question creator. Generate ONE unique, brand-new Previous Year style Multiple Choice Question (MCQ) strictly and exclusively for the subject: '{subject}'. 
    Language requirement: '{lang}'. (Random Seed: {random_seed}).
    Do NOT mix subjects. If the subject is History, question must be from History. If Polity, from Polity.
    The output must strictly follow this exact format with uppercase headers:
    QUESTION: [Write the question text here]
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
        
        lines = text.strip().split('\n')
        q_data = {"question": "", "options": {}, "correct": "A", "explanation": ""}
        
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
                
        if not q_data["question"] or not q_data["options"].get("A"):
            raise Exception("AI Parsing incomplete")
            
        return q_data
    except Exception as e:
        print(f"AI Error: {e}")
        # Subject-wise smart fallback
        sub_lower = subject.lower()
        if "history" in sub_lower:
            return {
                "question": "Who was the founder of the Maurya Empire?",
                "options": {"A": "Ashoka", "B": "Chandragupta Maurya", "C": "Bindusara", "D": "Samudragupta"},
                "correct": "B",
                "explanation": "Chandragupta Maurya founded the Maurya Empire in 322 BCE."
            }
        elif "polity" in sub_lower:
            return {
                "question": "Which article of the Indian Constitution deals with the Right to Equality?",
                "options": {"A": "Article 14-18", "B": "Article 19-22", "C": "Article 23-24", "D": "Article 25-28"},
                "correct": "A",
                "explanation": "Articles 14 to 18 guarantee the Right to Equality."
            }
        elif "current" in sub_lower:
            return {
                "question": "Recent important national event related question placeholder.",
                "options": {"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"},
                "correct": "A",
                "explanation": "Explanation for current affairs question."
            }
        else:
            return {
                "question": "Which is the highest civilian award in India?",
                "options": {"A": "Padma Vibhushan", "B": "Bharat Ratna", "C": "Padma Bhushan", "D": "Ashok Chakra"},
                "correct": "B",
                "explanation": "Bharat Ratna is the highest civilian award of the Republic of India."
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
        f"👋 Namaste {user_name} ji!\n\n"
        "🎯 SSC & Government Exams AI PYQ Bot me aapka swagat hai.\n"
        "Kripya apni bhasha (Preferred Language) chunein:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

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
            sub_text = "📚 **Vishay Chayan (Subject Selection):**\n\nAI practice ke liye niche diye gaye vishayon me se chunein:"
            buttons = [
                [InlineKeyboardButton("📖 Itihas (History)", callback_data="sub_History")],
                [InlineKeyboardButton("⚖️ Bharatiya Rajvyavastha (Indian Polity)", callback_data="sub_Indian Polity")],
                [InlineKeyboardButton("🔥 Current Affairs", callback_data="sub_Current Affairs")],
                [InlineKeyboardButton("💡 Static GK", callback_data="sub_Static GK")]
            ]
        else:
            sub_text = "📚 **Subject Selection:**\n\nPlease choose a subject for AI practice:"
            buttons = [
                [InlineKeyboardButton("📖 History", callback_data="sub_History")],
                [InlineKeyboardButton("⚖️ Indian Polity", callback_data="sub_Indian Polity")],
                [InlineKeyboardButton("🔥 Current Affairs", callback_data="sub_Current Affairs")],
                [InlineKeyboardButton("💡 Static GK", callback_data="sub_Static GK")]
            ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(sub_text, parse_mode='Markdown', reply_markup=reply_markup)

    # 2. Subject Selected or Next Question Clicked -> Generate AI Question
    elif data.startswith("sub_") or data == "next_q":
        if data.startswith("sub_"):
            subject = data.replace("sub_", "")
            user_data['subject'] = subject
            try:
                await query.message.delete()
            except:
                pass
        else:
            subject = user_data.get('subject', 'History')
            try:
                await query.message.delete()
            except:
                pass

        lang = user_data.get('language', 'English')
        
        loading_text = f"🤖 AI is generating a fresh {subject} question..." if lang == "English" else f"🤖 AI {subject} ka naya prashn taiyar kar raha hai..."
        loading_msg = await query.message.reply_text(loading_text)

        # AI question generation with strict subject passing
        q_data = generate_ai_question(subject, lang)
        user_data['current_question'] = q_data

        # Clean question layout
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
        
        await loading_msg.delete()
        await query.message.reply_text(question_box, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(q_keyboard))

    # 3. Answer Clicked -> Lock options and send separate explanation message
    elif data.startswith("ans_"):
        selected_option = data.replace("ans_", "")
        q_data = user_data.get('current_question')
        
        if not q_data:
            await query.message.reply_text("Session expired. Please click /start again.")
            return

        correct_option = q_data['correct']
        explanation = q_data['explanation']
        lang = user_data.get('language', 'English')

        # Lock buttons layout with correct/incorrect markers
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

        # Separate Explanation Message in selected language with Next Button
        if lang == "Hindi":
            exp_text = (
                f"✍️ **Aapka Uttar:** {selected_option} | 🟢 **Sahi Uttar:** {correct_option}\n\n"
                f"💡 **Vistrit Spashtikaran (Detailed Explanation):**\n{explanation}"
            )
            next_btn_text = "➡️ Agla Prashn (Next Question)"
        else:
            exp_text = (
                f"✍️ **Your Answer:** {selected_option} | 🟢 **Correct Answer:** {correct_option}\n\n"
                f"💡 **Detailed Explanation:**\n{explanation}"
            )
            next_btn_text = "➡️ Next Question"

        next_keyboard = [[InlineKeyboardButton(next_btn_text, callback_data="next_q")]]
        
        await query.message.reply_text(exp_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(next_keyboard))

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

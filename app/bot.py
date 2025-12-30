
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from app.gemini_client import GeminiClient
from app.document_processor import DocumentProcessor

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize clients
gemini_client = GeminiClient()
doc_processor = DocumentProcessor()

# Constants
DISCLAIMER = "\n\n⚠️ *Disclaimer*: This is legal information, not legal advice. Consult a licensed lawyer."

# --- Helper Logic for Intent Detection ---
def detect_intent(text: str) -> str:
    text = text.lower()
    
    # Explain a Law
    if any(k in text for k in ["section", "ipc", "act", "article", "law"]):
        return "explain_law"
    
    # Case Assistance
    if any(k in text for k in ["my case", "help", "win", "defend", "strength", "weakness"]):
        return "case_assist"
    
    # Language
    if any(k in text for k in ["hindi", "english", "telugu", "tamil", "urdu", "language"]):
        return "change_lang"

    # FAQ or General Legal Question
    if text.endswith("?") or len(text.split()) < 10: 
        return "faq"
    
    return "general_query"

# --- Handler Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Hello {user_first_name}! 👋\n\n"
        "I am your **Legal Information Assistant**. 🤖\n"
        "I can help you with:\n"
        "🔹 Explaining Laws\n"
        "🔹 Analyzing Case Files\n"
        "🔹 Case Strategy Assistance\n\n"
        "*I do NOT provide legal advice.*\n\n"
        "Select an option or just type your question:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📘 Explain a Law", callback_data='intent_explain_law')],
        [InlineKeyboardButton("📂 Upload Case File", callback_data='intent_upload_case')],
        [InlineKeyboardButton("⚖️ Case Assistance", callback_data='intent_case_assist')],
        [InlineKeyboardButton("🌐 Change Language", callback_data='intent_change_lang')],
        [InlineKeyboardButton("❓ Legal FAQ", callback_data='intent_faq')],
        [InlineKeyboardButton("🔒 Privacy Policy", callback_data='intent_privacy')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(welcome_text, reply_markup=reply_markup)

# Button Router
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Set context state based on button
    context.user_data['active_intent'] = data
    
    if data == 'intent_explain_law':
        await query.edit_message_text("Use /law <name> or just type the law name here (e.g. 'IPC 420').")
    elif data == 'intent_upload_case':
        await query.edit_message_text("Please upload your case document (PDF, DOCX, or Image) now.")
    elif data == 'intent_case_assist':
        await query.edit_message_text("I can help analyze your case strategy. Briefly describe your situation or ask 'How can I strengthen my case?'.")
    elif data == 'intent_change_lang':
        await query.edit_message_text("Please type your preferred language (e.g. 'Hindi', 'Telugu').")
    elif data == 'intent_faq':
        await query.edit_message_text("Ask me a short legal question, or type 'FAQ' to see common ones.")
    elif data == 'intent_privacy':
        await privacy_command(update, context)

# Text Handler (The Main Router)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_msg = update.message.text
    if user_msg.startswith("/"): return 
    
    # 1. Check Context State (from button clicks)
    active_intent = context.user_data.get('active_intent')
    
    # 2. If no active state, detect intent from text
    if not active_intent:
        active_intent = detect_intent(user_msg)
        # Map detected simple intent string to full intent key (optional, or just use identifying string)
        if active_intent == "explain_law": active_intent = 'intent_explain_law'
        elif active_intent == "case_assist": active_intent = 'intent_case_assist'
        elif active_intent == "change_lang": active_intent = 'intent_change_lang'
        elif active_intent == "faq": active_intent = 'intent_faq'
    
    # 3. Reset state for next interaction (optional, depending on flow. For now, we reset after processing)
    context.user_data['active_intent'] = None 

    status_msg = await update.message.reply_text("🔍 Processing...")

    # Route based on detected or set intent
    if active_intent == 'intent_explain_law':
        await process_explanation(update, context, user_msg, status_msg)
    elif active_intent == 'intent_case_assist':
        await process_case_assistance(update, context, user_msg, status_msg)
    elif active_intent == 'intent_change_lang':
        await process_language_change(update, context, user_msg, status_msg)
    elif active_intent == 'intent_faq':
        # Pass FAQ input to Gemini as requested
        await process_explanation(update, context, f"Answer this Legal FAQ briefly: {user_msg}", status_msg)
    else:
        # Fallback mechanism: Treat as general legal query
        await process_explanation(update, context, user_msg, status_msg)

async def process_explanation(update, context, query, status_msg):
    try:
        user_lang = context.user_data.get('language')
        response = gemini_client.get_legal_explanation(query, language=user_lang)
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text=response + DISCLAIMER
        )
    except Exception as e:
        await handle_error(update, context, status_msg, e)

async def process_case_assistance(update, context, query, status_msg):
    try:
        # Custom prompt for case assistance: "provide suggestion and help user to win"
        prompt = f"""User Request for Case Assistance: "{query}"

Please act as a Legal Strategy Assistant.
Provide:
1. Evaluation of the situation.
2. Strategic suggestions to win or strengthen the case.
3. Relevant laws that support this position.
4. Evidence that should be gathered.

Keep it practical and actionable.
"""
        # Call internal method to allow custom prompt
        user_lang = context.user_data.get('language')
        response = gemini_client._call_gemini(prompt, language=user_lang)
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text=response + DISCLAIMER
        )
    except Exception as e:
        await handle_error(update, context, status_msg, e)

async def process_language_change(update, context, lang, status_msg):
    # Store language preference (mock session for now)
    context.user_data['language'] = lang
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=status_msg.message_id,
        text=f"✅ Language set to: {lang}. I will try to answer in {lang} from now on."
    )

async def handle_error(update, context, status_msg, e):
    logger.error(f"Processing error: {e}", exc_info=True)
    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id, 
            message_id=status_msg.message_id, 
            text=f"⚠️ Error: {str(e)}"
        )
    except:
        pass

# Document Handler (File -> Upload Case File Intent)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document or update.message.photo[-1]
    is_image = bool(update.message.photo)
    
    if is_image:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_name = "image.png"
        file_ext = ".png"
    else:
        file = await context.bot.get_file(update.message.document.file_id)
        file_name = update.message.document.file_name
        _, file_ext = os.path.splitext(file_name)

    status_msg = await update.message.reply_text(f"🔍 Received {file_name}. Analyzing content...")
    
    try:
        f_byte_array = await file.download_as_bytearray()
        content = doc_processor.process_file(f_byte_array, file_ext)
        
        if not content or len(content) < 10:
             await context.bot.edit_message_text(
                chat_id=update.effective_chat.id, 
                message_id=status_msg.message_id, 
                text="⚠️ Could not extract text. File might be empty/unreadable."
             )
             return
        
        user_lang = context.user_data.get('language')
        analysis = gemini_client.analyze_document(content, doc_type="Case Document", language=user_lang)
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id, 
            message_id=status_msg.message_id, 
            text="Analysis Complete. Summary below:"
        )
        await update.message.reply_text(analysis + DISCLAIMER)
            
    except Exception as e:
        await handle_error(update, context, status_msg, e)

# Legacy Commands (kept for direct access)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = "**User Guide**\nUse the buttons or type natural queries like 'Explain IPC 302' or 'Help with my case'."
    await update.message.reply_markdown(help_text)

async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🔒 *Privacy Policy – Legal Tune Bot*\n\n"
        "We respect your privacy and are committed to protecting your data.\n\n"
        "*1. Data Collection*\n"
        "We do NOT store personal information\n"
        "Messages are processed only to generate responses\n"
        "Uploaded files are used temporarily for analysis and are not saved\n\n"
        "*2. Use of Information*\n"
        "Information is used only to explain laws and legal procedures\n"
        "No data is shared with third parties\n\n"
        "*3. AI Usage*\n"
        "This bot uses AI to provide legal information\n"
        "AI responses are informational only, not legal advice\n\n"
        "*4. Data Security*\n"
        "We do not maintain databases of user conversations\n"
        "Temporary processing is done securely\n\n"
        "*5. Legal Disclaimer*\n"
        "This bot provides legal information, not legal advice.\n"
        "Always consult a licensed lawyer for legal matters.\n\n"
        "*6. Policy Updates*\n"
        "This privacy policy may be updated without prior notice."
    )
    # Use effective_message to handle both Commands and CallbackQueries
    await update.effective_message.reply_markdown(text)

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "**Legal FAQ** ❓\n\n1. Is this advice? No.\n2. Predictions? No."
    await update.message.reply_markdown(text)

async def law_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        status_msg = await update.message.reply_text("🔍 Analyzing...")
        await process_explanation(update, context, " ".join(context.args), status_msg)
    else:
        await update.message.reply_text("Usage: /law <name>")

async def case_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please upload your document.")
    context.user_data['active_intent'] = 'intent_upload_case'

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Type your language name now.")
    context.user_data['active_intent'] = 'intent_change_lang'

# Global Error Handler
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .build()
    )

    application.add_error_handler(global_error_handler)

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("privacy", privacy_command))
    application.add_handler(CommandHandler("faq", faq_command))
    application.add_handler(CommandHandler("law", law_command))
    application.add_handler(CommandHandler("case", case_command))
    application.add_handler(CommandHandler("language", language_command))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()

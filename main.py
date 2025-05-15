import os
import logging
from deep_translator import GoogleTranslator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import InvalidToken

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot"""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha -> 🇷🇺 Ruscha", callback_data='uz-ru'),
            InlineKeyboardButton("🇷🇺 Ruscha -> 🇺🇿 O'zbekcha", callback_data='ru-uz')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"Assalomu alaykum, {user.mention_html()}! 👋\n\n"
        f"Men O'zbekcha-Ruscha tarjimon botman. Tarjima yo'nalishini tanlang:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    direction = query.data
    context.user_data['direction'] = direction
    
    if direction == 'uz-ru':
        message = "O'zbekcha -> Ruscha tarjima rejimi tanlandi. O'zbekcha matn yuboring."
    else:
        message = "Ruscha -> O'zbekcha tarjima rejimi tanlandi. Ruscha matn yuboring."
    
    await query.edit_message_text(text=message)

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate the sent text"""
    if 'direction' not in context.user_data:
        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 O'zbekcha -> 🇷🇺 Ruscha", callback_data='uz-ru'),
                InlineKeyboardButton("🇷🇺 Ruscha -> 🇺🇿 O'zbekcha", callback_data='ru-uz')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Iltimos, avval tarjima yo'nalishini tanlang:",
            reply_markup=reply_markup
        )
        return
    
    direction = context.user_data['direction']
    text = update.message.text
    
    try:
        if direction == 'uz-ru':
            translator = GoogleTranslator(source='uz', target='ru')
        else:
            translator = GoogleTranslator(source='ru', target='uz')
        
        translated_text = translator.translate(text)
        await update.message.reply_text(f"🔄 Tarjima:\n\n{translated_text}")
    except Exception as e:
        logger.error(f"Tarjima xatosi: {e}")
        await update.message.reply_text(
            "Tarjima vaqtida xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = (
        "📝 *O'zbekcha-Ruscha tarjimon bot haqida*\n\n"
        "Botdan foydalanish uchun qo'llanma:\n"
        "1. /start - Botni ishga tushirish\n"
        "2. Tarjima yo'nalishini tanlang\n"
        "3. Tarjima qilmoqchi bo'lgan matningizni yuboring\n\n"
        "Yo'nalishni o'zgartirish uchun /start buyrug'ini qayta ishlating.\n"
        "Yordam uchun /help buyrug'ini ishlating."
    )
    await update.message.reply_markdown(help_text)

def main():
    """Run the bot"""
    # Read the token from environment variable
    token = os.getenv("TELEGRAM_TOKEN")
    
    # Check if token is valid
    if not token or token.strip() == "":
        print("XATOLIK: TELEGRAM_TOKEN muhit o'zgaruvchisi topilmadi yoki bo'sh!")
        print("1. Telegram BotFather orqali bot yarating va token oling.")
        print("2. Tokenni .env fayliga qo'shing yoki muhit o'zgaruvchisi sifatida sozlang.")
        print("Misol: export TELEGRAM_TOKEN=your_bot_token_here")
        print("3. Agar Docker ishlatayotgan bo'lsangiz, docker-compose.yml yoki .env faylida tokenni sozlang.")
        return
    
    # Initialize the application
    try:
        application = Application.builder().token(token).build()
    except InvalidToken as e:
        print(f"XATOLIK: Yaroqsiz token! {e}")
        print("Iltimos, BotFather dan olingan to'g'ri tokenni ishlatganingizga ishonch hosil qiling.")
        return
    except Exception as e:
        print(f"XATOLIK: Botni ishga tushirishda xato yuz berdi: {e}")
        return
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    
    # Start the bot
    print("Bot ishga tushdi...")
    try:
        application.run_polling()
    except Exception as e:
        print(f"XATOLIK: Bot polling jarayonida xato yuz berdi: {e}")

if __name__ == '__main__':
    main()

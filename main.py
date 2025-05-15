import os
import logging
from googletrans import Translator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Logni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tarjimon klassi
translator = Translator()

# Funksiyalar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni ishga tushirish komandasi"""
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
    """Tugmalar bosilganda ishlaydigan funksiya"""
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
    """Yuborilgan matnni tarjima qilish"""
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
            src, dest = 'uz', 'ru'
        else:
            src, dest = 'ru', 'uz'
        
        translated = translator.translate(text, src=src, dest=dest)
        await update.message.reply_text(f"🔄 Tarjima:\n\n{translated.text}")
    except Exception as e:
        logger.error(f"Tarjima xatosi: {e}")
        await update.message.reply_text(
            "Tarjima vaqtida xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam xabarini ko'rsatish"""
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
    """Botni ishga tushirish"""
    # TOKEN ni o'qish
    token = os.getenv("TELEGRAM_TOKEN")
    
    # Applicationni sozlash
    application = Application.builder().token(token).build()
    
    # Handler qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    
    # Botni ishga tushirish
    application.run_polling()

if __name__ == '__main__':
    main()

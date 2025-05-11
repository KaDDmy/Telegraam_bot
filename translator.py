import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from deep_translator import GoogleTranslator

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения направлений перевода для каждого пользователя
user_languages = {}

# Клавиатура для выбора направления перевода
language_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Русский → Английский")],
        [KeyboardButton("Английский → Русский")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-переводчик.\n"
        "Пожалуйста, выберите направление перевода:",
        reply_markup=language_keyboard,
    )

# Установка направления перевода
async def set_language_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "Русский → Английский":
        user_languages[user_id] = ("russian", "english")
        await update.message.reply_text("Вы выбрали перевод с русского на английский. Введите текст.")
    elif text == "Английский → Русский":
        user_languages[user_id] = ("english", "russian")
        await update.message.reply_text("Вы выбрали перевод с английского на русский. Введите текст.")
    else:
        await update.message.reply_text("Пожалуйста, выберите направление перевода через клавиатуру.")

# Перевод текста
async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_languages:
        await update.message.reply_text("Сначала выберите направление перевода: /start")
        return

    source_lang, target_lang = user_languages[user_id]

    try:
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        await update.message.reply_text(translated)
    except Exception as e:
        logger.error(f"Ошибка перевода: {e}")
        await update.message.reply_text("Произошла ошибка при переводе.")

# Основной запуск
def main():
    application = Application.builder().token('TOKEN').build()

    language_options = ["Русский → Английский", "Английский → Русский"]
    language_filter = filters.TEXT & filters.Regex(f"^({'|'.join(language_options)})$")
    text_filter = filters.TEXT & ~filters.COMMAND & ~language_filter

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(language_filter, set_language_direction))
    application.add_handler(MessageHandler(text_filter, translate_text))

    application.run_polling()

if __name__ == "__main__":
    main()
    # для роботы программы установите: pip install deep-translator
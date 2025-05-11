import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
QUESTION_CITY, QUESTION_WEATHER = range(2)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос командой /stop, или пропустить вопрос командой /skip.\n"
        "В каком городе вы живёте?"
    )
    return QUESTION_CITY


# Ответ на вопрос о городе
async def first_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locality = update.message.text
    context.user_data["city"] = locality
    await update.message.reply_text(f"Какая погода в городе {locality}?")
    return QUESTION_WEATHER


# Обработка /skip — пропуск вопроса о городе
async def skip_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = None
    await update.message.reply_text("Какая погода у вас за окном?")
    return QUESTION_WEATHER


# Ответ на второй вопрос
async def second_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weather = update.message.text
    city = context.user_data.get("city")
    if city:
        logger.info(f"Погода в {city}: {weather}")
    else:
        logger.info(f"Погода без указания города: {weather}")
    await update.message.reply_text("Спасибо за участие в опросе! Всего доброго!")
    return ConversationHandler.END


# Прерывание диалога
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос прерван. Всего доброго!")
    return ConversationHandler.END


# Основной запуск
def main():
    application = Application.builder().token('TOKEN').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, first_response),
                CommandHandler("skip", skip_city),
            ],
            QUESTION_WEATHER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, second_response),
            ],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

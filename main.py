import logging
import random
import asyncio
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackContext,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Словарь для хранения таймеров
user_timers = {}

# Клавиатуры
start_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("/dice")], [KeyboardButton("/timer")]], resize_keyboard=True
)

dice_keyboard = ReplyKeyboardMarkup(
    [
        ["кинуть один шестигранный кубик"],
        ["кинуть 2 шестигранных кубика одновременно"],
        ["кинуть 20-гранный кубик"],
        ["вернуться назад"],
    ],
    resize_keyboard=True,
)

timer_keyboard = ReplyKeyboardMarkup(
    [
        ["30 секунд", "1 минута"],
        ["5 минут"],
        ["вернуться назад"],
    ],
    resize_keyboard=True,
)

close_keyboard = ReplyKeyboardMarkup(
    [["/close"]], resize_keyboard=True
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Выберите опцию:",
        reply_markup=start_keyboard,
    )


# /dice
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите тип броска:", reply_markup=dice_keyboard)


# /timer
async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите таймер:", reply_markup=timer_keyboard)


# /close
async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task = user_timers.pop(user_id, None)
    if task:
        task.cancel()
        await update.message.reply_text("Таймер сброшен.", reply_markup=start_keyboard)
    else:
        await update.message.reply_text("Нет активного таймера.", reply_markup=start_keyboard)


# Обработка нажатий кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "кинуть один шестигранный кубик":
        result = random.randint(1, 6)
        await update.message.reply_text(f"Результат: {result}", reply_markup=dice_keyboard)

    elif text == "кинуть 2 шестигранных кубика одновременно":
        result1, result2 = random.randint(1, 6), random.randint(1, 6)
        await update.message.reply_text(f"Результаты: {result1}, {result2}", reply_markup=dice_keyboard)

    elif text == "кинуть 20-гранный кубик":
        result = random.randint(1, 20)
        await update.message.reply_text(f"Результат: {result}", reply_markup=dice_keyboard)

    elif text == "30 секунд":
        await set_user_timer(update, context, user_id, 30, "30 секунд")

    elif text == "1 минута":
        await set_user_timer(update, context, user_id, 60, "1 минута")

    elif text == "5 минут":
        await set_user_timer(update, context, user_id, 300, "5 минут")

    elif text == "вернуться назад":
        await update.message.reply_text("Вы вернулись назад.", reply_markup=start_keyboard)

    else:
        await update.message.reply_text("Я не понимаю эту команду.")


async def set_user_timer(update, context, user_id, delay, label):
    await update.message.reply_text(f"Засек {label}.", reply_markup=close_keyboard)

    async def timer_task():
        try:
            await asyncio.sleep(delay)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{label} истекло.")
            await update.message.reply_text("Выберите таймер:", reply_markup=timer_keyboard)
        except asyncio.CancelledError:
            pass

    # Сброс предыдущего таймера
    task = user_timers.pop(user_id, None)
    if task:
        task.cancel()

    # Установка нового
    task = asyncio.create_task(timer_task())
    user_timers[user_id] = task



# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


# /time
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"Текущее время: {now}")


# /date
async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%d.%m.%Y")
    await update.message.reply_text(f"Сегодняшняя дата: {today}")


# /set_timer
async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        delay = int(context.args[0])
        await update.message.reply_text(f"Таймер установлен на {delay} секунд.")

        await asyncio.sleep(delay)
        await update.message.reply_text(f"Время вышло! Прошло {delay} секунд.")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажите время в секундах. Пример: /set_timer 5")


# echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_text = update.message.text
    response = f"Я получил сообщение: {received_text}"
    await update.message.reply_text(response)


# main
def main():
    application = Application.builder().token('TOKEN').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("close", close))

    button_texts = {
        "кинуть один шестигранный кубик",
        "кинуть 2 шестигранных кубика одновременно",
        "кинуть 20-гранный кубик",
        "30 секунд",
        "1 минута",
        "5 минут",
        "вернуться назад"
    }

    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(button_texts)})$"), handle_buttons))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()

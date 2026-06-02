import telebot
from telebot import types
import json

TOKEN = "5957429587:AAENoaAxpuHIuazy596V5mX_nQGgepu8xCg"

bot = telebot.TeleBot(TOKEN)

CHANNEL_ID = -1003702701562

user_codes = {}


def load_films():
    try:
        with open("films.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False


@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.add(
        types.KeyboardButton(
            "🎬 Найти фильм по коду"
        )
    )

    bot.send_message(
        message.chat.id,
        "Введите код фильма через кнопку ниже.",
        reply_markup=markup
    )


@bot.message_handler(content_types=['text'])
def text_handler(message):

    if message.text == "🎬 Найти фильм по коду":

        msg = bot.send_message(
            message.chat.id,
            "Введите код фильма:"
        )

        bot.register_next_step_handler(
            msg,
            input_code
        )


def input_code(message):

    films = load_films()

    code = message.text.strip()

    if code == "200":

        bot.send_sticker(
            message.chat.id,
            "CAACAgIAAxkBAAERTz5qHNbR8dRs3KAeQ56KCvHEwDv5tAACZ3AAAqrJkUsI15rBHAw1ITsE"
        )

        return
    film = films.get(code)

    if not film:
        bot.send_message(
            message.chat.id,
            "❌ Фильм не найден."
        )
        return

    user_codes[message.from_user.id] = code

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎬 Получить название фильма",
            callback_data="get_movie"
        )
    )

    bot.send_message(
        message.chat.id,
        "✅ Код найден.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_movie")
def get_movie(call):

    user_id = call.from_user.id

    if not check_subscription(user_id):

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "Подписаться",
                url="https://t.me/+ndaKkWZY28NiMzJi"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "❌ Для получения фильма подпишитесь на канал.",
            reply_markup=markup
        )

        return

    code = user_codes.get(user_id)

    if not code:
        bot.send_message(
            call.message.chat.id,
            "Введите код заново."
        )
        return

    films = load_films()

    film = films.get(code)

    if not film:
        bot.send_message(
            call.message.chat.id,
            "Фильм не найден."
        )
        return

    text = (
        f"🎬 Название: {film['title']}\n\n"
        f"📝 Описание:\n{film['description']}"
    )

    bot.send_message(
        call.message.chat.id,
        text
    )


print("Основной бот запущен...")
bot.infinity_polling(skip_pending=True)

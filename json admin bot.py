import telebot
from telebot import types
import json
from telebot.apihelper import ApiTelegramException

# ==========================
# НАСТРОЙКИ
# ==========================

TOKEN = "8986853338:AAEPb2lEVXW7Bstb0Gg1udr3M8njVMABxqI"

ADMINS = [1024857184, 1702740121] 

bot = telebot.TeleBot(TOKEN)

user_data = {}

MENU_BUTTONS = [
    "➕ Добавить фильм",
    "✏️ Изменить фильм",
    "❌ Удалить фильм",
    "📋 Список фильмов",
    "🚫 Отмена"
]

TOPIC_CHAT_ID = -1003904537992
TOPIC_ID = 8
LIST_MESSAGE_ID = 23


''' 
# ==========================
# ПРОВЕРКА ТОПИКА И НОВЕРА ЧАТА
# ==========================

@bot.message_handler(func=lambda message: True)
def debug(message):

    print("CHAT ID:", message.chat.id)
    print("TOPIC ID:", message.message_thread_id)
'''



# ==========================
# JSON
# ==========================

def load_films():
    try:
        with open("films.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_films(films):
    with open(
        "films.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            films,
            f,
            ensure_ascii=False,
            indent=4
        )

# ==========================
# ПРОВЕРКА АДМИНА
# ==========================

def is_admin(user_id):
    return user_id in ADMINS

# ==========================
# МЕНЮ
# ==========================

def admin_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("➕ Добавить фильм"),
        types.KeyboardButton("✏️ Изменить фильм")
    )

    markup.add(
        types.KeyboardButton("❌ Удалить фильм"),
        types.KeyboardButton("📋 Список фильмов")
    )

    markup.add(
        types.KeyboardButton("🚫 Отмена")
    )

    return markup

# ==========================
# СТАРТ
# ==========================

@bot.message_handler(commands=["start"])
def start(message):

    if not is_admin(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "⛔ Доступ запрещён."
        )

        return

    bot.send_message(
        message.chat.id,
        "🎬 Панель администратора",
        reply_markup=admin_menu()
    )


@bot.message_handler(commands=['info'])
def info(message):

    bot.send_message(
        message.chat.id,
        f"""
Chat ID: {message.chat.id}

Topic ID: {message.message_thread_id}
"""
    )
    
# ==========================
# ОТМЕНА
# ==========================

def cancel_process(message):

    user_data.pop(
        message.from_user.id,
        None
    )

    bot.send_message(
        message.chat.id,
        "✅ Действие отменено.",
        reply_markup=admin_menu()
    )

# ==========================
# ОСНОВНОЕ МЕНЮ
# ==========================

@bot.message_handler(content_types=["text"])
def text_handler(message):

    if not is_admin(message.from_user.id):
        return

    if message.text == "🚫 Отмена":

        cancel_process(message)
        return

    elif message.text == "➕ Добавить фильм":

        msg = bot.send_message(
            message.chat.id,
            "Введите код фильма:"
        )

        bot.register_next_step_handler(
            msg,
            get_code
        )

    elif message.text == "✏️ Изменить фильм":

        msg = bot.send_message(
            message.chat.id,
            "Введите код фильма для изменения:"
        )

        bot.register_next_step_handler(
            msg,
            edit_film_code
        )

    elif message.text == "❌ Удалить фильм":

        msg = bot.send_message(
            message.chat.id,
            "Введите код фильма для удаления:"
        )

        bot.register_next_step_handler(
            msg,
            delete_film
        )

    elif message.text == "📋 Список фильмов":

        films = load_films()

        if not films:

            bot.send_message(
                message.chat.id,
                "📭 База фильмов пуста."
            )

            return

        text = "📋 Список фильмов:\n\n"

        for code, film in films.items():
            text += f"🔢 {code} — {film['title']}\n"

        bot.send_message(
            message.chat.id,
            text
        )

# ==========================
# ДОБАВЛЕНИЕ ФИЛЬМА
# ==========================

def get_code(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    code = message.text.strip()

    if code in MENU_BUTTONS:

        msg = bot.send_message(
            message.chat.id,
            "❌ Введите настоящий код фильма."
        )

        bot.register_next_step_handler(msg, get_code)
        return

    if not code.isdigit():

        msg = bot.send_message(
            message.chat.id,
            "❌ Код должен содержать только цифры."
        )

        bot.register_next_step_handler(msg, get_code)
        return

    films = load_films()

    if code in films:

        bot.send_message(
            message.chat.id,
            "❌ Такой код уже существует."
        )

        return

    user_data[message.from_user.id] = {
        "code": code
    }

    msg = bot.send_message(
        message.chat.id,
        "Введите название фильма:"
    )

    bot.register_next_step_handler(
        msg,
        get_title
    )


def get_title(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    title = message.text.strip()

    if title in MENU_BUTTONS:

        msg = bot.send_message(
            message.chat.id,
            "❌ Введите название фильма."
        )

        bot.register_next_step_handler(msg, get_title)
        return

    if len(title) < 2:

        msg = bot.send_message(
            message.chat.id,
            "❌ Название слишком короткое."
        )

        bot.register_next_step_handler(msg, get_title)
        return

    user_data[message.from_user.id]["title"] = title

    msg = bot.send_message(
        message.chat.id,
        "Введите описание фильма:"
    )

    bot.register_next_step_handler(
        msg,
        get_description
    )


def get_description(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    description = message.text.strip()

    if description in MENU_BUTTONS:

        msg = bot.send_message(
            message.chat.id,
            "❌ Введите описание фильма."
        )

        bot.register_next_step_handler(msg, get_description)
        return

    if len(description) < 10:

        msg = bot.send_message(
            message.chat.id,
            "❌ Описание слишком короткое."
        )

        bot.register_next_step_handler(msg, get_description)
        return

    data = user_data[message.from_user.id]

    films = load_films()

    films[data["code"]] = {
        "title": data["title"],
        "description": description
    }

    save_films(films)
    update_films_post()

    bot.send_message(
        message.chat.id,
        f"✅ Фильм добавлен\n\n"
        f"🎬 {data['title']}\n"
        f"🔢 Код: {data['code']}",
        reply_markup=admin_menu()
    )

    user_data.pop(
        message.from_user.id,
        None
    )


# ==========================
# ВЫВОД СПИСКА ФИЛЬМОВ В ЧАТ
# ==========================

def build_films_text():

    films = load_films()

    text = "🎬 Список фильмов\n\n"

    if not films:
        return text + "Список пуст."

    for code, film in sorted(films.items()):

        text += (
            f"🔢 {code}\n"
            f"🎥 {film['title']}\n\n"
        )

    return text

def update_films_post():

    text = build_films_text()

    try:

        bot.edit_message_text(
            chat_id=TOPIC_CHAT_ID,
            message_id=LIST_MESSAGE_ID,
            text=text
        )

    except ApiTelegramException as e:

        if "message is not modified" in str(e):
            return

        print("Ошибка обновления сообщения:", e)
# ==========================
# УДАЛЕНИЕ
# ==========================

def delete_film(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    code = message.text.strip()

    films = load_films()

    if code not in films:

        bot.send_message(
            message.chat.id,
            "❌ Фильм не найден."
        )

        return

    title = films[code]["title"]

    del films[code]

    save_films(films)
    update_films_post()

    bot.send_message(
        message.chat.id,
        f"✅ Удалён фильм:\n🎬 {title}",
        reply_markup=admin_menu()
    )

# ==========================
# РЕДАКТИРОВАНИЕ
# ==========================

def edit_film_code(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    code = message.text.strip()

    films = load_films()

    if code not in films:

        bot.send_message(
            message.chat.id,
            "❌ Фильм не найден."
        )

        return

    user_data[message.from_user.id] = {
        "edit_code": code
    }

    msg = bot.send_message(
        message.chat.id,
        "Введите новое название:"
    )

    bot.register_next_step_handler(
        msg,
        edit_film_title
    )


def edit_film_title(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    title = message.text.strip()

    if title in MENU_BUTTONS:

        msg = bot.send_message(
            message.chat.id,
            "❌ Введите название фильма."
        )

        bot.register_next_step_handler(
            msg,
            edit_film_title
        )

        return

    user_data[message.from_user.id]["title"] = title

    msg = bot.send_message(
        message.chat.id,
        "Введите новое описание:"
    )

    bot.register_next_step_handler(
        msg,
        edit_film_description
    )


def edit_film_description(message):

    if message.text == "🚫 Отмена":
        cancel_process(message)
        return

    data = user_data[message.from_user.id]

    films = load_films()

    films[data["edit_code"]] = {
        "title": data["title"],
        "description": message.text.strip()
    }

    save_films(films)
    update_films_post()

    bot.send_message(
        message.chat.id,
        "✅ Фильм успешно изменён.",
        reply_markup=admin_menu()
    )

    user_data.pop(
        message.from_user.id,
        None
    )

# ==========================
# ЗАПУСК
# ==========================

print("Админ бот запущен...")

bot.infinity_polling(skip_pending=True)

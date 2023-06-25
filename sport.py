import telebot
import pickle
from telebot import types

bot = telebot.TeleBot('6157269191:AAH72mQK-rleahK-XWHf4NxSzBxIYGvWzao')

# Словарь для хранения информации о проголосовавших
voters = {}

# Функция сохранения информации в файл
def save_voters():
    with open('voters.pkl', 'wb') as f:
        pickle.dump(voters, f)

# Функция загрузки информации из файла (если есть)
def load_voters():
    try:
        with open('voters.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

# Загружаем информацию о проголосовавших (если есть)
voters = load_voters()

# Определение вариантов спорта
sport_options = {
    'Футбол': 'football',
    'Волейбол': 'volleyball',
    'Баскетбол': 'basketball',
    'Теннис': 'tennis'
}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем кнопку "Начать"
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Начать", callback_data='start')
    keyboard.add(button)

    # Отправляем приветственное сообщение с кнопкой
    bot.send_message(message.chat.id, 'Привет! Нажми на кнопку "Начать", чтобы продолжить.', reply_markup=keyboard)

# Обработчик команды /clear
@bot.message_handler(commands=['clear'])
def clear_cache(message):
    global voters
    voters = {}
    save_voters()
    bot.send_message(message.chat.id, 'Кэш очищен.')

# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.send_message(message.chat.id, 'Бот остановлен.')
    bot.stop_polling()

# Обработчик нажатия на кнопку
@bot.callback_query_handler(func=lambda call: call.data == 'start')
def button_click(call):
    # Создаем кнопки для выбора вида спорта
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for sport in sport_options:
        button = types.InlineKeyboardButton(sport, callback_data=sport)
        keyboard.add(button)

    # Отправляем опросное сообщение с кнопками выбора спорта
    bot.send_message(call.message.chat.id, 'Каким спортом займемся?', reply_markup=keyboard)

# Обработчик нажатия на кнопку выбора спорта
@bot.callback_query_handler(func=lambda call: call.data in sport_options)
def sport_selection(call):
    sport = call.data

    # Записываем выбранный спорт в словарь проголосовавших
    voters[call.from_user.id] = sport

    # Создаем кнопки для опроса "Кто идет на выбранный вид спорта?"
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Я иду", callback_data='yes')
    button2 = types.InlineKeyboardButton("Не иду", callback_data='no')
    keyboard.add(button1, button2)

    # Отправляем опросное сообщение с кнопками
    bot.send_message(call.message.chat.id, f"Кто идет на {sport}?", reply_markup=keyboard)

# Обработчик нажатия на кнопку опроса
@bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
def answer_click(call):
    user_id = call.from_user.id
    sport = voters.get(user_id)

    if sport:
        if call.data == 'yes':
            voters[user_id] = f"{call.from_user.username} (Идет)"
        else:
            voters[user_id] = f"{call.from_user.username} (Не идет)"

        # Сохраняем информацию о проголосовавших
        save_voters()

        # Отправляем сообщение с информацией о проголосовавших
        result_message = "Список проголосовавших:\n"
        for user_id, status in voters.items():
            result_message += f"{status}\n"
        bot.send_message(call.message.chat.id, result_message)

# Запускаем бота
bot.polling()

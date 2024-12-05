from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import configparser
import os
from Levenshtein import ratio

# Путь к файлу конфигурации
config_file = 'config.ini'


# Функция для создания файла конфигурации, если его нет, и добавления пустого списка
def create_config():
    if not os.path.exists(config_file):
        config = configparser.ConfigParser()
        config['BotSets'] = {'token': '', 'admin_id': ''}
        config['Words'] = {'list': ''}
        with open(config_file, 'w') as file:
            config.write(file)


create_config()  # Создаем конфиг, если его нет


config = configparser.ConfigParser()
config.read(config_file)

# Считываем параметры перед запуском
BOT_TOKEN = config['BotSets']['token']
ADMIN_ID = config['BotSets']['admin_id']

# Создаем объекты бота и диспетчера
dp = Dispatcher()


# Функция для добавления одного слова в список
def add_word(word):
    config = configparser.ConfigParser()
    config.read(config_file)

    # Считываем текущий список
    words = config['Words']['list']
    words_list = words.split(',') if words else []

    # Добавляем новое слово в список
    words_list.append(word)

    # Записываем обновленный список обратно в конфиг
    config['Words']['list'] = ','.join(words_list)
    with open(config_file, 'w') as file:
        config.write(file)


# Функция для очистки списка
def clear_list():
    config = configparser.ConfigParser()
    config.read(config_file)

    # Очищаем список
    config['Words']['list'] = ''

    # Записываем изменения
    with open(config_file, 'w') as file:
        config.write(file)


# Функция для считывания информации из файла
def read_words():
    config = configparser.ConfigParser()
    config.read(config_file)

    words = config['Words']['list']
    return words.split(',') if words else []


def remove_word(word):
    config = configparser.ConfigParser()
    config.read(config_file)

    # Считываем текущий список
    words = config['Words']['list']
    words_list = words.split(',') if words else []

    # Если слово в списке, удаляем его
    if word.lower() in words_list:
        words_list.remove(word.lower())  # Удаляем слово с учетом регистра

    # Записываем обновленный список обратно в конфиг
    config['Words']['list'] = ','.join(words_list)
    with open(config_file, 'w') as file:
        config.write(file)


# /start
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nЯ бот для фильтрации сообщений в беседах.\n/help - Список доступных команд. \n\n'
                         'Разработчик: @Vassago_666')

    config = configparser.ConfigParser()
    config.read(config_file)
    admin_id = config['BotSets']['admin_id']

    if admin_id is None or admin_id == '':
        ADMIN_ID = message.from_user.id
        config['BotSets']['admin_id'] = str(ADMIN_ID)
        with open(config_file, 'w') as file:
            config.write(file)



# Обновление списка
@dp.message(Command(commands=['append_list']))
async def append_list(message: Message):
    if ADMIN_ID == str(message.from_user.id):
        list_words = message.text.replace('/append_list', '').split(', ')
        if list_words[0]:
            words = read_words()
            for word in list_words:
                if word.lower() not in words:
                    add_word(word.lower())

            await message.reply(text=f"Обновленный список слов: {read_words()}")
        else:
            await message.reply(text='Введите слова через запятую.')


# Получение списка
@dp.message(Command(commands=["get_words"]))
async def get_words_list(message: Message):
    if ADMIN_ID == str(message.from_user.id):
        await message.reply(text=f'Список добавленных слов: {read_words()}')


# Очистка списка
@dp.message(Command(commands=['clear_list']))
async def clear_list_words(message: Message):
    if ADMIN_ID == str(message.from_user.id):
        clear_list()
        await message.reply(text='Список очищен!')


# Удалить одно слово
@dp.message(Command(commands=['remove_word']))
async def remove_word_func(message: Message):
    if ADMIN_ID == str(message.from_user.id):
        word = message.text.replace('/remove_word ', '')
        remove_word(word)
        await message.reply(text=f"Обновленный список слов: {read_words()}")


# Помощь
@dp.message(Command(commands=['help']))
async def help(message: Message):
    print(ADMIN_ID)
    print(str(message.from_user.id))
    if ADMIN_ID == str(message.from_user.id):
        await message.reply(text="Список доступных команд:\n"
                                 "/append_list [слова через запятую] - добавить слова в список (можно добавлять по одному слову, либо несколько слов через запятую)\n"
                                 "/get_words - Получить список добавленных слов\n"
                                 "/clear_list - Очистить список добавленных слов\n"
                                 "/remove_word [слово] - удаляет слово из списка\n"
                                 "/help - Помощь")


# Если совпадение слова в сообщении со словом из списка больше или равно 80%, удалить сообщение
@dp.message()
async def delete_words(message: Message):
    text = message.text
    for i in text.split():
        for a in read_words():
            similarity_score = ratio(i.lower(), a) * 100
            if similarity_score >= 80:
                await message.delete()



if __name__ == '__main__':

    print(BOT_TOKEN)

    if BOT_TOKEN is None or BOT_TOKEN == '':
        BOT_TOKEN = input('Введите токен бота: ')
        config = configparser.ConfigParser()
        config.read(config_file)
        config['BotSets']['token'] = BOT_TOKEN
        with open(config_file, 'w') as file:
            config.write(file)

    bot = Bot(token=BOT_TOKEN)
    dp.run_polling(bot)
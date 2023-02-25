import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot.api import TelegramAPIServer
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN

from aiogram.types import Message


from aiogram_dialog.widgets.input import MessageInput
# Configure logging
from texts import help_text
from handlers.utils.filters.filters import IsAdmin
from db import get_lastseen, get_favorite, new_user, get_user

logging.basicConfig(level=logging.INFO)

# Create private Bot API server endpoints wrapper
local_server = TelegramAPIServer.from_base('http://localhost')
storage = MemoryStorage()
# Initialize bot with using local server
bot = Bot(token=API_TOKEN, server=local_server)

dp = Dispatcher(bot, storage=storage)

button_1 = KeyboardButton('Просмотренные 👀')
button_2 = KeyboardButton('Избранное👑')
button_3 = KeyboardButton('Предложения для вас🎫')
button_4 = KeyboardButton('Поддержка 👨‍💻')


main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_1, button_3).add(button_2, button_4)
async def hello_throttled(*args, **kwargs):
    # args will be the same as in the original handler
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    print(f"hello_throttled was called with args={args} and kwargs={kwargs}")
    message = args[0]  # as message was the first argument in the original handler
    await message.answer("Не спамьте")


@dp.message_handler(commands=["start"])
@dp.throttled(hello_throttled, rate=4)
async def start(message: Message):
    try:
        user = await get_user(message.from_user.id)
        if user[0] != message.from_user.id:
            await new_user(message.chat.id, message.from_user.username, message.from_user.first_name)
        else:
            await message.answer("Привет, здесь ты можешь посмотреть фильмы/аниме/сериалы, просто напиши название и бот найдет его", reply_markup=main_kb)

    except Exception as e:
        print(e)
        await message.answer("Обратитесь в поддержку", reply_markup=main_kb)


@dp.message_handler(lambda message: message.text == "Просмотренные 👀")
@dp.throttled(hello_throttled, rate=4)
async def lastseen(message: types.Message):
    lastseen = await get_lastseen(message.from_user.id)
    if lastseen:
        await message.answer("Последние 3 просмотренных:\n" + "\n\n".join(lastseen[:3]))
    else:
        await message.answer("Вы ничего не смотрели")


@dp.message_handler(lambda message: message.text == "Избранное👑")
@dp.throttled(hello_throttled, rate=4)
async def favorite(message: types.Message):
    info = await get_favorite(message.chat.id)
    if info:
        info = "\n\n".join(info)
        if len(info) > 4096:
            for x in range(0, len(info), 4096):
                await bot.send_message(message.chat.id, info[x:x+4096])
        else:
            await bot.send_message(message.chat.id, f"Список избранных:\n\n{info}")
    else:
        await message.answer("Пусто")


@dp.message_handler(lambda message: message.text == "Поддержка 👨‍💻")
@dp.throttled(hello_throttled, rate=4)
async def helper(message: types.Message):
    inline_kb_full = InlineKeyboardMarkup(row_width=2)
    inline_kb_full.add(InlineKeyboardButton('Обращения по боту', url='https://t.me/Am0nt0'))
    inline_kb_full.add(InlineKeyboardButton('Другие Обращения', url='https://t.me/Am0nt0'))
    await message.answer("Администрация", reply_markup=inline_kb_full)

@dp.message_handler(commands=["help"])
async def help(m: Message):
    await m.answer(help_text)       



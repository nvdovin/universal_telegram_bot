from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.utils import executor

TOKEN = "6395981820:AAHKmVFuqvX5kly0w113z5PHhaLm0Q-yXGs"
bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_message(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Я проснулся. Меня сейчас программируют")


@dp.message_handler(commands=['search'])
async def search_request(message: types.Message):
    bot.send_message(chat_id=message.from_user.id, text="Введи свой поисковый запрос и отправь его мне.")
    request = message.text
    print(request)


executor.start_polling(dispatcher=dp)

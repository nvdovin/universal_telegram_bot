from bs4 import BeautifulSoup
import requests
from config import byble_text, TG_TOKEN, post_url
import os
import time

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from datetime import datetime
import scheduler

from avito_parser.avito_parser import AvitoParser


bot = Bot(TG_TOKEN)
dp = Dispatcher(bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add("Стих из Писания").add("Авито поиск")


class Data:
    def __init__(self) -> None:
        self.request = requests.get(byble_text).text
        self.soap = BeautifulSoup(self.request, "lxml")

    @staticmethod
    def image_source():
        """ Возвращается ссылка на рандомное изображение разных размеров """

        # os.system("clear")

        requests.post(post_url)
        image_data = requests.get("https://api.rand.by/image").json()
        image_raw = image_data["urls"]["regular"]
        print(f"""{datetime.now().hour}:{datetime.now().minute},
{image_raw}""")

        return image_raw

    def parsed_data(self):
        bible_verse = self.soap.find("span", class_="v1").text
        bible_place = self.soap.find("div", class_="vr").find("a", class_="vc").text

        return bible_verse, bible_place

@dp.message_handler(commands=["keyboard"])
async def get_keyboard(message: types.Message):
    print("Keyboard started here")
    await bot.send_message(chat_id=message.from_user.id,
                           reply_markup=keyboard)


@dp.message_handler(text="Стих из Писания")
async def get_bible_verse(message: types.Message):
    data = Data()
    verse_data = data.parsed_data()
    image_url = data.image_source()

    sending_message = f"""{verse_data[0]} 

    {verse_data[1]}"""

    # await bot.delete_message()
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=image_url,
                         caption=sending_message)


@dp.message_handler(commands=["photo"])
async def get_bible_verse(message: types.Message):
    data = Data()
    image_url = data.image_source()

    await bot.send_photo(chat_id=message.from_user.id,
                         photo=image_url)


@dp.message_handler(commands=["des"])
async def get_bible_verse(message: types.Message):
    description = """Я - Бот, который умеет отправлять рандомные стихи из Библии, и рандомные фото
Чтобы получить только фото, напиши - /photo
Чтобы получить фото и стих - /verse

Я всё еще развиваюсь!
     """

    await bot.send_message(chat_id=message.from_user.id,
                           text=description)


async def daily_bible_verse():
    data = Data()
    verse_data = data.parsed_data()
    image_url = data.image_source()

    sending_message = f"""{verse_data[0]} 

        {verse_data[1]}"""

    await bot.send_photo(chat_id=419057426,
                         photo=image_url,
                         caption=sending_message)
    await bot.send_message(chat_id=419057426, text="Timer")


@dp.message_handler(text="Авито поиск")
async def avito_sender(message: types.Message, sender=True):
    avito = AvitoParser()
    data = avito.get_parsed_data(10)

    # Запись в .json файл
    avito.write_to_file(data, "json", "from_telegram")

    counter = 1

    if sender is True:
        chat = message.from_user.id
    else:
        chat = 419057426

    for i in range(len(data)):
        message_to_send = f'''##### {counter} #####
{data[i]["car_name"]} - {data[i]["year"]}
{data[i]["price"]} Рублей.

Пробег: {data[i]["car_info"]["way_length"]} км.
Объём двигателя: {data[i]["car_info"]["volume"]} л.
Мощность: {data[i]["car_info"]["power"]} л.с.
Тип машины: {data[i]["car_info"]["car_type"]}.
Привод: {data[i]["car_info"]["transmission"]}.
Топливо: {data[i]["car_info"]["fuel"]}.

{data[i]["url"]}

{data[i]["description"]} '''

        await bot.send_message(chat_id=chat, text=message_to_send)
        counter += 1
        time.sleep(1)            

def main():
    executor.start_polling(dp, skip_updates=True)


main()

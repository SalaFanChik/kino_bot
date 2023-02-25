from .filters.filters import IsAdmin
from scrapper.movie_scrapper import get_movie, get_anime, get_serial
from main import dp, bot
from aiogram import types
from db import new_movie, new_anime, add_anime_series, get_count, new_serial, add_serial_series, get_animeid_data_by_uniqueid, get_serialid_data_by_uniqueid
import os
import asyncio
import random
import string
from states import MySG, YouSG
from aiogram.types import Message
from aiogram.dispatcher import FSMContext




@dp.message_handler(IsAdmin(), commands=["upload"])
async def upload_video(message: types.Message):
	await message.answer("Начал")
	loop = asyncio.get_event_loop()
	movie = await loop.run_in_executor(None, get_movie, message.text.split(" ")[1])
	await message.answer("Отправка...")
	file_id	= await bot.send_video(message.chat.id, open(movie[9], 'rb'), supports_streaming=True)
	file_id_2 = await bot.send_photo(message.chat.id, open(movie[10], 'rb'))
	os.remove(movie[9])
	os.remove(movie[10])
	await new_movie(file_id=str(file_id.video.file_id), year=str(movie[1]), movie_name=str(movie[2]), country=str(movie[3]), genre=str(movie[4]), description=str(movie[5]), imdb_rate=str(movie[6]), kinopoisk_rate=str(movie[7]), movie_poster=file_id_2.photo[0]['file_id'])


@dp.message_handler(IsAdmin(), commands=["uploadanime"])
async def upload_anime(message: types.Message):
	await message.answer("Начал")
	loop = asyncio.get_event_loop()
	anime = await loop.run_in_executor(None, get_anime, message.text.split(" ")[1])
	file_id_2 = await bot.send_photo(message.chat.id, open(anime[0][0], 'rb'))
	uniqueid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
	await new_anime(year=anime[0][2], anime_name=anime[0][4], uniqueid=uniqueid, series=len(anime[1]), genre=anime[0][1], description=anime[0][3], anime_poster=file_id_2.photo[0].file_id)
	await message.answer("Отправка...")
	for b, i in enumerate(anime[1]):
		file_id	= await bot.send_video(message.chat.id, open(i, 'rb'), supports_streaming=True)
		await add_anime_series(file_id=file_id.video.file_id, uniqueid=uniqueid, series_num=int(b)+1)

@dp.message_handler(IsAdmin(), commands=["get_stat"])
async def get_stat(message: types.Message):
	await message.answer(f"Кол-во пользователей {await get_count()}")


@dp.message_handler(IsAdmin(), commands=["uploadserial"])
async def upload_serial(message: types.Message):
	await message.answer("Начал")
	loop = asyncio.get_event_loop()
	serial = await loop.run_in_executor(None, get_serial, message.text.split(" ")[1])
	file_id_2 = await bot.send_photo(message.chat.id, open(serial[8], 'rb'))
	uniqueid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
	await new_serial(year=str(serial[1]), serial_name=str(serial[2]), country=str(serial[3]), genre=str(serial[4]), description=str(serial[5]), imdb_rate=str(serial[6]), kinopoisk_rate=str(serial[7]), serial_poster=file_id_2.photo[0]['file_id'], uniqueid=uniqueid)
	await message.answer("Отправка...")
	for b, i in enumerate(serial[0]):
		file_id	= await bot.send_video(message.chat.id, open(serial[0][i], 'rb'), supports_streaming=True)
		await add_serial_series(file_id=file_id.video.file_id, uniqueid=uniqueid, series_num=i)



@dp.message_handler(IsAdmin(),commands=["addanime"])
async def serial(message: Message):
    await MySG.main.set()
    await message.answer("Ид")

@dp.message_handler(state=MySG.main)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
    await MySG.next()
    await message.answer("Видео")


@dp.message_handler(IsAdmin(),content_types=['video'], state=MySG.video)
async def anime(message: Message, state: FSMContext):
    async with state.proxy() as data:
        ids = data['id']

    series_num = await get_animeid_data_by_uniqueid(ids)
    print(series_num)
    await add_anime_series(str(message.video.file_id), str(ids), int(series_num[0])+1)
    await message.answer("OK")
    await state.finish()


#---
@dp.message_handler(IsAdmin(),commands=["addserial"])
async def serial(message: Message):
    await YouSG.main.set()
    await message.answer("Ид")


@dp.message_handler(IsAdmin(),state=YouSG.main)
async def serial_1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
    await YouSG.next()
    await message.answer("Видео")


@dp.message_handler(IsAdmin(),content_types=['video'], state=YouSG.video)
async def serial_2(message: Message, state: FSMContext):
    async with state.proxy() as data:
        ids = data['id']

    series_num = await get_serialid_data_by_uniqueid(ids)
    await add_serial_series(message.video.file_id, ids, int(series_num[0])+1)
    await message.answer("OK")
    await state.finish()


from main import dp, bot, hello_throttled
from aiogram import types
from db import search, set_to_delete, get_to_delete, get_movie_data, get_anime_data, get_anime_series, add_suggestions, get_anime_data_by_uniqueid, add_lastseen, add_to_favorite, genre_suggestions, get_serial_data, get_serial_data_by_uniqueid, get_serial_series, get_favorite, del_from_favorite
#from keyboards import test_buttons_creator
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext


video_cb = CallbackData('video', 'type', 'id')



async def create_inline_movie_list(user_id, movies = None, anime = None, serials = None, offsetX: int = 0, offsetY: int = 10):
    video_kb = InlineKeyboardMarkup()
    if movies:
        pagination = list(movies.keys())[offsetX:offsetY]
        first_value = f'{offsetX-10}#{offsetY-10}'
        last_value = f'{offsetX+10}#{offsetY+10}'
        list1 = list(pagination)[-1]
        list2 = list(movies.keys())[-1]
        for i in pagination:
            video_kb.row(InlineKeyboardButton(f'{str(movies[i][0])}', callback_data=video_cb.new(type='movie', id=str(movies[i][1]))))
            #video_kb.row(InlineKeyboardButton(f'{i}', callback_data=movie_cb.new(movie_name=str(i), id=str(i))))
        await set_to_delete(user_id, first_value)
        video_kb.row(InlineKeyboardButton(text='< Сюда' if int(list1) > 10 else ' ', callback_data=f'edit_config#{first_value}'),
               InlineKeyboardButton(text=f'{list1}/{list2}', callback_data='page'),
               InlineKeyboardButton(text='Туда >' if int(list1) < int(list2) else ' ', callback_data=f'edit_config#{last_value}'))
    if anime:
        pagination = list(anime.keys())[offsetX:offsetY]
        first_value = f'{offsetX-10}#{offsetY-10}'
        last_value = f'{offsetX+10}#{offsetY+10}'
        list1 = list(pagination)[-1]
        list2 = list(anime.keys())[-1]
        for i in pagination:
            video_kb.row(InlineKeyboardButton(f'{str(anime[i][0])}', callback_data=video_cb.new(type='anime', id=str(anime[i][1]))))
            #video_kb.row(InlineKeyboardButton(f'{i}', callback_data=movie_cb.new(movie_name=str(i), id=str(i))))
        await set_to_delete(user_id, first_value)
        video_kb.row(InlineKeyboardButton(text='< Сюда' if int(list1) > 10 else ' ', callback_data=f'edit_config#{first_value}'),
               InlineKeyboardButton(text=f'{list1}/{list2}', callback_data='page'),
               InlineKeyboardButton(text='Туда >' if int(list1) < int(list2) else ' ', callback_data=f'edit_config#{last_value}'))
    if serials:
        pagination = list(serials.keys())[offsetX:offsetY]
        first_value = f'{offsetX-10}#{offsetY-10}'
        last_value = f'{offsetX+10}#{offsetY+10}'
        list1 = list(pagination)[-1]
        list2 = list(serials.keys())[-1]
        for i in pagination:
            video_kb.row(InlineKeyboardButton(f'{str(serials[i][0])}', callback_data=video_cb.new(type='serial', id=str(serials[i][1]))))
            #video_kb.row(InlineKeyboardButton(f'{i}', callback_data=movie_cb.new(movie_name=str(i), id=str(i))))
        await set_to_delete(user_id, first_value)
        video_kb.row(InlineKeyboardButton(text='< Сюда' if int(list1) > 10 else ' ', callback_data=f'edit_config#{first_value}'),
               InlineKeyboardButton(text=f'{list1}/{list2}', callback_data='page'),
               InlineKeyboardButton(text='Туда >' if int(list1) < int(list2) else ' ', callback_data=f'edit_config#{last_value}'))

    return video_kb

@dp.callback_query_handler(video_cb.filter(type='movie'))
async def movies_send(query: types.CallbackQuery, callback_data: dict):
    video_id = callback_data['id']
    video = await get_movie_data(video_id)
    watch_kb = InlineKeyboardMarkup()
    watch_kb.row(InlineKeyboardButton(f'Смотреть', callback_data=video_cb.new(type='watch_movie', id=str(callback_data['id']))))
    if video[3] in await get_favorite(query.from_user.id):
        watch_kb.row(InlineKeyboardButton(f'Удалить из избранных', callback_data=f"del_favorite{video[3]}"))
    else:
        watch_kb.row(InlineKeyboardButton(f'Добавить в избранное', callback_data=f"add_favorite{video[3]}"))
    await bot.send_photo(query.from_user.id, caption=f"<b>{video[3]}</b>\n\nIMDB:{video[7]}\nKINOPOISK:{video[8]}\nГод:{video[2]}\nСтрана:{video[4]}\nЖанр:{video[5]}\n\n{video[6]}", photo=video[9], reply_markup=watch_kb,parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("add_favorite"))
async def process_callback(callback_query: types.CallbackQuery):
    await add_to_favorite(callback_query.from_user.id, callback_query.data.split("add_favorite")[-1])
    await bot.answer_callback_query(callback_query.id,text='Добавлено', show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith("del_favorite"))
async def process_callback(callback_query: types.CallbackQuery):
    await del_from_favorite(callback_query.from_user.id, callback_query.data.split("del_favorite")[-1])
    await bot.answer_callback_query(callback_query.id,text='Удалено', show_alert=True)


@dp.callback_query_handler(video_cb.filter(type='watch_movie'))
async def movie_send(query: types.CallbackQuery, callback_data: dict):
    video_id = callback_data['id']
    video = await get_movie_data(video_id)
    await add_suggestions(query.from_user.id, video[5].split(','))
    print(video)
    await add_lastseen(query.from_user.id, video[3])
    await bot.send_video(query.from_user.id, video[1])

@dp.callback_query_handler(video_cb.filter(type='watch_anime'))
async def anime_send(query: types.CallbackQuery, callback_data: dict):
    video_id = callback_data['id']
    video_id = video_id.split("-")
    video = await get_anime_series(video_id[0], int(video_id[1]) - 1)
    video_check = await get_anime_series(video_id[0], int(video_id[1]))
    no = await get_anime_data_by_uniqueid(video[2])
    await add_lastseen(query.from_user.id, f"{no[1]}-{int(video_id[1])} серия")
    if video_check:
        watch_kb = InlineKeyboardMarkup()
        watch_kb.row(InlineKeyboardButton(f'{int(video_id[1]) +1} серия', callback_data=video_cb.new(type='watch_anime', id=f"{video[2]}-{int(video_id[1])+1}")))
        await bot.send_video(query.from_user.id, video[0], reply_markup=watch_kb)
    else:
        yes = await get_anime_data_by_uniqueid(video[2])
        await add_suggestions(query.from_user.id, yes[4].split(','))
        await bot.send_video(query.from_user.id, video[0])

@dp.callback_query_handler(video_cb.filter(type='watch_serial'))
async def serial_send(query: types.CallbackQuery, callback_data: dict):
    video_id = callback_data['id']
    video_id = video_id.split("-")
    print(video_id)
    video = await get_serial_series(video_id[0], int(video_id[1]))
    print(video)
    video_check = await get_serial_series(video_id[0], int(video_id[1])+ 1)
    print(video_check )
    no = await get_serial_data_by_uniqueid(video[2])
    await add_lastseen(query.from_user.id, f"{no[2]}-{int(video_id[1])} серия")
    if video_check:
        watch_kb = InlineKeyboardMarkup()
        watch_kb.row(InlineKeyboardButton(f'{int(video_id[1]) +1} серия', callback_data=video_cb.new(type='watch_serial', id=f"{video[2]}-{int(video_id[1])+1}")))
        await bot.send_video(query.from_user.id, video[0], reply_markup=watch_kb)
    else:
        yes = await get_serial_data_by_uniqueid(video[2])
        await add_suggestions(query.from_user.id, yes[4].split(','))
        await bot.send_video(query.from_user.id, video[0])


@dp.callback_query_handler(video_cb.filter(type='anime'))
async def animes_send(query: types.CallbackQuery, callback_data: dict):
    video_id = callback_data['id']
    video = await get_anime_data(video_id)
    description = video[6]
    new_description = ''
    if len(description) > 500:
        for i in description.split("."):
            new_description += f'{i}.'
            if len(new_description) > 400:
                break
    watch_kb = InlineKeyboardMarkup()
    watch_kb.row(InlineKeyboardButton(f'Смотреть', callback_data=video_cb.new(type='watch_anime', id=f"{video[3]}-1")))
    if video[1] in await get_favorite(query.from_user.id):
        watch_kb.row(InlineKeyboardButton(f'Удалить из избранных', callback_data=f"del_favorite{video[1]}"))
    else:
        watch_kb.row(InlineKeyboardButton(f'Добавить в избранное', callback_data=f"add_favorite{video[1]}"))
    if query.from_user.id == 1639491822:
        await query.message.answer(video[3])
    await bot.send_photo(query.from_user.id, caption=f"<b>{video[1]}</b>\n\n\nГод:{video[5]}\n\nЖанр:{video[4]}\n\nОписание: {new_description}...", photo=video[7], reply_markup=watch_kb ,parse_mode="HTML")

@dp.callback_query_handler(video_cb.filter(type='serial'))
async def animes_send(query: types.CallbackQuery, callback_data: dict):
    video_id = callback_data['id']
    video = await get_serial_data(video_id)
    watch_kb = InlineKeyboardMarkup()
    watch_kb.row(InlineKeyboardButton(f'Смотреть', callback_data=video_cb.new(type='watch_serial', id=f"{video[9]}-1")))
    print(video[2], await get_favorite(query.from_user.id))
    if video[2] in await get_favorite(query.from_user.id):
        watch_kb.row(InlineKeyboardButton(f'Удалить из избранных', callback_data=f"del_favorite{video[2]}"))
    else:
        watch_kb.row(InlineKeyboardButton(f'Добавить в избранное', callback_data=f"add_favorite{video[2]}"))
    if query.from_user.id == 1639491822:
        await query.message.answer(video[9])
    await bot.send_photo(query.from_user.id, caption=f"<b>{video[2]}</b>\n\nIMDB:{video[6]}\nKINOPOISK:{video[7]}\nГод:{video[1]}\nСтрана:{video[3]}\nЖанр:{video[4]}\n\n{video[5]}", photo=video[8], reply_markup=watch_kb,parse_mode="HTML")
    

@dp.callback_query_handler(lambda c: c.data.startswith('edit_config'))
async def set_or_update_config(callback_query: types.CallbackQuery = None, state: FSMContext = None, user_id=None, offsetX="", offsetY=""):
    async with state.proxy() as data:
        if data['movies']:
            b = data['movies']
        else:
            b = data['anime']
    if callback_query is not None:
        user_id = callback_query.from_user.id
        offsetX = callback_query.data.split("#")[1]
        offsetY = callback_query.data.split("#")[-1]
    if offsetX == "" and offsetY == "":
        async with state.proxy() as data:
            if data['movies']:
                await bot.send_message(user_id, text='Фильмы', reply_markup=await create_inline_movie_list(callback_query.from_user.id, movies=b))
            else:
                await bot.send_message(user_id, text='Аниме', reply_markup=await create_inline_movie_list(callback_query.from_user.id, anime=b))
    else:
        msg_id = callback_query.message.message_id
        if int(list(b.keys())[-1]) > int(offsetX) > -10:
            async with state.proxy() as data:
                if data['movies']:
                    await bot.edit_message_reply_markup(user_id, message_id=msg_id, reply_markup=await create_inline_movie_list(callback_query.from_user.id, movies=b, offsetX=int(offsetX), offsetY=int(offsetY)))
                else:
                    await bot.edit_message_reply_markup(user_id, message_id=msg_id, reply_markup=await create_inline_movie_list(callback_query.from_user.id, anime=b, offsetX=int(offsetX), offsetY=int(offsetY)))
        else:
            await bot.answer_callback_query(callback_query_id=callback_query.id, text="Мотай в другую сторону!!!", show_alert=True)


@dp.message_handler(lambda message: message.text.split(" ")[0] not in ["1", "/upload", "/uploadanime", "/get_stat", "/uploadserial", "/addserial", "/addanime", "Просмотренные", "Избранное👑 ", "Предложения", "Поддержка"])
@dp.throttled(hello_throttled, rate=4)
async def send_movie(message: types.Message, state: FSMContext):
    videos = await search(message.text)
    if videos[0]:
        di = {}
        n = 0
        for i in videos[0]:
            n += 1 
            di[n] = [f'{i[3]}', i[0]]
        async with state.proxy() as data:
            data['movies'] = di
        await message.answer("Фильмы", reply_markup=await create_inline_movie_list(message.from_user.id, movies=di))
    if videos[1]:
        di = {}
        n = 0
        for i in videos[1]:
            n += 1 
            di[n] = [f'{i[1]}', i[0]]
        async with state.proxy() as data:
            data['anime'] = di
        await message.answer("Аниме", reply_markup=await create_inline_movie_list(message.from_user.id, anime=di))
    if videos[2]:
        di = {}
        n = 0
        for i in videos[2]:
            n += 1 
            di[n] = [f'{i[2]}', i[0]]
        async with state.proxy() as data:
            data['serials'] = di
        await message.answer("Сериалы", reply_markup=await create_inline_movie_list(message.from_user.id, serials=di))

    if not videos[1] and not videos[0] and not videos[2]:
        await message.answer("Ничего не найдено, название должно быть на русском и без ошибок, Обратитесь в поддержку чтобы добавить фильм")


@dp.message_handler(lambda message: message.text == "Предложения для вас🎫")
@dp.throttled(hello_throttled, rate=2)
async def suggestions(message: types.Message, state: FSMContext):
    videos = await genre_suggestions(message.chat.id)
    if videos:
        if videos[0]:
            di = {}
            n = 0
            for i in videos[0]:
                n += 1 
                di[n] = [f'{i[3]}', i[0]]
            async with state.proxy() as data:
                data['movies'] = di
            await message.answer("Фильмы", reply_markup=await create_inline_movie_list(message.from_user.id, movies=di))
        if videos[1]:
            di = {}
            n = 0
            for i in videos[1]:
                n += 1 
                di[n] = [f'{i[1]}', i[0]]
            async with state.proxy() as data:
                data['anime'] = di
            await message.answer("Аниме", reply_markup=await create_inline_movie_list(message.from_user.id, anime=di))

        if not videos[0] and not videos[1]:
            await message.answer("Ничего не найдено")
    else:
        await message.answer("Посмотрите хотя бы пару фильмов")




@dp.message_handler(lambda message: message.text == "1")
async def send_movie(message: types.Message):
    await message.answer('asdasd')
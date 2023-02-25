import aiosqlite
import asyncio 
from fuzzywuzzy import fuzz

database = 'data.db'
async def main():
   db = await aiosqlite.connect(database)
   await db.execute("""CREATE TABLE IF NOT EXISTS users(
      userid INT PRIMARY KEY,
      username TEXT,
      fname TEXT,
      is_active BOOL FALSE,
      vip BOOL,
      last_seen TEXT,
      suggestions TEXT,
      favorite TEXT);
   """)
   await db.execute("""CREATE TABLE IF NOT EXISTS movies(
      movieid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      file_id TEXT, 
      year TEXT, 
      moviename TEXT,
      country TEXT,
      genre TEXT,
      description TEXT,
      imdb_rate TEXT,
      kinopoisk_rate TEXT,
      poster TEXT);
   """)

   await db.execute("""CREATE TABLE IF NOT EXISTS serials(
      serialid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
      year TEXT, 
      serialname TEXT,
      country TEXT,
      genre TEXT,
      description TEXT,
      imdb_rate TEXT,
      kinopoisk_rate TEXT,
      poster TEXT,
      uniqueid TEXT);
   """)

   await db.execute("""CREATE TABLE IF NOT EXISTS reviews(
      reviewid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      movieid INT, 
      fname TEXT,
      review TEXT,
      rate INT);
   """)

   await db.execute("""CREATE TABLE IF NOT EXISTS anime(
      animeid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      animename TEXT,
      series INT, 
      uniqueid TEXT,
      genre TEXT,
      year TEXT,
      description TEXT,
      poster TEXT);
   """)

   await db.execute("""CREATE TABLE IF NOT EXISTS anime_series(
      file_id TEXT,
      series_num INT,
      uniqueid TEXT);
   """)

   await db.execute("""CREATE TABLE IF NOT EXISTS serial_series(
      file_id TEXT,
      series_num INT,
      uniqueid TEXT);
   """)


   await db.execute("""CREATE TABLE IF NOT EXISTS to_delete(
      user_id INT,
      value INT);
   """)


   await db.commit()

   #cur.execute("ALTER TABLE 'movies' ADD 'poster' TEXT;")
   await db.execute("DELETE from to_delete")
   await db.close()

async def new_movie(file_id, year, movie_name, country, genre, description, imdb_rate, kinopoisk_rate, movie_poster):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO movies(file_id, year, moviename, country, genre, description, imdb_rate, kinopoisk_rate, poster) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", (file_id, year, movie_name, country, genre, description, imdb_rate, kinopoisk_rate, movie_poster))
   await db.commit()
   await db.close()

async def set_to_delete(user_id, value):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO to_delete(user_id, value) VALUES(?, ?);", (user_id, value))
   await db.commit()
   await db.close()


async def get_to_delete(user_id):
   db = await aiosqlite.connect(database)
   cur = await db.execute(f"SELECT value FROM to_delete WHERE user_id={user_id}")
   result = await cur.fetchone()
   db.execute(f"DELETE from to_delete where user_id={user_id}")
   await db.close()
   return result

async def new_user(user_id, username, fname):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO users(userid, username, fname, vip) VALUES(?, ?, ?, ?);", (user_id, username, fname, False))
   await db.commit()
   await db.close()


async def new_serial(year, serial_name, country, genre, description, imdb_rate, kinopoisk_rate, serial_poster, uniqueid):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO serials(year, serialname, country, genre, description, imdb_rate, kinopoisk_rate, poster, uniqueid) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", (year, serial_name, country, genre, description, imdb_rate, kinopoisk_rate, serial_poster, uniqueid))
   await db.commit()
   await db.close()



async def add_serial_series(file_id, uniqueid, series_num):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO serial_series(file_id, series_num, uniqueid) VALUES(?, ?, ?);", (file_id, series_num, uniqueid))
   await db.commit()
   await db.close()

async def new_review(reviewid, movieid, fname, review, rate):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO reviews(reviewid, movieid, fname, review, rate) VALUES(?, ?, ?, ?, ?, ?, ?, ?);", (reviewid, movieid, fname, review, rate))
   await db.commit()
   await db.close()




async def get_full_info():
   db = await aiosqlite.connect(database)
   cur = await db.execute("SELECT * FROM movies ORDER BY movieid DESC LIMIT 1")
   result = await cur.fetchone()
   await db.close()
   return result

async def set_info(column, ids, data, table, by):
   db = await aiosqlite.connect(database)
   await db.execute(f"UPDATE {table} SET {column}  = '{data}' WHERE {by} = {ids};")
   await db.commit()
   await db.close()
#set_info(table='movies', column='year', data='26 октября 1990 года', by='movieid', ids='1')

async def search(name):
   db = await aiosqlite.connect(database)
   cur = await db.execute("SELECT movieid, moviename FROM 'movies'")
   movies_list = await cur.fetchall()
   movies = []
   for i in movies_list:
      if fuzz.token_set_ratio(i[1], name) > 80:
         cur = await db.execute(f"SELECT * FROM 'movies' WHERE movieid = {i[0]} ") 
         movies.append(await cur.fetchone())
   
   animes = []
   cur = await db.execute("SELECT animeid, animename FROM 'anime'")
   anime_list = await cur.fetchall()
   for i in anime_list:
      if fuzz.token_set_ratio(i[1], name) > 80:
         cur = await db.execute(f"SELECT * FROM 'anime' WHERE animeid = {i[0]} ") 
         animes.append(await cur.fetchone())
   
   serials = []
   cur = await db.execute("SELECT serialid, serialname FROM 'serials'")
   serial_list = await cur.fetchall()
   for i in serial_list:
      if fuzz.token_set_ratio(i[1], name) > 80:
         cur = await db.execute(f"SELECT * FROM 'serials' WHERE serialid = {i[0]} ") 
         serials.append(await cur.fetchone())

   await db.close()
   return movies, animes, serials


async def genre_suggestions(user_id):
   db = await aiosqlite.connect(database)
   suggestions = await db.execute(f"SELECT suggestions FROM 'users' WHERE userid={user_id}")
   suggestions = await suggestions.fetchone()
   if suggestions[0]:
      genre = " ".join(suggestions[0].split("|"))
      cur = await db.execute("SELECT movieid, genre, moviename FROM 'movies'")
      movies_list = await cur.fetchall()
      movies = []
      ss = await get_lastseen(user_id)
      ss = [i[:i.find('-')] for i in ss]
      ss = [i.strip() for i in ss]
      for i in movies_list:
         if fuzz.token_set_ratio(i[1], genre) > 80:
            if i[2].strip() not in ss:
               cur = await db.execute(f"SELECT * FROM 'movies' WHERE movieid = {i[0]} ") 
               movies.append(await cur.fetchone())

      animes = []
      cur = await db.execute("SELECT animeid, genre, animename FROM 'anime'")
      anime_list = await cur.fetchall()
      for i in anime_list:
         if fuzz.token_set_ratio(i[1], genre) > 80:
            if i[2].strip() not in ss:
               cur = await db.execute(f"SELECT * FROM 'anime' WHERE animeid = {i[0]} ") 
               animes.append(await cur.fetchone())
      await db.close()
      return movies, animes
   else:
      await db.close()
      return None


async def get_movie_data(video_id):
   db = await aiosqlite.connect(database)
   movie = await db.execute(f"SELECT * FROM 'movies' WHERE movieid={video_id}") 
   movie = await movie.fetchone()
   await db.close()
   return movie

async def get_user(user_id):
   db = await aiosqlite.connect(database)
   users = await db.execute(f"SELECT * FROM 'users' WHERE userid={user_id}") 
   users = await users.fetchone()
   await db.close()
   return users

async def get_anime_data(video_id):
   db = await aiosqlite.connect(database)
   anime = await db.execute(f"SELECT * FROM 'anime' WHERE animeid={video_id}") 
   anime = await anime.fetchone()
   await db.close()
   return anime

async def get_anime_data_by_uniqueid(uniqueid):
   db = await aiosqlite.connect(database)
   anime = await db.execute(f"SELECT * FROM 'anime' WHERE uniqueid='{uniqueid}'") 
   anime = await anime.fetchone()
   await db.close()
   return anime



async def get_animeid_data_by_uniqueid(uniqueid):
   db = await aiosqlite.connect(database)
   anime = await db.execute(f"SELECT series_num FROM 'anime_series' WHERE uniqueid = '{uniqueid}' ORDER BY series_num DESC LIMIT 1;") 
   anime = await anime.fetchone()
   await db.close()
   return anime

async def get_serialid_data_by_uniqueid(uniqueid):
   db = await aiosqlite.connect(database)
   serial = await db.execute(f"SELECT series_num FROM 'serial_series' WHERE uniqueid = '{uniqueid}' ORDER BY series_num DESC LIMIT 1;") 
   serial = await serial.fetchone()
   await db.close()
   return serial


async def get_serial_data(video_id):
   db = await aiosqlite.connect(database)
   serial = await db.execute(f"SELECT * FROM 'serials' WHERE serialid={video_id}") 
   serial = await serial.fetchone()
   await db.close()
   return serial

async def get_serial_data_by_uniqueid(uniqueid):
   db = await aiosqlite.connect(database)
   serial = await db.execute(f"SELECT * FROM 'serials' WHERE uniqueid='{uniqueid}'") 
   serial = await serial.fetchone()
   await db.close()
   return serial

async def get_anime_series(uniqueid, series_num):
   db = await aiosqlite.connect(database)
   anime = await db.execute(f"SELECT * FROM 'anime_series' WHERE uniqueid='{uniqueid}' AND series_num={series_num}") 
   anime = await anime.fetchone()
   await db.close()
   return anime

async def get_serial_series(uniqueid, series_num):
   db = await aiosqlite.connect(database)
   serial = await db.execute(f"SELECT * FROM 'serial_series' WHERE uniqueid='{uniqueid}' AND series_num={series_num}") 
   serial = await serial.fetchone()
   await db.close()
   return serial

async def new_anime(year, anime_name, uniqueid, series, genre, description, anime_poster):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO anime(animename, series, year, uniqueid, genre, description, poster) VALUES(?, ?, ?, ?, ?, ?, ?);", (anime_name, series, year, uniqueid, genre, description, anime_poster))
   await db.commit()
   await db.close()

#cur.execute("DELETE from movies where movieid = null")
#new_anime(1997, 'asd', 'asdasd', 10, 'asdasdasdsf', 'asfnsdonionf', 'wefjopwpefpef')


async def add_anime_series(file_id, uniqueid, series_num):
   db = await aiosqlite.connect(database)
   await db.execute(f"INSERT INTO anime_series(file_id, series_num, uniqueid) VALUES(?, ?, ?);", (file_id, series_num, uniqueid))
   await db.commit()
   await db.close()
#cur.execute("""UPDATE movies SET poster = 'AgACAgIAAxkDAAIVAWL_J7p992hgLXPaUJEDVsPSHFaUAAJtuTEbt1X5S4pUVsjdWo6tAQADAgADcwADKQQ' WHERE movieid = 3;""")

#conn.commit()



async def add_suggestions(user_id: int = None, suggestion: list = None):
   db = await aiosqlite.connect(database)
   suggestions = await db.execute(f"SELECT suggestions FROM 'users' WHERE userid={user_id}")
   suggestions = await suggestions.fetchone()
   if suggestions[0]:
      print(suggestions)
      suggestion = '|'.join(set(suggestions[0].split("|")+suggestion))
      print(suggestion)
   else:
      suggestion = '|'.join(set(suggestion))


   await db.execute(f"""UPDATE users SET suggestions = '{suggestion}' WHERE userid = {user_id};""")
   await db.commit()
   await db.close()



async def add_lastseen(user_id: int = None, last_seen: list = None):
   db = await aiosqlite.connect(database)
   last_seened = await db.execute(f"SELECT last_seen FROM 'users' WHERE userid={user_id}")
   last_seened = await last_seened.fetchone()
   if last_seened[0]:
      last_seen = '|'.join(set(list(last_seened)+[last_seen]))
   else:
      last_seen = '|'.join(set([last_seen]))
   
   await db.execute(f"""UPDATE users SET last_seen = '{last_seen}' WHERE userid = {user_id};""")
   await db.commit()
   await db.close()

async def get_lastseen(user_id):
   db = await aiosqlite.connect(database)
   last_seened = await db.execute(f"SELECT last_seen FROM 'users' WHERE userid={user_id}")
   last_seened = await last_seened.fetchone()
   if last_seened[0]:
      print(1)
      await db.close()
      return last_seened[0].split("|")
   else:
      await db.close()
      return None
   


async def add_to_favorite(user_id, favorite):
   db = await aiosqlite.connect(database)
   favorites = await db.execute(f"SELECT favorite FROM 'users' WHERE userid={user_id}")
   favorites = await favorites.fetchone()
   if favorites[0]:
      favorite = '|'.join(set(favorites[0].split("|")+[favorite]))
   else:
      favorite = '|'.join(set([favorite]))
   await db.execute(f"""UPDATE users SET favorite = '{favorite}' WHERE userid = {user_id};""")
   await db.commit()
   await db.close()


async def del_from_favorite(user_id, favorites):
   db = await aiosqlite.connect(database)
   favorite = await db.execute(f"SELECT favorite FROM 'users' WHERE userid={user_id}")
   favorite = await favorite.fetchone()
   print(f"'{favorites}'")
   favorite = favorite[0].split("|")
   favorite.remove(favorites)
   print(favorite)
   favorite = '|'.join(favorite)
   print(favorite)
   await db.execute(f"""UPDATE users SET favorite = '{favorite}' WHERE userid = {user_id};""")
   await db.commit()
   await db.close()

 
async def get_favorite(user_id):
   db = await aiosqlite.connect(database)
   favorite = await db.execute(f"SELECT favorite FROM 'users' WHERE userid={user_id}")
   favorite = await favorite.fetchone()
   await db.close()
   if favorite[0]:
      return favorite[0].split("|")
   else:
      return []



async def get_count():
   db = await aiosqlite.connect(database)
   count = await db.execute("SELECT COUNT(*) FROM 'users'")
   result = await count.fetchone()
   print(result)
   await db.close()
   return result



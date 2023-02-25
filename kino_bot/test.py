import sqlite3

conn = sqlite3.connect('data.db')

cur = conn.cursor()

cur.execute("DELETE  FROM anime_series WHERE series_num = '6QKLQ82IVP'")
conn.commit()
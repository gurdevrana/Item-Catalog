import psycopg2

conn = psycopg2.connect(database="postgres", user="postgres", password="babaji9lm", host="localhost", port="5432")
conn.autocommit = True
c = conn.cursor()

c.execute("""CREATE DATABASE CATELOG; """)
conn.commit()
conn.close()

conn = psycopg2.connect(database="catelog", user="postgres", password="babaji9lm", host="localhost", port="5432")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS public.item2 (
  id  SERIAL PRIMARY KEY  ,
  name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  user_email TEXT NOT NULL
)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS public.categories2 (
  id  SERIAL  PRIMARY KEY NOT NULL,
  name TEXT
);""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS users2 (
  username TEXT,
  email TEXT PRIMARY KEY NOT NULL
);""")
conn.commit()

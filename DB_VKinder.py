import psycopg2
import sqlalchemy

DSN = 'postgresql://postgres:dfc.irf1999@localhost:5432/VKinder'
engine = sqlalchemy.create_engine(DSN)
connection = engine.connect()


def create_db():
    initial_connection = psycopg2.connect(
        database='VKinder',
        user='postgres',
        password='dfc.irf1999',
        host='localhost',
        port='5432'
    )
    initial_connection.close()


def create_tables():
    connection.execute('''
    CREATE TABLE IF NOT EXISTS find_users (
    id integer PRIMARY KEY,
    first_name varchar(40) NOT NULL,
    last_name varchar(40) NOT NULL,
    photo_inf varchar(150) NOT NULL
    );
    ''')


create_db()
create_tables()


def add_find_person(id, first_name, last_name, photo_inf):
    if not connection.execute(f"SELECT id FROM find_users WHERE id = {id};").fetchone():
        connection.execute('''
            INSERT INTO find_users(id, first_name, last_name, photo_inf) VALUES(%s, %s, %s, %s);
            ''', (id, first_name, last_name, photo_inf))
        print('Пользователь добавлен в базу данных')


def check_users(cand_id):
    if connection.execute(f"SELECT id FROM find_users WHERE id = {cand_id};").fetchone():
        return False
    return True

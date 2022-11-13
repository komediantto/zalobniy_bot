import re
import sqlite3 as db

from handlers import main_handlers, text
from handlers.handlers_for_settings import Settings


def sql_start():
    global conn, cur
    conn = db.connect('db.sqlite3')
    cur = conn.cursor()
    if conn:
        print('DB is OK!')
    conn.execute('CREATE TABLE IF NOT EXISTS general('
                 'id INTEGER PRIMARY KEY, '
                 'full_name TEXT, '
                 'phone TEXT, '
                 'block INTEGER DEFAULT 0)')
    conn.commit()


# Создание словаря из колонок таблицы
def dict_factory(table_name: str, column_name: str, id):
    conn.row_factory = db.Row
    cur.execute(f'SELECT {column_name} FROM {table_name} WHERE id = {id}')
    return cur.fetchall()


# Добавление данных от пользователя в таблицы
async def sql_add_command(message, state):
    async with state.proxy() as data:
        id = message.from_user.id
        try:
            cur.execute('INSERT INTO general(id, full_name, phone) '
                        'VALUES (?, ?, ?)', tuple(data.values()))
            conn.commit()
            await main_handlers.hello(message)
            data = dict_factory('general', 'id, full_name, phone', id)
        except db.IntegrityError:
            await message.answer('Вы уже регистрировались!')
            data = dict_factory('general', 'id, full_name, phone', id)
            await main_handlers.hello(message)


async def change_name(message, state):
    id = message.from_user.id
    counter = message.text.count(' ')
    if re.search('[a-zA-Z]', message.text):
        await message.answer(text.NAME_INCORRECT, parse_mode='HTML')
        await state.set_state(Settings.name)
    elif not message.text.istitle():
        await message.answer(text.NAME_INCORRECT, parse_mode='HTML')
        await state.set_state(Settings.name)
    elif counter != 1:
        await message.answer(text.NAME_INCORRECT, parse_mode='HTML')
        await state.set_state(Settings.name)
    else:
        sql_update_query = """Update general set full_name = ? where id = ?"""
        data = (message.text, id)
        cur.execute(sql_update_query, data)
        conn.commit()
        await state.finish()


async def change_phone(message, state):
    id = message.from_user.id
    sql_update_query = """Update general set phone = ? where id = ?"""
    data = (message.text, id)
    cur.execute(sql_update_query, data)
    conn.commit()
    await state.finish()


def get_users_id():
    cur.execute('SELECT id FROM general')
    return cur.fetchall()


def get_info(id):
    cur.execute(f'''SELECT full_name, phone FROM general WHERE id = {id}''')
    return cur.fetchall()


def user_is_blocked(id):
    cur.execute(f'''SELECT block FROM general WHERE id = {id}''')
    blocked = cur.fetchone()
    if blocked is None:
        return False
    elif blocked[0] == 0:
        return False
    else:
        return True


def blacklist_user(id, action):
    if action == 'add':
        sql_update_query = """Update general set block = ? where id = ?"""
        data = (1, id)
        cur.execute(sql_update_query, data)
        conn.commit()
    elif action == 'remove':
        sql_update_query = """Update general set block = ? where id = ?"""
        data = (0, id)
        cur.execute(sql_update_query, data)
        conn.commit()
    else:
        pass


def get_id(name):
    sql_get_query = '''SELECT id FROM general WHERE full_name = ?'''
    cur.execute(sql_get_query, (name,))
    id = cur.fetchone()
    return id[0]

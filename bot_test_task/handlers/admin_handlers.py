from sqlite3 import OperationalError

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import keyboards.base as keyboards
from BotDB import db
from create_bot import bot

from . import text


class Admin(StatesGroup):
    text = State()
    id = State()
    ban = State()


async def spam(message: types.Message, state: FSMContext):
    await message.answer('Введите текст рассылки:')
    await state.set_state(Admin.text)


async def spam_execute(message: types.Message, state: Admin.text):
    spam_base = db.get_users_id()
    for i in range(len(spam_base)):
        await bot.send_message(spam_base[i][0], message.text)
    await message.answer('Рассылка завершена успешно')
    await state.finish()
    await message.answer(text.ADMIN_PANEL,
                         parse_mode='HTML',
                         reply_markup=keyboards.admin_keyboard())


async def info(message: types.Message, state: FSMContext):
    await message.answer('Введите ID пользователя:')
    await state.set_state(Admin.id)


async def get_info(message: types.Message, state: Admin.id):
    id = message.text
    try:
        info = db.get_info(id)
        name = info[0][0]
        phone = info[0][1]
        await message.answer(f'<b>Имя и фамилия:</b> {name}\n '
                             f'<b>Номер телефона: {phone} </b>',
                             parse_mode='HTML',
                             reply_markup=keyboards.admin_keyboard())
        await state.finish()
    except OperationalError:
        await message.answer('Введите корректный ID:')
        await state.set_state(Admin.id)


async def blacklist(message: types.Message, state: FSMContext):
    await message.answer('Введите ID пользователя для блокировки:')
    await state.set_state(Admin.ban)


async def blacklist_add(message: types.Message, state: Admin.ban):
    user_id = message.text
    try:
        if not db.user_is_blocked(user_id):
            db.blacklist_user(user_id, 'add')
            await state.finish()
            await message.answer('Пользователь успешно заблокирован!')
        else:
            await state.update_data(ban=user_id)
            await message.answer(f'Пользователь {user_id} уже заблокирован. '
                                 'Разблокировать?',
                                 reply_markup=keyboards.block_keyboard())
            await state.reset_state(with_data=False)
    except OperationalError:
        await message.answer('Введите корректный ID:')
        await state.set_state(Admin.ban)


async def blacklist_remove(message: types.Message, state: Admin.ban):
    current_data = await state.get_data()
    db.blacklist_user(current_data['ban'], 'remove')
    await message.answer('Пользователь успешно разблокирован')
    await state.finish()
    await message.answer(text.ADMIN_PANEL,
                         parse_mode='HTML',
                         reply_markup=keyboards.admin_keyboard())


async def blacklist_dont_remove(message: types.Message, state: Admin.ban):
    await state.finish()
    await message.answer(text.ADMIN_PANEL,
                         parse_mode='HTML',
                         reply_markup=keyboards.admin_keyboard())


def register(dp: Dispatcher):
    dp.register_message_handler(spam, Text(equals='Рассылка'))
    dp.register_message_handler(spam_execute, state=Admin.text)
    dp.register_message_handler(info, Text(equals='Информация'))
    dp.register_message_handler(get_info, state=Admin.id)
    dp.register_message_handler(blacklist, Text(equals='Чёрный список'))
    dp.register_message_handler(blacklist_add, state=Admin.ban)
    dp.register_message_handler(blacklist_remove, Text(equals='✅Да'))
    dp.register_message_handler(blacklist_dont_remove, Text(equals='❌Нет'))

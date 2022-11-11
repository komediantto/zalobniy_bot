import os
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

import keyboards.base as keyboards
from BotDB import db

from . import text

load_dotenv()

admin_list = (os.getenv("ADMIN_ID")).split(', ')


class User(StatesGroup):
    id = State()
    full_name = State()
    phone = State()


async def start(message: types.Message, state: FSMContext):
    user_list = db.get_users_id()
    if not db.user_is_blocked(str(message.from_user.id)) or message.from_user.id not in user_list:
        if str(message.from_user.id) in admin_list:
            await message.answer(text.ADMIN_PANEL,
                                parse_mode='HTML',
                                reply_markup=keyboards.admin_keyboard())
        else:
            await state.update_data(id=message.from_user.id)
            await message.answer(text.REGISTRATION, parse_mode='HTML')
            await state.set_state(User.full_name)
    else:
        await message.answer('Вы были заблокированы администратором.')

async def name_is_correct(name, state):
    counter = name.text.count(' ')
    if re.search('[a-zA-Z]', name.text):
        await name.answer(text.NAME_INCORRECT, parse_mode='HTML')
        await state.set_state(User.full_name)
    elif not name.text.istitle():
        await name.answer(text.NAME_INCORRECT, parse_mode='HTML')
        await state.set_state(User.full_name)
    elif counter != 1:
        await name.answer(text.NAME_INCORRECT, parse_mode='HTML')
        await state.set_state(User.full_name)
    else:
        await state.update_data(full_name=name.text)
        await name.answer(text.PHONE, parse_mode='HTML')
        await state.set_state(User.phone)

async def phone_is_correct(phone, state):
    if len(phone.text) != 12 or not phone.text.startswith('+7'):
        await phone.answer(text.PHONE_INCORRECT, parse_mode='HTML')
    else:
        await state.update_data(phone=phone.text)
        # current_data = await state.get_data()
        await db.sql_add_command(phone, state)
        await state.finish()

def register(dp: Dispatcher):
    dp.register_message_handler(start, Command('start'))
    dp.register_message_handler(name_is_correct, state=User.full_name)
    dp.register_message_handler(phone_is_correct, state=User.phone)
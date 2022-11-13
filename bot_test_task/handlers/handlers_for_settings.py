import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import keyboards.base as keyboards
from BotDB import db
from create_bot import dp

from . import text


class Settings(StatesGroup):
    name = State()
    phone = State()


async def settings(message: types.Message):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        await message.answer(text.SETTINGS,
                             parse_mode='HTML',
                             reply_markup=keyboards.inline_keyboard_settings())
    else:
        await message.answer('Вы были заблокированы администратором.')


@dp.callback_query_handler(text='change_name')
async def change_name(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(text.CHANGE_NAME, parse_mode='HTML')
    await state.set_state(Settings.name)
    await query.answer()


async def get_new_name(message: types.Message, state: FSMContext):
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
        await db.change_name(message, state)
        await state.finish()
        await message.answer(text.NEW_NAME, parse_mode='HTML')
        await message.answer(text.GREETINGS,
                             reply_markup=keyboards.main_keyboard())


@dp.callback_query_handler(text='change_phone')
async def change_phone(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(text.CHANGE_PHONE, parse_mode='HTML')
    await state.set_state(Settings.phone)
    await query.answer()


async def get_new_phone(message: types.Message, state: FSMContext):
    if len(message.text) != 12 or not message.text.startswith('+7'):
        await message.answer(text.PHONE_INCORRECT, parse_mode='HTML')
        await state.set_state(Settings.phone)
    else:
        await db.change_phone(message, state)
        await message.answer(text.NEW_PHONE, parse_mode='HTML')
        await message.answer(text.GREETINGS,
                             reply_markup=keyboards.main_keyboard())


@dp.callback_query_handler(text='settings_back')
async def back(query: types.CallbackQuery):
    await query.message.answer(text.GREETINGS,
                               reply_markup=keyboards.main_keyboard())
    await query.answer()


def register(dp: Dispatcher):
    dp.register_message_handler(settings, Text(equals='⚙️Настройки'))
    dp.register_message_handler(get_new_name, state=Settings.name)
    dp.register_message_handler(get_new_phone, state=Settings.phone)

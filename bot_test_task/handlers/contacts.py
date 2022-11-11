from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

import keyboards.base as keyboards
from BotDB import db

from . import text


async def get_contacts(message: types.Message):
    await message.answer(text.CONTACTS, parse_mode='HTML')
    id = message.from_user.id
    if not db.user_is_blocked(id):
        await message.answer(text.GREETINGS, 
                            reply_markup=keyboards.main_keyboard())
    else:
        await message.answer('Вы были заблокированы администратором.')


def register(dp: Dispatcher):
    dp.register_message_handler(get_contacts, Text(equals='☎️Полезные контакты'))
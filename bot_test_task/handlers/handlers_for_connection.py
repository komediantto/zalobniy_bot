import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

import keyboards.base as keyboards
from BotDB import db
from create_bot import bot, dp

from . import text

load_dotenv()

group_id = os.getenv("ADMIN_GROUP_ID")


class Question(StatesGroup):
    text = State()


class Phone(StatesGroup):
    number = State()


async def choose_type_connect(message: types.Message):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        global ID
        ID = message.from_user.id
        await message.answer(text.CHOOSE_TYPE_CONNECT,
                             parse_mode='HTML',
                             reply_markup=keyboards.inline_keyboard_for_call())
    else:
        await message.answer('Вы были заблокированы администратором.')


@dp.callback_query_handler(text='call_me')
async def call_me(query: types.CallbackQuery):
    data = db.dict_factory('general', 'phone', ID)
    phone = data[0][0]
    await query.message.answer(
        f'<b>Это Ваш верный номер телефона {phone}?</b>'
        ' <i>Если да, нажмите соответствующую кнопку, '
        '<b>если нет,</b> впишите свой актуальный номер'
        ' телефона здесь</i>', parse_mode='HTML',
        reply_markup=keyboards.inline_kb_yes_or_change())
    await query.answer()


@dp.callback_query_handler(text='text_me')
async def text_me(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(
        text.DISPATCHER,
        reply_markup=keyboards.inline_keyboard_finish_dialog())
    await state.set_state(Question.text)
    await query.answer()


async def get_question_text(message: types.Message):
    await bot.forward_message(group_id, message_id=message.message_id,
                              from_chat_id=message.chat.id)


@dp.callback_query_handler(text='finish', state=Question.text)
async def finish_dialog(query: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.finish()
    await query.message.answer(text.DIALOG_CLOSED, parse_mode='HTML')
    await query.message.answer(text.GREETINGS,
                               reply_markup=keyboards.main_keyboard())
    await query.answer()


@dp.callback_query_handler(text='yes')
async def yes(query: types.CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    if current_data != {}:
        await bot.send_message(group_id,
                               f'Пользователь @{query.from_user.username} '
                               'оставил заявку на звонок по номеру '
                               f'{current_data["phone"]}')
        await query.message.answer(text.ADMIN_CALL, parse_mode='HTML')
        await query.message.answer(text.GREETINGS,
                                   reply_markup=keyboards.main_keyboard())
        await state.finish()
        await query.answer()
    else:
        data = db.dict_factory('general', 'phone', ID)
        phone = data[0][0]
        await bot.send_message(group_id,
                               f'Пользователь @{query.from_user.username} '
                               f'оставил заявку на звонок по номеру {phone}')
        await query.message.answer(text.ADMIN_CALL, parse_mode='HTML')
        await query.message.answer(text.GREETINGS,
                                   reply_markup=keyboards.main_keyboard())
        await state.finish()
        await query.answer()


@dp.callback_query_handler(text='change')
async def change_button(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer('Введите актуальный номер')
    await state.set_state(Phone.number)
    await query.answer()


async def change(message: types.Message, state: FSMContext):
    phone = message.text
    if len(phone) != 12 or not phone.startswith('+7'):
        await message.answer(text.PHONE_INCORRECT, parse_mode='HTML')
    else:
        await state.update_data(phone=phone)
        await message.answer(f'<b>Это Ваш верный номер телефона {phone}? '
                             '</b><i>Если да, нажмите соответствующую кнопку, '
                             '<b>если нет,</b> впишите свой актуальный номер '
                             'телефона здесь</i>', parse_mode='HTML',
                             reply_markup=keyboards.inline_kb_yes_or_change())
        await state.reset_state(with_data=False)


@dp.callback_query_handler(text='call_back')
async def back(query: types.CallbackQuery):
    await query.message.answer(text.GREETINGS,
                               reply_markup=keyboards.main_keyboard())
    await query.answer()


def register(dp: Dispatcher):
    dp.register_message_handler(choose_type_connect, Text(equals='📞Связаться'))
    dp.register_message_handler(get_question_text, state=Question.text)
    dp.register_message_handler(change, state=Phone.number)

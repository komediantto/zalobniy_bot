import os
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import AdminFilter, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BadRequest
from dotenv import load_dotenv

import keyboards.base as keyboards
from BotDB import db
from create_bot import bot, dp

from . import text

load_dotenv()

group_id = os.getenv("BID_GROUP_ID")
proposal_group_id = os.getenv('PROPOSAL_GROUP_ID')
admin_list = (os.getenv("ADMIN_ID")).split(', ')

class Bid(StatesGroup):
    address = State()
    photo = State()
    reason = State()

class Proposal(StatesGroup):
    proposal = State()

class Answer(StatesGroup):
    id = State()
    text = State()
    
global data_for_answer
data_for_answer = {}

async def hello(message: types.Message):
    try:
        id = message.from_user.id
        if not db.user_is_blocked(id):
            await message.answer(text.GREETINGS, reply_markup=keyboards.main_keyboard())
        else:
            await message.answer('Вы были заблокированы администратором.')
    except AttributeError:
        await bot.send_message(text=text.GREETINGS,
                               chat_id=id,
                               reply_markup=keyboards.main_keyboard())


async def put_bid1(message: types.Message):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        await message.answer(text.CHOOSE_CATEGORY, reply_markup=keyboards.category_keyboard())
    else:
        await message.answer('Вы были заблокированы администратором.')

async def back(message: types.Message):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        await message.answer(text.GREETINGS, reply_markup=keyboards.main_keyboard())
    else:
        await message.answer('Вы были заблокированы администратором.')

async def put_bid2(message: types.Message, state: FSMContext):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        if message == {'raw_state': None}:
            await state.set_state(Bid.address)
            await bot.send_message(text=text.STEP_ONE,
                                chat_id= id,
                                reply_markup=keyboards.inline_keyboard(), parse_mode='HTML')
        else:
            await state.set_state(Bid.address)
            await message.answer(text.STEP_ONE, reply_markup=keyboards.inline_keyboard(), parse_mode='HTML')
    else:
        await message.answer('Вы были заблокированы администратором.')


async def first_state(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Bid.photo)
    current_data=await state.get_data()
    await message.answer(text.STEP_TWO,
                        reply_markup=keyboards.inline_keyboard(),
                        parse_mode='HTML')
    
async def second_state(message: types, state: Bid.photo):
    if message.photo:
        await state.update_data(photo=message.photo[2].file_id)
    elif message.video:
        await state.update_data(photo=message.video.file_id)
    current_data=await state.get_data()
    await message.answer(text.STEP_THREE,
                        reply_markup=keyboards.inline_keyboard_only_back(),
                        parse_mode='HTML')
    await state.set_state(Bid.reason)
    
async def third_state(message: types.Message, state: Bid.reason):
    id = message.from_user.id
    data = db.dict_factory('general', 'full_name, phone', id)
    full_name = data[0][0]
    phone = data[0][1]
    await state.update_data(reason=message.text)
    current_data=await state.get_data()
    address = current_data['address']
    if current_data['photo'] != 'Без фото' and current_data['photo'] != False:
        photo = current_data['photo']
    reason = current_data['reason']
    username = '@' + message.from_user.username
    NEW_BID = f'⛔️Поступила новая жалоба:\n{username}\n<b>Имя и фамилия:</b> {full_name}\n<b>Номер телефона:{phone}</b>\n<b>Адрес:</b>{address}\n<b>Содержание:</b>{reason}'
    await message.answer(text.BID_ACCEPTED, parse_mode='HTML')
    await state.finish()
    if current_data['photo'] == 'Без фото' or current_data['photo'] == False:
        pass
    else:
        try:
            await bot.send_photo(group_id, photo)
        except BadRequest:
            await bot.send_video(group_id, photo)
    await bot.send_message(group_id,
                           NEW_BID,
                           parse_mode='HTML',
                           reply_markup=keyboards.answer_keyboard())
    await message.answer(text.GREETINGS, reply_markup=keyboards.main_keyboard())


@dp.callback_query_handler(text='skip', state='*')
async def skip(query: types.CallbackQuery, state: FSMContext, **kwargs):
    answer_data = query.data
    current_data = await state.get_data()
    if len(current_data) == 0:
        if answer_data == 'skip':
            await state.reset_state(with_data=False)
            await state.update_data(address='Нет адреса')
            current_data=await state.get_data()
            await query.message.answer(text.STEP_TWO,
                                    reply_markup=keyboards.inline_keyboard(),
                                    parse_mode='HTML')
            await state.set_state(Bid.photo)
            await query.answer()
        else:
            current_data = await state.get_data()
            if len(current_data) == 0:
                await first_state(kwargs)
            else:
                await third_state(kwargs)
    else:
        if answer_data == 'skip':
            await state.update_data(photo='Без фото')
            current_data=await state.get_data()
            await query.message.answer(text.STEP_THREE,
                                    reply_markup=keyboards.inline_keyboard_only_back(),
                                    parse_mode='HTML')
            await state.set_state(Bid.reason)
            await query.answer()
        else:
            await state.set_state(Bid.photo)
            await second_state(kwargs)


async def sended_not_photo(message: types.Message, state: FSMContext):
    await message.answer(text.SEND_PHOTO, parse_mode='HTML')
    await message.answer(text.STEP_TWO,
                        reply_markup=keyboards.inline_keyboard(),
                        parse_mode='HTML')
    await state.set_state(Bid.photo)


@dp.callback_query_handler(text='back', state='*')
async def back(query: types.CallbackQuery, state: FSMContext, **kwargs):
    answer_data = query.data
    current_data = await state.get_data()
    if ('photo' not in current_data.keys() or current_data['photo'] == False) and len(current_data)>0:
        if answer_data == 'back':
            await state.reset_state()
            current_data = await state.get_data()
            await query.message.answer(text.STEP_ONE,
                                       reply_markup=keyboards.inline_keyboard(),
                                       parse_mode='HTML')
            await state.set_state(Bid.address)
            await query.answer()
        else:
            await second_state(kwargs)
            await state.set_state(Bid.photo)
            
            current_data = await state.get_data()
    elif 'photo' not in current_data.keys() or (current_data['photo'] == ' ' and current_data['address'] == 'Нет адреса'):
        if answer_data == 'back':
            await state.reset_state(with_data=False)
            await state.finish()
            await query.message.answer(text.CHOOSE_CATEGORY, reply_markup=keyboards.category_keyboard())
            await query.answer()
        else:
            await first_state(kwargs)
    elif current_data['photo']:
        if answer_data == 'back':
            await state.reset_state(with_data=False)
            await state.update_data(photo=False)
            current_data = await state.get_data()
            await query.message.answer(text.STEP_TWO,
                        reply_markup=keyboards.inline_keyboard(),
                        parse_mode='HTML')
            await state.set_state(Bid.photo)
            await query.answer()
        else:
            await state.set_state(Bid.reason)
            await second_state(kwargs)
    else:
        if answer_data == 'back':
            await state.reset_state(with_data=False)
            await state.finish()
            await query.message.answer(text.CHOOSE_CATEGORY, reply_markup=keyboards.category_keyboard())
            await query.answer()

async def proposal(message: types.Message, state: FSMContext):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        await message.answer(text.GET_PROPOSAL,
                            parse_mode='HTML',
                            reply_markup = keyboards.inline_keyboard_proposal_back())
        await state.set_state(Proposal.proposal)
    else:
        await message.answer('Вы были заблокированы администратором.')

async def get_proposal(message: types.Message, state: FSMContext):
    proposal = message.text
    if message.photo:
        photo = message.photo[2].file_id
        await bot.send_photo(proposal_group_id, photo=photo)
        proposal = message.caption
    username = '@' + message.from_user.username
    id = message.from_user.id
    data = db.dict_factory('general', 'full_name, phone', id)
    full_name = data[0][0]
    phone = data[0][1]
    NEW_PROPOSAL = f'💡Поступило новое предложение:\n{username}\n<b>Имя и фамилия:</b> {full_name}\n<b>Номер телефона:{phone}</b>\n<b>Содержание:</b>{proposal}'
    await bot.send_message(proposal_group_id,
                           NEW_PROPOSAL,
                           parse_mode='HTML',
                           reply_markup=keyboards.answer_keyboard())
    await state.finish()
    await message.answer(text.PROPOSAL_ACCEPTED, parse_mode='HTML')
    await message.answer(text.GREETINGS, reply_markup=keyboards.main_keyboard())

@dp.callback_query_handler(text='proposal_back', state=Proposal.proposal)
async def proposal_back(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.answer(text.CHOOSE_CATEGORY,
                               reply_markup=keyboards.category_keyboard())
    await query.answer()

async def main_back(message: types.Message):
    id = str(message.from_user.id)
    if not db.user_is_blocked(id):
        await message.answer(text.GREETINGS, reply_markup=keyboards.main_keyboard())
    else:
        await message.answer('Вы были заблокированы администратором.')

@dp.callback_query_handler(text='answer')
async def answer_to_user(query: types.CallbackQuery):
    if str(query.from_user.id) in admin_list:
        text = query['message']['text']
        name = (re.search('(?<=Имя и фамилия: ).*.+?(?=\\nНомер телефона)', text).group()).rstrip()
        id = int(db.get_id(name=name))
        data_for_answer['id'] = id
        await query.answer('Введите текст ответа:')
    else:
        await query.answer('Нужно обладать правами администратора')

async def get_message_for_user(message: types.Message):
    if message.chat.type == 'supergroup':
        data_for_answer['text'] = message.text
        await bot.send_message(data_for_answer['id'], data_for_answer['text'])
        data_for_answer.clear()
    else:
        pass
    

def register(dp: Dispatcher):
    dp.register_message_handler(put_bid1, Text(equals='📛Оставить заявку'))
    dp.register_message_handler(put_bid2, Text(equals='📛Oставить заявку'))
    dp.register_message_handler(first_state, state=Bid.address)
    dp.register_message_handler(third_state, state=Bid.reason)
    dp.register_message_handler(sended_not_photo, content_types=text.CONTENT_TYPES, state=Bid.photo)
    dp.register_message_handler(second_state, content_types=['photo', 'video'], state=Bid.photo)
    dp.register_message_handler(proposal, Text(equals='💡Поделиться предложением'))
    dp.register_message_handler(get_proposal, state=Proposal.proposal, content_types=['text', 'photo'])
    dp.register_message_handler(main_back, Text(equals='🔙Назад'))
    dp.register_message_handler(get_message_for_user, AdminFilter())

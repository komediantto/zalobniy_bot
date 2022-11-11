from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('📛Оставить заявку')
    b2 = KeyboardButton('📞Связаться')
    b3 = KeyboardButton('⚙️Настройки')
    b4 = KeyboardButton('☎️Полезные контакты')
    keyboard.row(b1, b2)
    keyboard.row(b3)
    keyboard.row(b4)
    return keyboard

def category_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    b1 = KeyboardButton('📛Oставить заявку')
    b2 = KeyboardButton('💡Поделиться предложением')
    b3 = KeyboardButton('🔙Назад')
    keyboard.row(b1, b2)
    keyboard.row(b3)
    return keyboard
    
def inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    button_skip = InlineKeyboardButton(text='▶️Пропустить', callback_data='skip')
    button_back = InlineKeyboardButton(text='🔙Назад', callback_data='back')
    keyboard.row(button_skip)
    keyboard.row(button_back)
    return keyboard

def inline_keyboard_only_back():
    keyboard = InlineKeyboardMarkup()
    button_back = InlineKeyboardButton(text='🔙Назад', callback_data='back')
    keyboard.row(button_back)
    return keyboard

def inline_keyboard_for_call():
    keyboard = InlineKeyboardMarkup()
    button_call_me = InlineKeyboardButton(text='📞Перезвоните мне', callback_data='call_me')
    button_text_me = InlineKeyboardButton(text='📞Свяжитесь со мной в чат-боте',
                                          callback_data='text_me')
    button_back = InlineKeyboardButton(text='🔙Назад', callback_data='call_back')
    keyboard.row(button_call_me)
    keyboard.row(button_text_me)
    keyboard.row(button_back)
    return keyboard

def inline_kb_yes_or_change():
    keyboard = InlineKeyboardMarkup()
    button_yes = InlineKeyboardButton(text='✅Да', callback_data='yes')
    button_change = InlineKeyboardButton(text='🔙Оставить номер телефона', callback_data='change')
    keyboard.row(button_yes, button_change)
    return keyboard

def inline_keyboard_finish_dialog():
    keyboard = InlineKeyboardMarkup()
    button_finish = InlineKeyboardButton(text='❌📞Завершить диалог', callback_data='finish')
    keyboard.row(button_finish)
    return keyboard

def inline_keyboard_settings():
    keyboard = InlineKeyboardMarkup()
    button_change_name = InlineKeyboardButton(text='🛠Поменять имя', callback_data='change_name')
    button_change_phone = InlineKeyboardButton(text='🛠Сменить номер', callback_data='change_phone')
    button_back = InlineKeyboardButton(text='🔙Назад', callback_data='settings_back')
    keyboard.row(button_change_name, button_change_phone)
    keyboard.row(button_back)
    return keyboard

def inline_keyboard_proposal_back():
    keyboard = InlineKeyboardMarkup()
    button_back = InlineKeyboardButton(text='🔙Назад', callback_data='proposal_back')
    keyboard.row(button_back)
    return keyboard

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Рассылка')
    b2 = KeyboardButton('Информация')
    b3 = KeyboardButton('Чёрный список')
    keyboard.row(b1, b2)
    keyboard.row(b3)
    return keyboard

def block_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('✅Да')
    b2 = KeyboardButton('❌Нет')
    keyboard.row(b1, b2)
    return keyboard

def answer_keyboard():
    keyboard = InlineKeyboardMarkup()
    answer_button = InlineKeyboardButton(text='Ответить', callback_data='answer')
    keyboard.row(answer_button)
    return keyboard
from aiogram import executor

from BotDB import db
from create_bot import dp
from handlers import (admin_handlers, contacts, handlers_for_connection,
                      handlers_for_settings, main_handlers, registration)


async def start(_):
    print('Бот запущен')
    db.sql_start()


main_handlers.register(dp)
registration.register(dp)
contacts.register(dp)
handlers_for_connection.register(dp)
handlers_for_settings.register(dp)
admin_handlers.register(dp)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True, on_startup=start)

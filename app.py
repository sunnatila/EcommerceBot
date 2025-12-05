import asyncio
import logging
import sys

from loader import dp, bot, db, main_db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup():
    # Birlamchi komandalar (/star va /help)
    await set_default_commands()

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify()


async def main() -> None:
    await main_db()
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

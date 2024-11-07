#!/usr/bin/env python
import sys
import logging
import asyncio
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message


from data import DataHandler
import keyboards as kb
import handlers 
import filters 
import credentials

tlg_token = credentials.TELEGRAM_BOT_TOKEN
gss_key = credentials.SPREADSHEET_KEY
owner_id = int(credentials.OWNER_USER_ID)

dp = Dispatcher()
dh = DataHandler(gss_key)

dp.message.register(
    partial(handlers.start_handler, owner_id=owner_id), 
    filters.start_filter
)
dp.message.register(
    partial(handlers.find_handler, owner_id=owner_id, datahandler=dh, keyboard=kb.plant_kb), 
    filters.find_filter
)
dp.message.register(
    partial(handlers.findall_handler, owner_id=owner_id, datahandler=dh), 
    filters.findall_filter
)
dp.message.register(
    partial(handlers.get_plant_handler, owner_id=owner_id, datahandler=dh, keyboard=kb.plant_kb), 
    filters.get_plant_filter
)
dp.message.register(
    partial(handlers.genus_stat_handler, owner_id=owner_id, datahandler=dh), 
    filters.genus_stat_filter
)


async def main() -> None:
    bot = Bot(tlg_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try: 
        await dp.start_polling(bot)
    finally: 
        await bot.session.close()


if __name__ == "__main__":
    file_handler = logging.FileHandler(filename='log.txt')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - " 
                "(%(filename)s).%(funcName)s(%(lineno)d - %(message)s)",
        handlers=handlers
    )
    
    asyncio.run(main())
    
    
    
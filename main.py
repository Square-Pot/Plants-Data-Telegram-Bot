#!/usr/bin/env python
import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F

import credentials
from data import DataHandler
from utils import make_plant_message
import keyboards as kb

tlg_token = credentials.TELEGRAM_BOT_TOKEN
gss_key = credentials.SPREADSHEET_KEY
owner_id = int(credentials.OWNER_USER_ID)

dp = Dispatcher()
dh = DataHandler(gss_key)


@dp.callback_query(F.data == "get_plant_details")
async def send_random_value(callback: CallbackQuery):
    await callback.message.answer('Plant details will be here...')
    await callback.answer()
    
    
@dp.message(Command(commands=['find']))
async def command_open_handler(message: Message, command) -> None:    
    if message.from_user.id == owner_id:
        request = command.args
        plants = dh.search_str(request.strip())
        if plants.empty:
            await message.answer("Sorry, no plants was found.")
            return
        if len(plants) > 10: 
            await message.answer(f"Here are the first 10 results from { len(plants) }:")
            plants = plants[:10]
        for i, plant in plants.iterrows():
            await message.answer(make_plant_message(plant), reply_markup=kb.plant_kb)
        logging.info(f"Find request: { request }, results: {len(plants)}")
    else:
        await message.answer(f"Sorry, this is personal bot. Your id: { message.from_user.id }, owner_id: {owner_id}")
        logging.info(f"Stranger try: {message.from_user.full_name} (id: { message.from_user.id })")

    
@dp.message(Command(commands=['start', 'help']))
async def command_start_handler(message: Message) -> None:  
    await message.answer("Sorry, this is personal bot")


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
    
    
    
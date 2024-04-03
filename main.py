#!/usr/bin/env python

import logging
import asyncio
from io import BytesIO
import requests
import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ChatMemberMember, ChatMemberOwner
from aiogram.utils.markdown import hbold, hcode, text, hitalic
from aiogram import F

import credentials


tlg_token = credentials.TELEGRAM_BOT_TOKEN
gss_key = credentials.SPREADSHEET_KEY
owner_id = int(credentials.OWNER_USER_ID)

# keyboard = [[KeyboardButton(text="...")]]
# kb_markup = ReplyKeyboardMarkup(
#     resize_keyboard=True, 
#     one_time_keyboard=True,
#     keyboard=keyboard
# )


dp = Dispatcher()

def make_plant_message(raw):
    msg = text(
        hbold(raw['field_number'] + '\n') if raw['field_number'] else '', 
        hitalic(raw['genus']),
        'ssp.' if raw['subspecies'] else '',
        hitalic(raw['subspecies']) if raw['subspecies'] else '',
        'var.' if raw['variety'] else '',
        hitalic(raw['variety']) if raw['variety'] else '',
    )
    return msg

@dp.message(Command(commands=['find']))
async def command_open_handler(message: Message, command) -> None:    
    if message.from_user.id == owner_id:
        request = command.args
        plants = df[df.eq(request.strip()).any(axis=1)]
        if len(plants) > 0: 
            for i, row in plants.iterrows():       
                await message.answer(make_plant_message(row)) #, reply_markup=kb_markup)
        logging.info(f"Find request: { request }, results: {len(plants)}")
    else:
        await message.answer(f"Sorry, this is personal bot. Your id: { message.from_user.id }, owner_id: {owner_id}")
        logging.info(f"Stranger try: {message.from_user.full_name} (id: { message.from_user.id })")
    
    
@dp.message(Command(commands=['start', 'help']))
async def command_start_handler(message: Message) -> None:  
    await message.answer("Sorry, this is personal bot")

def get_dataframe():
    r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={ gss_key }&output=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data), index_col=0, parse_dates=['seeding_date', 'purchase_date'], dayfirst=True, date_format='%d.%m.%Y')
    return df


async def main() -> None:
    global df
    df = get_dataframe() 
    bot = Bot(tlg_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try: 
        await dp.start_polling(bot)
    finally: 
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        filename='log.txt',
        filemode='a',
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - " 
                "(%(filename)s).%(funcName)s(%(lineno)d - %(message)s)"
    )
    asyncio.run(main())
    
    
    
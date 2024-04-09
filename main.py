#!/usr/bin/env python
import sys
import logging
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.utils.markdown import hcode
from aiogram.types import BufferedInputFile

import credentials
from data import DataHandler
from utils import make_plant_message, plant_to_str
import keyboards as kb

tlg_token = credentials.TELEGRAM_BOT_TOKEN
gss_key = credentials.SPREADSHEET_KEY
owner_id = int(credentials.OWNER_USER_ID)

dp = Dispatcher()
dh = DataHandler(gss_key)


@dp.callback_query(F.data == "get_plant_details")
async def reply_plant_details(callback: CallbackQuery):
    await callback.message.answer('Plant details will be here...')
    await callback.answer()


@dp.callback_query(F.data == "show_last_photo")
async def reply_last_photo(callback: CallbackQuery):
    await callback.message.answer('Photo will be here...')
    await callback.answer()
    
    
@dp.message(Command(commands=['find']))
async def command_find_handler(message: Message, command) -> None:    
    RESULT_PLANTS_LIMIT = 5
    if message.from_user.id != owner_id:
        await message.answer(f"Sorry, this is personal bot. Your id: { message.from_user.id }, owner_id: {owner_id}")
        logging.info(f"Stranger try: {message.from_user.full_name} (id: { message.from_user.id })")
        return
    request = command.args
    plants = dh.search(request)
    if plants.shape[0] == 0:
        await message.answer("Sorry, no plants was found.")
        return
    if len(plants.index) > RESULT_PLANTS_LIMIT: 
        await message.answer(f"Here are the first 5 results from { len(plants) }. Use { hcode('/findall') } command")
        plants = plants[:RESULT_PLANTS_LIMIT]
    for i, plant in plants.iterrows():
        await message.answer(make_plant_message(plant), reply_markup=kb.plant_kb)
    logging.info(f"Find request: { request }, results: {len(plants)}")


@dp.message(Command(commands=['findall',]))
async def command_findall_handler(message: Message, command) -> None:  
    if message.from_user.id != owner_id:
        await message.answer(f"Sorry, this is personal bot. Your id: { message.from_user.id }, owner_id: {owner_id}")
        logging.info(f"Stranger try of findall: {message.from_user.full_name} (id: { message.from_user.id })")
        return 
    request = command.args
    plants = dh.search(request)
    plants = plants.uid.astype(str)
    reply_msg = ''
    cnt = 0
    for index, plant in plants.iterrows():
        cnt += 1
        plant = plant.dropna()
        reply_msg += plant_to_str(plant) + '\n'
        if cnt >= 10:
            await message.answer(reply_msg)
            reply_msg = ''
            cnt = 0     
    await message.answer(reply_msg)
    logging.info(f"Findall request: { request }, results: {len(plants)}")
        


@dp.message(Command(commands=['plant', 'uid',]))
async def command_get_plant_handler(message: Message, command) -> None:  
    if message.from_user.id != owner_id:
        await message.answer("Sorry, this is personal bot")
        return     
    uid = command.args
    plant_df = dh.get_plant_by_uid(uid)
    for i, plant in plant_df.iterrows():
        await message.answer(make_plant_message(plant), reply_markup=kb.plant_kb)

@dp.message(Command(commands=['genus_stat']))
async def command_genus_stat_handler(message: Message, command) -> None: 
    if message.from_user.id != owner_id:
        await message.answer("Sorry, this is personal bot")
        return     
    genus = command.args

    if genus: 
        genus_df = dh.df.loc[dh.df['genus'].str.contains(genus, case=False)]
        if len(genus_df) == 0:
            await message.answer(f"Sorry, couldn't find this genus: '{ genus }'")
            return
        if len(genus) < 5:
            await message.answer(f"Too short request. Should be 5 chars min.")
            return
        genus_full = genus_df.iloc[0].genus.capitalize()
        species_stat = genus_df.value_counts(genus_df['species']).plot(kind='bar')
        capture = f'Species of genus { genus_full } stats'
        x_label = 'Species'
    else:
        genuses_stat =  dh.df.value_counts(dh.df['genus']).plot(kind='bar')
        capture = 'Genera stats'
        x_label = 'Genera'


        
    bio = BytesIO()
    plt.xlabel(x_label)
    plt.ylabel("Quantity")
    plt.title(capture)
    plt.grid(True) 
    plt.tight_layout()
    plt.savefig(bio, format="png")
    bio.seek(0)
    plot_file = BufferedInputFile(bio.getvalue(), filename="plot.png")
    await message.answer_photo(plot_file, caption=capture)
    bio.close()

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
    
    
    
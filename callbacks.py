from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram import F


class PlantCallback(CallbackData, prefix="plant"):
    uid: str


async def reply_plant_details(callback: CallbackQuery, callback_data: PlantCallback):
    await callback.message.answer(f'Plant {callback_data.uid} details will be here...')
    await callback.answer()


async def reply_last_photo(callback: CallbackQuery):
    await callback.message.answer('Photo will be here...')
    await callback.answer()
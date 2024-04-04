from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


plant_kb = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text = "ℹ️ Details", callback_data="get_plant_details"),
    ]],
)
from aiogram.filters import Command, Filter
from aiogram.types import CallbackQuery


start_filter = Command(commands=['start', 'help'])
find_filter = Command(commands=['find'])
findall_filter = Command(commands=['findall',])
get_plant_filter = Command(commands=['plant', 'uid',])
genus_stat_filter = Command(commands=['genus_stat'])



class GetPlantDetailsFilter(Filter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data == "get_plant_details"
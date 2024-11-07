import logging
from io import BytesIO
import matplotlib.pyplot as plt

from aiogram.types import Message
from aiogram.utils.markdown import hcode
from aiogram.types import BufferedInputFile

from callbacks import PlantCallback
from utils import make_plant_message, is_owner, plant_to_str
import messages

logger = logging.getLogger(__name__)


async def start_handler(message: Message, owner_id) -> None:  
    if not await is_owner(message, owner_id):
        await message.answer("Sorry, this is personal bot (hello from handler)")
    await message.answer(messages.HELP_MESSAGE)
    
async def find_handler(message: Message, command, owner_id, datahandler, keyboard, result_plants_limit=5) -> None:    
    if not await is_owner(message, owner_id):
        return
    request = command.args
    plants = datahandler.search(request)
    if plants.shape[0] == 0:
        await message.answer("Sorry, no plants was found.")
        return
    if len(plants.index) > result_plants_limit: 
        await message.answer(f"Here are the first 5 results from { len(plants) }. Use { hcode('/findall') } command")
        plants = plants[:result_plants_limit]
    for i, plant in plants.iterrows():
        keyboard.inline_keyboard[0][0].callback_data = PlantCallback(uid=plant.uid).pack()  
        await message.answer(make_plant_message(plant), reply_markup=keyboard)
    logging.info(f"Find request: { request }, results: {len(plants)}")

async def findall_handler(message: Message, command, owner_id, datahandler) -> None:  
    if not await is_owner(message, owner_id):
        return
    request = command.args
    plants = datahandler.search(request)
    # plants = plants.uid.astype(str)
    reply_msg = ''
    for cnt, (index, plant) in enumerate(plants.iterrows()):
        plant = plant.dropna()
        reply_msg += plant_to_str(plant) + '\n'
        if cnt % 10 == 0:
            await message.answer(reply_msg)
            reply_msg = ''     
    await message.answer(reply_msg)
    logging.info(f"Findall request: { request }, results: {len(plants)}")
    
async def get_plant_handler(message: Message, command, owner_id, datahandler, keyboard) -> None:  
    if not await is_owner(message, owner_id):
        return  
    uid = command.args
    plant_df = datahandler.get_plant_by_uid(uid)
    for i, plant in plant_df.iterrows():
        await message.answer(make_plant_message(plant), reply_markup=keyboard)

async def genus_stat_handler(message: Message, command, owner_id, datahandler) -> None: 
    if not await is_owner(message, owner_id):
        return     
    genus = command.args

    if genus: 
        genus_df = datahandler.df.loc[datahandler.df['genus'].str.contains(genus, case=False)]
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
        genuses_stat =  datahandler.df.value_counts(datahandler.df['genus']).plot(kind='bar')
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

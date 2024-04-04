
import pandas
from aiogram.utils.markdown import hbold, hcode, text, hitalic


def make_plant_message(plant: pandas.core.series.Series) -> str:
    plant = plant.dropna()
    msg_list = []
    if hasattr(plant, 'field_number'):
        msg_list.append(hbold(f"{ plant.field_number }\n"))
    msg_list.append(hitalic(plant.genus))
    if hasattr(plant, 'species'):
        msg_list.append(hitalic(plant.species))
    if hasattr(plant, 'subspecies'):
        msg_list.append('ssp.')
        msg_list.append(hitalic(plant.subspecies))
    if hasattr(plant, 'variety'):
        msg_list.append('var.')
        msg_list.append(hitalic(plant.variety))
    if hasattr(plant, 'cultivated_variety'):
        msg_list.append(f"\ncv. `{plant.cultivated_variety}`")
    msg = text(*msg_list)
    return msg
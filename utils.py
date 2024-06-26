import datetime
import humanize
from pandas.core.series import Series
from aiogram.utils.markdown import hbold, hcode, text, hitalic


def get_age(plant) -> str:
    if hasattr(plant, 'seeding_date'):
        age = datetime.datetime.now() - plant.seeding_date    
        return humanize.precisedelta(age, minimum_unit="months", format='%0.0f') + (' from seeding')
    if hasattr(plant, 'purchase_date'):
        age = datetime.datetime.now() - plant.seeding_date
        return humanize.precisedelta(age, minimum_unit="months", format='%0.0f') + (' from puchase')
    return None


def make_plant_message(plant: Series) -> str:
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
    if hasattr(plant, 'source'):
        msg_list.append(hbold("\nSource: "))
        msg_list.append(f"{ plant.source }")
    age = get_age(plant)
    if age: 
        msg_list.append(hbold("\nAge: "))
        msg_list.append(age)
    msg = text(*msg_list)
    return msg


def plant_to_str(plant: Series) -> str:
    """ Makes formatted string of list of plants """
    
    def quote(text: str) -> str:
        return f"'{ text }'"
    
    PLANT_NAME_MODEL = {
        'uid': {
            'style': hcode,
            'prefix': None,
        },
        'genus': {
            'style': hitalic,
            'prefix': None,
        },
        'species': {
            'style': hitalic,
            'prefix': None,
        },
        'subspecies': {
            'style': hitalic,
            'prefix': 'ssp.',
        },
        'variety': {
            'style': hitalic,
            'prefix': 'var.',
        },
        'cultivated_variety': {
            'style': quote,
            'prefix': 'cv.',
        },
        'synonym': {
            'style': None,
            'prefix': 'syn.',
        },
        'field_number': {
            'style': hbold,
            'prefix': None,
        },
    }
    
    def get_prefix(attr):
        if not PLANT_NAME_MODEL[attr]['prefix']:
            return ''
        return PLANT_NAME_MODEL[attr]['prefix'] + ' '

    def get_styled(plant, attr):
        if not PLANT_NAME_MODEL[attr]['style']:
            return plant[attr] + ' '
        else:
            apply_style = PLANT_NAME_MODEL[attr]['style']
            return apply_style(plant[attr]) + ' '

    result = ''
    for attr in PLANT_NAME_MODEL:
        if hasattr(plant, attr):
            result += get_prefix(attr)
            result += get_styled(plant, attr)
    return result.strip()



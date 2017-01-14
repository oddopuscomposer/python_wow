from models.characters.saved_character import SavedCharacter
from database.main import session


def load_saved_character(name: str):
    """
    This function loads the information about a saved chacacter in the saved_character DB table.

       name,   class,  level,  loaded_scripts_ID,  killed_monsters_ID, completed_quests_ID, inventory_ID, gold
Netherblood, Paladin,     10,                 1,                    1,                   1,            1,   23

    The attributes that end in ID like loaded_scripts_ID are references to other tables.

    For more information:
    https://github.com/Enether/python_wow/wiki/How-saving-a-Character-works-and-information-about-the-saved_character-database-table.
    """
    from classes import Paladin
    loaded_character: SavedCharacter = session.query(SavedCharacter).filter_by(name=name).one_or_none()

    if loaded_character is None:
        raise NoSuchCharacterError(f'There is no saved character by the name of {name}!')

    return loaded_character.convert_to_character_object()
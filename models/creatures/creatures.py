from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from utils.helper import parse_int
from entities import FriendlyNPC, VendorNPC, Monster
from constants import CREATURE_DEFAULT_VALUES
from database.main import Base


class CreaturesSchema(Base):
    # TODO: Remove the Type column from this table
    """
    This table holds information about SPECIFIC monsters in the game
    guid - the unique ID of the specific creature
    creature_id - the ID of the creature in the creature_template table where his general info is stored
    type - the type of creature. Currently supported:
        monster - hostile creature
        fnpc - friendly npc
        vendor - vendor npc
    zone - the zone this specific creature spawns in
    sub_zone - the subzone this specific creature spawns in

     guid, creature_id,       type,             zone,          subzone
           1,          11,  'monster',    Elwynn Forest, Northshire Abbey
    """
    __tablename__ = 'creatures'

    guid = Column(Integer, primary_key=True)
    creature_id = Column(Integer, ForeignKey('creature_template.entry'))
    creature = relationship('CreatureTemplateSchema')
    type = Column(String(60))
    zone = Column(String(60))
    sub_zone = Column(String(60))

    def convert_to_living_thing_object(self) -> VendorNPC or FriendlyNPC or Monster:
        """ Converts the Creature to whatever object he is according to his type column """
        # TODO: move to creature_template.py
        entry: int = self.creature_id
        name: str = self.creature.name
        type_: str = self.creature.type
        level: int = parse_int(self.creature.level)
        health: int = parse_int(self.creature.health)
        mana: int = parse_int(self.creature.mana)
        armor: int = parse_int(self.creature.armor)
        min_dmg: int = parse_int(self.creature.min_dmg)
        max_dmg: int = parse_int(self.creature.max_dmg)
        quest_relation_id: int = parse_int(self.creature.quest_relation_id)
        loot_table: 'LootTable' = self.creature.loot_table
        gossip: str = self.creature.gossip
        respawnable: bool = self.creature.respawnable

        if type_ == "fnpc":
            return FriendlyNPC(name=name, health=health,
                               mana=mana, level=level,
                               min_damage=min_dmg,
                               max_damage=max_dmg,
                               quest_relation_id=quest_relation_id,
                               loot_table=loot_table,
                               gossip=gossip)

        elif type_ == "vendor":
            vendor_inventory = self.creature.build_vendor_inventory()
            return VendorNPC(name=name, entry=entry,
                             health=health, mana=mana, level=level,
                             min_damage=min_dmg,
                             max_damage=max_dmg,
                             quest_relation_id=quest_relation_id,
                             loot_table=loot_table,
                             inventory=vendor_inventory,
                             gossip=gossip)
        elif type_ == "monster":
            gold_to_give_range = (CREATURE_DEFAULT_VALUES[level]['min_gold_reward'],
                                  CREATURE_DEFAULT_VALUES[level]['max_gold_reward'])
            xp_to_give = CREATURE_DEFAULT_VALUES[level]['xp_reward']
            armor = armor if armor else CREATURE_DEFAULT_VALUES[level]['armor']
            return Monster(monster_id=entry,
                           name=name,
                           health=health,
                           mana=mana,
                           armor=armor,
                           level=level,
                           min_damage=min_dmg,
                           max_damage=max_dmg,
                           quest_relation_id=quest_relation_id,
                           loot_table=loot_table,
                           xp_to_give=xp_to_give,
                           gold_to_give_range=gold_to_give_range,
                           gossip=gossip,
                           respawnable=respawnable)
        else:
            raise Exception(f'{type_} is not a valid creature type!')

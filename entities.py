"""
This holds the classes for every entity in the game: Monsters and Characters currently
"""

import random

from items import Weapon, Item
from loader import (load_creature_xp_rewards, load_character_level_stats,
                    load_character_xp_requirements, load_creature_gold_reward,
                    load_loot_table, load_item, load_vendor_inventory)
from quest import Quest
from damage import Damage

# dictionary that holds information about how much XP a monster of a certain level should award the player.
# key: level(int), value: xp reward(int)
CREATURE_XP_REWARD_DICTIONARY = load_creature_xp_rewards()
CREATURE_GOLD_REWARD_DICTIONARY = load_creature_gold_reward()


def lookup_xp_reward(level: int) -> int:
    """ Return the appropriate XP reward associated with the given level"""
    return CREATURE_XP_REWARD_DICTIONARY[level]


def lookup_gold_reward(level: int) -> tuple:
    """ Return a tuple that has the minimum and maximum gold amount a creature of certain level should give"""
    return CREATURE_GOLD_REWARD_DICTIONARY[level]


class LivingThing:
    """
    This is the base class for all things _alive - characters, monsters and etc.
    """

    def __init__(self, name: str, health: int = 1, mana: int = 1):
        self.name = name
        self.health = health
        self.max_health = health
        self.mana = mana
        self.max_mana = mana
        self._alive = True
        self._in_combat = False

    def is_alive(self):
        return self._alive

    def is_in_combat(self):
        return self._in_combat

    def enter_combat(self):
        self._in_combat = True

    def leave_combat(self):
        self._in_combat = False
        self._regenerate()

    def _regenerate(self):
        self.health = self.max_health
        self.mana = self.max_mana

    def check_if_dead(self):
        if self.health <= 0:
            self._die()

    def _die(self):
        self._alive = False

    def revive(self):
        self._regenerate()
        self._alive = True


class FriendlyNPC(LivingThing):
    """
    This is the class for friendly creatures in the world
    """

    def __init__(self, name: str, health: int = 1, mana: int = 1, level: int = 1, min_damage: int = 0,
                 max_damage: int = 1, quest_relation_id = 0, loot_table_ID: int = 0, gossip: str = 'Hello'):
        super().__init__(name, health, mana)
        self.level = level
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.gossip = gossip

    def __str__(self):
        return "{npc_name}".format(npc_name=self.name)

    def talk(self, player_name: str):
        print("{npc_name} says: {msg}".format(npc_name=self.name, msg=self.gossip.replace("$N", player_name)))


class VendorNPC(FriendlyNPC):
    """
    This is the class for the vendor NPCs in the world
    """

    def __init__(self, name: str, entry: int, health: int = 1, mana: int = 1, level: int = 1, min_damage: int = 0,
                 max_damage: int = 1, quest_relation_id = 0, loot_table_ID: int = 0, gossip: str = 'Hello'):
        super().__init__(name, health, mana, level, min_damage, max_damage, quest_relation_id, loot_table_ID, gossip)
        self.entry = entry
        self.inventory = load_vendor_inventory(self.entry)  # type: dict: key-item_name(str), value: tuple(item object, count)

    def __str__(self):
        return "{npc_name} <Vendor>".format(npc_name=self.name)

    def print_inventory(self):
        print("{}'s items for sale:".format(self.name))
        for item, item_count in self.inventory.values():
            print("\t{item_count} {item_name} - {price} gold.".format(item_count=item_count,
                                                                      item_name=item.name,
                                                                      price=item.buy_price))

    def has_item(self, item_name: str) -> bool:
        """
        Checks if the vendor has the item in stock
        :param item_name: The name of the item in a string
        :return: A boolean indicating if we have it or not
        """
        return item_name in self.inventory.keys()

    def get_item_price(self, item_name: str) -> int:
        """Returns the price the vendor sells the item for"""
        item, _ = self.inventory[item_name]
        return item.buy_price

    def sell_item(self, item_name: str) -> tuple:
        """ Returns a tuple(1,2,3)
            1 - the item object type: Item
            2 - the number of items type: int
            3 - the price of the item type: int"""
        item, item_count = self.inventory[item_name]
        item_price = item.buy_price

        del self.inventory[item_name]

        return item, item_count, item_price


class Monster(LivingThing):
    def __init__(self, monster_id: int, name: str, health: int = 1, mana: int = 1, level: int = 1, min_damage: int = 0,
                 max_damage: int = 1, quest_relation_id=0, loot_table_ID: int = 0, gossip = ''):
        super().__init__(name, health, mana)
        self.monster_id = monster_id
        self.level = level
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.xp_to_give = lookup_xp_reward(self.level)
        self.gossip = gossip
        self._gold_to_give = self._calculate_gold_reward(lookup_gold_reward(self.level))
        self.quest_relation_ID = quest_relation_id
        self.loot_table_ID = loot_table_ID
        self.loot = {"gold": self._gold_to_give}  # dict Key: str, Value: Item class object

    def __str__(self):
        return "Creature Level {level} {name} - {hp}/{max_hp} HP | {mana}/{max_mana} Mana | " \
               "{min_dmg}-{max_dmg} Damage".format(level=self.level, name=self.name,
                                                   hp=self.health, max_hp=self.max_health,
                                                   mana=self.mana, max_mana=self.max_mana,
                                                   min_dmg=self.min_damage, max_dmg=self.max_damage)

    def get_auto_attack_damage(self, target_level: int):
        level_difference = self.level - target_level
        percentage_mod = (abs(level_difference) * 0.1)  # calculates by how many % we're going to increase/decrease dmg

        damage_to_deal = random.randint(int(self.min_damage), int(self.max_damage) + 1)
        # 10% more or less damage for each level that differs
        if level_difference == 0:
            pass
        elif level_difference < 0:  # character is bigger level
            damage_to_deal -= damage_to_deal * percentage_mod  # -X%
        elif level_difference > 0:  # monster is bigger level
            damage_to_deal += damage_to_deal * percentage_mod  # +X%

        return Damage(phys_dmg=damage_to_deal)

    def attack(self, victim):  # victim: Character
        monster_swing = self.get_auto_attack_damage(victim.level)  #  type: Damage

        victim.take_attack(self.name, monster_swing, self.level)

    def take_attack(self, damage: Damage):
        self.health -= damage
        self.check_if_dead()

    def _drop_loot(self):
        """
        This method gets the loot the monster can drop, rolls the dice on each drop chance and
        populates the creature's self.loot dictionary that will hold the dropped loot
        """
        # loot_list is a list of tuples containing (item_ID(int), drop_chance(1-100))
        loot_list = load_loot_table(monster_loot_table_ID=self.loot_table_ID)

        for item_ID, item_drop_chance in loot_list:
            '''
            Generate a random float from 0.0 to ~0.9999 with random.random(), then multiply it by 100
            and compare it to the drop_chance. If the drop_chance is bigger, the item has dropped.

            Example: drop chance is 30% and we roll a random float. There's a 70% chance to get a float that's bigger
            than 0.3 and a 30% chance to get a float that's smaller. We roll 0.25, multiply it by 100 = 25 and see
            that the drop chance is bigger, therefore the item should drop.
            '''
            random_float = random.random()

            if item_drop_chance >= (random_float * 100):
                # item has dropped, load it from the DB
                item = load_item(item_ID)

                self.loot[item.name] = item

    def give_loot(self, item_name: str):
        """ Returns the item that's looted and removes it from the monster's inventory"""
        if item_name not in self.loot:  # TODO: This should not be checked here
            # unsuccessful loot
            print("{monster_name} did not drop {item_name}.".format(monster_name=self.name,item_name=item_name))
            return False

        item = self.loot[item_name] # type: Item
        del self.loot[item_name] # remove it from the inventory
        return item

    def _die(self):
        super()._die()
        self._drop_loot()
        print("Creature {} has died!".format(self.name))

    def _calculate_gold_reward(self, min_max_gold: tuple) -> int:
        """ Calculate the gold this monster is going to award the player
            min_max_gold: A tuple containing the minimum and maximum amount of gold a creature of this level can give
            (2,5) meaning this creature should give from 2-5 gold, picked at random"""
        return random.randint(min_max_gold[0], min_max_gold[1])


class Character(LivingThing):
    # keys are used to access the level_stats dictionary that holds information on stats to update on each level up
    KEY_LEVEL_STATS_HEALTH = 'health'
    KEY_LEVEL_STATS_MANA = 'mana'
    KEY_LEVEL_STATS_STRENGTH = 'strength'
    KEY_LEVEL_STATS_ARMOR = 'armor'

    def __init__(self, name: str, health: int = 1, mana: int = 1, strength: int = 1):
        super().__init__(name, health, mana)
        self.strength = strength
        self.min_damage = 0
        self.max_damage = 1
        self.equipped_weapon = Weapon(name="Starter Weapon")
        self.level = 1
        self.experience = 0
        self.xp_req_to_level = 400
        self.armor = 75
        self.current_zone = "Elwynn Forest"
        self.current_subzone = "Northshire Valley"
        # A dictionary of dictionaries. Key: level(int), Value: dictionary holding values for hp,mana,etc
        self._LEVEL_STATS = load_character_level_stats()
        self._REQUIRED_XP_TO_LEVEL = load_character_xp_requirements()
        self.quest_log = {}
        self.inventory = {"gold": 0} # dict Key: str, Value: Item class object

    def equip_item(self, item: Item):
        """
        This method equips an item to the character and handles the appropriate change in inventory following the equip
        (equipped item goes back to the inventory and the item to be equipped is removed from the inventory)
        :param item:
        :return:
        """
        if isinstance(item, Weapon):
            item_in_inventory, count = self.inventory[item.name]

            # remove the item we're equipping from the inventory
            if count == 1:  # remove from the inventory
                del self.inventory[item.name]
            else:  # reduce it's count
                self.inventory[item.name] = item_in_inventory, count-1

            # transfer the equipped weapon to the inventory
            eq_weapon = self.equipped_weapon

            if eq_weapon.name in self.inventory.keys():  # if we have such an item in the inventory, we add one more
                weapon_in_inventory, wep_count = self.inventory[eq_weapon.name]
                self.inventory[eq_weapon.name] = weapon_in_inventory, wep_count + 1
            else:  # we don't have such an item in the inventory, we create one
                self.inventory[eq_weapon.name] = eq_weapon, 1

            self.equip_weapon(item)

    def equip_weapon(self, weapon: Weapon):
        print("{} has equipped Weapon {}".format(self.name, weapon.name))
        self.equipped_weapon = weapon
        self._calculate_damage(self.equipped_weapon)

    def _calculate_damage(self, weapon: Weapon):
        # current formula for damage is: wep_dmg * 0.1 * strength
        self.min_damage = weapon.min_damage + (0.1 * self.strength)
        self.max_damage = weapon.max_damage + (0.1 * self.strength)


    def spell_handler(self, command: str):
        """
        Every class will have different spells, this method will make sure the proper spell is caster
        :param command: the spell name that is to be cast
        :return:
        """
        pass

    def get_auto_attack_damage(self, target_level: int) -> Damage:
        level_difference = self.level - target_level
        percentage_mod = (abs(level_difference) * 0.1)  # calculates by how many % we're going to increase/decrease dmg

        damage_to_deal = random.randint(int(self.min_damage), int(self.max_damage) + 1)
        # 10% more or less damage for each level that differs
        if level_difference == 0:
            pass
        elif level_difference < 0:  # monster is bigger level
            damage_to_deal -= damage_to_deal * percentage_mod  # -X%
        elif level_difference > 0:  # character is bigger level
            damage_to_deal += damage_to_deal * percentage_mod  # +X%

        return Damage(phys_dmg=damage_to_deal)

    def attack(self, victim: Monster):
        pass

    def take_attack(self, monster_name:str, damage: Damage, attacker_level: int):
        damage = self._apply_armor_reduction(damage, attacker_level)

        print("{0} attacks {1} for {2}!".format(monster_name, self.name, damage))
        self.health -= damage
        self.check_if_dead()

    def _apply_armor_reduction(self, damage: Damage, attacker_level: int):
        """
        This method applies the armor reduction to a blow, the formula is as follows:
        Percentage to Reduce = Armor / (Armor + 400 + 85 * Attacker_Level)
        :param damage: the raw damage
        :return: the damage with the applied reduction
        """
        reduction_percentage = self.armor / (self.armor + 400 + 85 * attacker_level)
        damage_to_deduct = damage.phys_dmg * reduction_percentage
        reduced_damage = damage.phys_dmg - damage_to_deduct

        return Damage(phys_dmg=reduced_damage)

    def _die(self):
        super()._die()
        print("Character {} has died!".format(self.name))

    def prompt_revive(self):
        print("Do you want to restart? Y/N")
        if input() in 'Yy':
            self.revive()
            print("Character {} has been revived!".format(self.name))
        else:
            exit()

    def has_enough_gold(self, gold: int) -> bool:
        """
        :return: a boolean indicating if we have that much gold
        """
        return self.inventory['gold'] >= gold

    def buy_item(self, sale: tuple):
        """
        This method is used when we buy an item from a vendor. It subtracts the price of the item from our gold and
        gives us the item in our inventory
        :param sale: A Tuple(1,2,3)
                        1 - the item object type: Item
                        2 - the number of items type: int
                        3 - the price of the item type: int
        """
        item, item_count, item_price = sale

        self.inventory['gold'] -= item_price

        self.award_item(item, item_count)

    def add_quest(self, quest: Quest):
        self.quest_log[quest.ID] = quest

    def _check_if_quest_completed(self, quest: Quest):
        if quest.is_completed:
            self._complete_quest(quest)

    def _complete_quest(self, quest: Quest):
        print("Quest {} is completed! XP awarded: {}!".format(quest.name, quest.xp_reward))
        xp_reward = quest.give_reward()

        del self.quest_log[quest.ID]  # remove from quest log

        self._award_experience(xp_reward)

    def _award_experience(self, xp_reward: int):
        """ Method that awards experience to the player and checks if he levels up"""
        self.experience += xp_reward
        self.check_if_levelup()

    def award_monster_kill(self, monster: Monster):
        monster_level = monster.level
        xp_reward = monster.xp_to_give
        monster_quest_ID = monster.quest_relation_ID

        level_difference = self.level - monster_level
        xp_bonus_reward = 0
        if level_difference >= 5:  # if the character is 5 levels higher, give no XP
            xp_reward = 0
        elif level_difference < 0:  # monster is higher level
            percentage_mod = abs(
                level_difference) * 0.1  # 10% increase of XP for every level the monster has over player
            xp_bonus_reward += int(xp_reward * percentage_mod)  # convert to int

        if xp_bonus_reward:
            print("XP awarded: {0} + bonus {1} for the level difference!".format(xp_reward, xp_bonus_reward))
        else:
            print("XP awarded: {0}!".format(xp_reward))

        self._award_experience(xp_reward + xp_bonus_reward)

        # If this monster is for a quest and we have that quest
        if monster_quest_ID and monster_quest_ID in self.quest_log:
            # TODO: Might want another way to handle this
            quest = self.quest_log[monster_quest_ID]
            quest.update_kills()
            self.quest_log[monster_quest_ID] = quest

            self._check_if_quest_completed(quest)

    def award_gold(self, gold: int):
        self.inventory['gold'] += gold

    def award_item(self, item: Item, item_count=1):
        """ Take an item and put it into the character's inventory,
        store it as a tuple holding (Item Object, Item Count) """
        item_quest_id = item.quest_ID

        if item.name not in self.inventory.keys():  # if we don't have the item
            self.inventory[item.name] = (item, item_count)
        else:
            # if there is such an item, simply update it's count by one
            item, item_count = self.inventory[item.name]
            self.inventory[item.name] = (item, item_count + item_count)

        # if the item is related to a quest and if we have that quest
        if item_quest_id and item_quest_id in self.quest_log:
            temp_quest = self.quest_log[item_quest_id]

            # have the quest check if the player has enough items to complete it
            temp_quest.check_if_complete(self.inventory)

            self.quest_log[item_quest_id] = temp_quest

            self._check_if_quest_completed(temp_quest)

    def check_if_levelup(self):
        if self.experience >= self.xp_req_to_level:
            self._level_up()
            self.experience = 0
            self.xp_req_to_level = self._lookup_next_xp_level_req()

    def _level_up(self):
        self.level += 1

        current_level_stats = self._LEVEL_STATS[self.level]
        # access the dictionary holding the appropriate value increases for each level
        hp_increase_amount = current_level_stats[self.KEY_LEVEL_STATS_HEALTH]
        mana_increase_amount = current_level_stats[self.KEY_LEVEL_STATS_MANA]
        strength_increase_amount = current_level_stats[self.KEY_LEVEL_STATS_STRENGTH]
        armor_increase_amount = current_level_stats[self.KEY_LEVEL_STATS_ARMOR]

        self.max_health += hp_increase_amount
        self.max_mana += mana_increase_amount
        self.strength += strength_increase_amount
        self.armor += armor_increase_amount
        self._regenerate()  # regen to full hp/mana

        print('*' * 20)
        print("Character {0} has leveled up to level {1}!".format(self.name, self.level))
        print("Armor Points increased by {}".format(armor_increase_amount))
        print("Health Points increased by {}".format(hp_increase_amount))
        print("Mana Points increased by {}".format(mana_increase_amount))
        print("Strength Points increased by {}".format(strength_increase_amount))
        print('*' * 20)

    def print_quest_log(self):
        print("Your quest log:")

        for _, quest in self.quest_log.items():
            print("\t{quest_name} - {monsters_killed}/{required_kills} {monster_name} slain.".format(
                quest_name=quest.name,
                monsters_killed=quest.kills,
                required_kills=quest.needed_kills,
                monster_name=quest.monster_to_kill))

        print()

    def print_inventory(self):
        print("Your inventory:")

        # print the gold separately so it always comes up on top
        print("\t{} gold".format(self.inventory['gold']))
        for key, item_tuple in self.inventory.items():
            if key is not "gold":
                item, item_count = item_tuple
                print("\t{item_count} {item}".format(item_count=item_count, item=item))

    def _lookup_next_xp_level_req(self):
        return self._REQUIRED_XP_TO_LEVEL[self.level]

    def get_class(self) -> str:
        """Returns the class of the character as a string"""
        pass

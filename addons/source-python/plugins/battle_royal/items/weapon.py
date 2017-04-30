## IMPORTS

from entities.entity import Entity
from weapons.entity import Weapon
from entities.helpers import index_from_pointer
from listeners.tick import Delay
from messages import SayText2

from .item import Item
from ..globals import _authorize_weapon


class WeaponItem(Item):
    item_type = 'weapon'
    slot = ''

    def create(self, location):
        weapon_name = 'weapon_' + self.__class__.__name__.lower()
        entity = Weapon.create(weapon_name)
        entity.origin = location
        entity.spawn()
        entity.ammo = 0
        # entity.clip = 0
        return entity

    def equip(self, player):
        weapon = player.get_weapon(is_filters=self.slot)
        if weapon is None:
            self.use(player)

    def on_item_given(player, item):
        SayText2('Player {player} has got {item} !'.format(player=player.name, item=item.classname)).send()

    def use(self, player, callback=on_item_given):
        def delay_callback():
            weapon_name = 'weapon_' + self.__class__.__name__.lower()
            weapon_pointer = player.give_named_item(weapon_name, 0, None, True)
            weapon = Entity(index_from_pointer(weapon_pointer))
            _authorize_weapon.append(index_from_pointer(weapon_pointer))
            callback(player, weapon)
     
        player.delay(0, delay_callback)
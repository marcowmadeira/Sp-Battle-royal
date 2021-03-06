## IMPORTS

import random


from cvars import ConVar

from engines.server import global_vars
from entities.entity import BaseEntity, Entity

from filters.entities import BaseEntityIter, EntityIter
from filters.players import PlayerIter

from listeners.tick import Delay

from mathlib import Vector

from messages import SayText2

from players.entity import Player
from players.constants import LifeState


import battle_royal.entity.parachute

from .player import BattleRoyalPlayer

from .gas import Gas

from .. import globals
from ..config import _configs

from ..items.item import Item, items

from ..utils.spawn_manager import SpawnManager
from ..utils.spawn_player import SpawnPlayer, SpawnType

## ALL DECLARATIONS

__all__ = (
    'BattleRoyal',
    '_battle_royal'
)


class BattleRoyal:
    '''
        This class manage a BattleRoyal round.
    '''

    def __init__(self):
        self.is_warmup = False
        self.match_begin = False
        self._players = dict()
        self._dead_players = dict()
        self._teams = dict()

    @property
    def teams(self):
        'Get all distrinct players group.'
        return self._teams

    def add_team(self, team):
        'Add team.'
        self._teams[team.name] = team

    def remove_team(self, team):
        'Remove team.'
        del self._teams[team.name] 

    @property
    def players(self):
        'Returns dict with alive players.'
        return self._players   

    def get_player(self, player):
        'Get a player by userid or Player object.'
        if isinstance(player, Player):
            return self._players[player.userid] if player.userid in self._players else None
        else:
            return self._players[player] if player in self._players else None

    def add_player(self, player):
        'Add player.'
        self._players[player.userid] = player

    def remove_player(self, player):
        'Remove player.'
        del self._players[player.userid]

    @property
    def deads(self):
        'Returns all dead players.'
        return self._dead_players   

    def get_dead_player(self, player):
        'Get dead players by userid or Player object.'
        if isinstance(player, Player):
            return self._dead_players[player.userid] if player.userid in self._dead_players else None
        else:
            return self._dead_players[player] if player in self._dead_players else None

    def add_dead_player(self, player):
        'Add player to deads.'
        self._dead_players[player.userid] = player

    def remove_dead_player(self, player):
        'Remove player to deads.'
        del self._dead_players[player.userid]

    def _god_mode_noblock(self, enable):
        'Set god mode and noblock to all players.'
        for br_player in self._players.values():
            br_player.godmode = enable
            br_player.noblock = enable

    def spawn_item(self):
        'Spawn all items on current map.'
        # Number of items depend on player and rarity of item add this attribute to item
        globals.items_spawn_manager = SpawnManager('item', global_vars.map_name)
        locations = globals.items_spawn_manager.locations
        if len(locations) != 0:
            for classname, cls in Item.get_subclass_dict().items():
                if len(locations) == 0:
                    break
                if classname in ['Weapon', 'Ammo', 'Armor', 'Care']:
                    continue

                vector = random.choice(locations)
                item = cls.create(vector)
                locations.remove(vector)
        else:
            SayText2('Any spawn point on this map.').send()
    
    def spawn_players(self, **kwargs):
        'Spawn all players on the map.'
        if ConVar('mp_randomspawn').get_int() == 0:
            ConVar('mp_randomspawn').set_int(1)
            ConVar('mp_restartgame').set_int(1)

        globals.players_spawn_manager = SpawnManager('player', global_vars.map_name)
        all_locations = globals.players_spawn_manager.locations

        # Maybe add check nb_player > len(loca) choose deathmatch spawn
        if len(all_locations) == 0 or len(all_locations) < len(self._players):
            all_locations = [
                entity.get_key_value_vector('origin')
                for entity in BaseEntityIter('info_deathmatch_spawn')
            ]

        if len(kwargs) == 1 and 'spawn_type' in kwargs:
            spawn_type = kwargs['spawn_type']
        else:
            spawn_type = _configs['spawn_player_type'].get_int()

        spawn_player = SpawnPlayer(self._players, all_locations, spawn_type)
        spawn_player.spawn()

    def spread_gas(self):
        'Begin gas spreading.'
        # Get random radius and gas the rest (Wave of gas depend on map maybe, 3 mini)
        # Maybe create a listener to start another gas spreading after the end of the following
        start = _configs['time_before_spreading'].get_int()
        waiting = _configs['time_between_spreading'].get_int()

        wave_one = Gas()
        wave_one.spread(start)

    def warmup(self):
        'Run the warmup.'
        self.is_warmup = True
        self.spawn_players(spawn_type=0)
        self._god_mode_noblock(True)

    def start(self):
        'Start a battle royal game.'
        SayText2('Match start !').send()
        self.is_warmup = False
        self.match_begin = True
        self._god_mode_noblock(False)

        if bool(_configs['parachute_enable'].get_int()):
            globals.parachute.enable = True
            Delay(_configs['parachute_duration'].get_int(), globals.parachute.disable)
        else:
            globals.parachute.enable = False

        self.spawn_item()
        self.spawn_players()

        # Add repeater to spread gas
        # self.spread_gas()

    def end(self):
        'Stop a battle royal game.'
        self.match_begin = False
        self.is_warmup = False
        globals.parachute.enable = False

        # Remove all spawned entities
        Delay(1, items.clear)

        # Recreate player list
        dead_players = self._dead_players.copy()
        self._players.update(dead_players) 
        self._dead_players.clear()

        
## GLOBALS

_battle_royal = BattleRoyal()

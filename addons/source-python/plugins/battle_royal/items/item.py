from entities.entity import Entity
from entities.helpers import index_from_pointer
from engines.precache import Model
from messages import SayText2

## ALL DECLARATIONS

__all__ = (
    'Item',
)

class Item:
    name = ''
    item_type = ''
    description = ''
    models = None
    amount = 1
    weight = 0
    models = 'models/props/coop_cementplant/coop_ammo_stash/coop_ammo_stash_empty.mdl'

    def create(self, location):
        entity = Entity.create('prop_physics_override')
        entity.origin = location
        if self.models is not None:
            entity.model = Model(self.models)
        entity.spawn_flags = 256
        # entity.solid_type = 6
        # entity.collision_group = 1
        entity.spawn()
        return entity

    def use(self):
        SayText2('Can\'t use').send()
        return False

    def destroy(self):
        SayText2('Can\'t destroy').send()
        return False

    @classmethod
    def get_subclasses(cls):
        for subcls in cls.__subclasses__():
            yield subcls
            yield from subcls.get_subclasses()

    @classmethod
    def get_subclass_dict(cls):
        return { subcls.__name__: subcls for subcls in cls.get_subclasses() }

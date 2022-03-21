import struct

from ori.save.generic_save import GenericSave


UUID_ROOT_SCENE = '00000000-0000-0000-0000-000000000000'
UUID_DEATH_COUNTER = '499a49ac-3153-48b6-bc8c-c8e24f87ddef'
UUID_ABILITIES = '465d2e6b-7974-4b41-b30b-0fbd8d6d6ae0'
UUID_WORLD_EVENTS = '1864e352-d258-4744-b0f1-05282134f823'


ABILITIES_IDS = {
    0: 'Bash',
    1: 'Charge Flame',
    2: 'Wall Jump',
    3: 'Stomp',
    4: 'Double Jump',
    5: 'Charge Jump',
    8: 'Climb',
    9: 'Glide',
    10: 'Spirit Flame',
    37: 'Dash',
    38: 'Grenade'
}


WORLD_EVENTS_IDS = {
    0: 'Gumon Seal',
    1: 'Water Vein',
    2: 'Sunstone',
    5: 'Water Cleaned',
    6: 'Wind Restored',
    10: 'Warmth Returned'
}

class OriSave(  ):
    def get_death_counter(self):
        data = self.object(UUID_ROOT_SCENE, UUID_DEATH_COUNTER)
        return struct.unpack('<i', data)[0]

    def get_abilities(self):
        data = self.object(UUID_ROOT_SCENE, UUID_ABILITIES)
        data = struct.unpack('<43?', data)
        return { name: data[i] for i, name in ABILITIES_IDS.items() }

    def get_world_events(self):
        data = self.object(UUID_ROOT_SCENE, UUID_WORLD_EVENTS)
        data = struct.unpack('<12?', data)
        return { name: data[i] for i, name in WORLD_EVENTS_IDS.items() }

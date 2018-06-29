import struct
import sys
import os
from uuid import UUID as UUID


def DevilUUID(text):
    devil_data = bytearray.fromhex(text)
    mem_data = struct.unpack('>QQ', devil_data)
    raw_data = struct.pack('<QQ', *mem_data)
    
    return UUID(bytes_le=raw_data)

class Buffer:
    def __init__(self, data):
        self.buffer = data
        self.i = 0

    def pop(self, format):
        format = '<'+format
        ret = struct.unpack_from(format, self.buffer, self.i)
        self.i += struct.calcsize(format)
        return ret

    def pop_uuid(self):
        value, = self.pop('16s')
        return UUID(bytes_le=value)

    def pop_string(self, length_type='B'):
        length, = self.pop(length_type)
        return self.pop('{}s'.format(length))[0]

    def pop_bool(self): return self.pop('?')[0]
    def pop_int(self): return self.pop('I')[0]
    def pop_time(self): return self.pop('III')

SAVE_FORMAT = """
string  area_name
int     completion
int     health
int     max_health
int     energy
int     max_energy
time    time
int     progression
bool    is_completed
uuid    uuid
bool    is_debug_on
int     order
int     difficulty
bool    was_killed
bool    completed_with_everything
int     lowest_difficulty
bool    is_trial_save
"""

SCENES = open('scenes.txt').read()

SAVE_FORMAT = [ row.split() for row in SAVE_FORMAT.split('\n') if row.strip() ]
SCENES = { DevilUUID(uuid): name for uuid, name in [row.split() for row in SCENES.split('\n') if row.strip() ] }

class Save:
    def __init__(self, path):
        b = Buffer(open(path, 'rb').read())

        file_header = b.pop_string()
        assert file_header == b'OriSave'
        file_version = b.pop_int()
        assert file_version == 13

        for data_type, data_name in SAVE_FORMAT:
            pop_func = getattr(b, 'pop_{}'.format(data_type))
            setattr(self, data_name, pop_func())

        file_format_string = b.pop_string()
        assert file_format_string == b'SaveGameData'
        data_version, = b.pop('i')
        assert data_version == 1

        def read_scenes(b):
            count, = b.pop('i')
            for _ in range(count):
                uuid = b.pop_uuid()
                data = b.pop_string('I')
                #name = SCENES.get(uuid)
                #if name is not None:
                #    print('    ', uuid, name, len(data))

                yield uuid, data

        def read_scene_collections(b):
            count, = b.pop('i')
            for _ in range(count):
                uuid = b.pop_uuid()
                
                #name = SCENES.get(uuid)

                #print(uuid)

                #if name is not None:
                #    print(uuid, name)
                scene = dict(read_scenes(b))

                yield uuid, scene

        self.scenes = dict(read_scene_collections(b))

    def object(self, scene_id, object_id):
        return self.scenes.get(UUID(scene_id), {}).get(UUID(object_id))

    def print(self):
        for _, data_name in SAVE_FORMAT:
            print(data_name, getattr(self, data_name))

        print()

class OriSave(Save):
    def get_death_counter(self):
        data = self.object('00000000-0000-0000-0000-000000000000', '499a49ac-3153-48b6-bc8c-c8e24f87ddef')
        return struct.unpack('<i', data)[0]

    def get_abilities(self):
        data = self.object('00000000-0000-0000-0000-000000000000', '465d2e6b-7974-4b41-b30b-0fbd8d6d6ae0')
        data = struct.unpack('<43?', data)
        return {
            'Bash': data[0],
            'Charge Flame': data[1],
            'Wall Jump': data[2],
            'Stomp': data[3],
            'Double Jump': data[4],
            'Charge Jump': data[5],
            'Climb': data[8],
            'Glide': data[9],
            'Spirit Flame': data[10],
            'Dash': data[37],
            'Grenade': data[38]
        }

    def get_world_events(self):
        data = self.object('00000000-0000-0000-0000-000000000000', '1864e352-d258-4744-b0f1-05282134f823')
        data = struct.unpack('<12?', data)
        return {
            'Gumon Seal': data[0],
            'Water Vein': data[1],
            'Sunstone': data[2],
            'Water Cleaned': data[5],
            'Wind Restored': data[6],
            'Warmth Returned': data[10]
        } 

if __name__ == '__main__':
    def get_uuid_name(uuid):
        name = SCENES.get(uuid, None)
        if name is None: return uuid

        return '{} ({})'.format(name, uuid)

    FLOAT_ONLY = """
        199d7188-7748-42b8-8189-e1126676c2d9
        2dec26a0-641f-4cda-81db-29b2992296d3
        """

    INT_ONLY = """
        499a49ac-3153-48b6-bc8c-c8e24f87ddef # death counter
    """

    def TryUUID(text):
        try:
            return UUID(text)
        except:
            return None

    def text(key, value):
        if key in map(TryUUID, FLOAT_ONLY.split()):
            n = len(value)//4
            return struct.unpack('<{}f'.format(n), value)

        if key in map(TryUUID, INT_ONLY.split()):
            n = len(value)//4
            return struct.unpack('<{}i'.format(n), value)

        return '<Data: length={}>'.format(len(value)) + '  ' + ('' if len(value) > 50 else value.hex())

    save1 = OriSave(sys.argv[1])
    save1.print()

    if len(sys.argv[2:]) == 0:
        def get_text(scene_id, object_id):
            key = UUID(object_id)
            value = save1.object(scene_id, object_id)

            if value is None:
                return None
            return text(key, value)

        print(get_text('00000000-0000-0000-0000-000000000000', '199d7188-7748-42b8-8189-e1126676c2d9'))
        print(get_text('00000000-0000-0000-0000-000000000000', '2dec26a0-641f-4cda-81db-29b2992296d3'))
        sys.exit(0)

    save2 = OriSave(sys.argv[2])
    save2.print()

    scenes = save1.scenes.keys() | save2.scenes.keys()

    for scene_id in scenes:
        data1 = save1.scenes.get(scene_id, {})
        data2 = save2.scenes.get(scene_id, {})

        data = data1.keys() | data2.keys()

        printed_header = False
        def print_header():
            global printed_header
            if not printed_header:
                print(scene_id)
                printed_header = True

        for key in data:
            value1 = data1.get(key)
            value2 = data2.get(key)

            if value1 == value2:
                continue

            print_header()

            key_name = get_uuid_name(key)

            if value1 is None: 
                print(' ', key_name, 'added')
                print('    2:', text(key, value2))
            elif value2 is None: 
                print(' ', key_name, 'removed')
                print('    1:', text(key, value1))
            else: 
                print(' ', key_name, 'changed')
                print('    1:', text(key, value1))
                print('    2:', text(key, value2))

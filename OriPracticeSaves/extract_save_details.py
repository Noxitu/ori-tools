import parsesave
import os
import sys
import json
from pprint import pprint

DIRECTORY = sys.argv[1]
saves = os.listdir(DIRECTORY)

data = {}

def get_name(filename):
    name = filename[:-4]
    if name.startswith('save - '):
        name = name[7:]
    name = name.replace('..', ':')
    return name

def time2str(ts):
    ret = '{:02d}:{:02d}'.format(ts[1], ts[2])
    if ts[0] > 0:
        ret = '{:02d}:'.format(ts[0]) + ret
    return ret

for save_name in saves:

    if not save_name.endswith('.sav'):
        continue

    name = get_name(save_name)
    print(name)
    try:
        save = parsesave.OriSave(os.path.join(DIRECTORY, save_name))
    except:
        print('failed')
        continue
    #pprint((get_name(save_name), save.uuid, save.health, save.max_health, save.energy, save.max_energy, save.time, save.get_death_counter()))

    skills = save.get_abilities()
    events = save.get_world_events()

    new_data = {
        'hp': {
            'current': save.health,
            'max': save.max_health
        },
        'energy': {
            'current': save.energy,
            'max': save.max_energy
        },
        'time': time2str(save.time),    
        'event_mask': [ int(events[name]) for name in "Water Vein, Water Cleaned, Gumon Seal, Wind Restored, Sunstone, Warmth Returned".split(', ') ],
        'skill_mask': [ int(skills[name]) for name in "Spirit Flame, Wall Jump, Charge Flame, Double Jump, Bash, Stomp, Glide, Climb, Charge Jump, Grenade, Dash".split(', ') ],
        'area': save.area_name.decode('utf-8')
    }

    if save.get_death_counter() > 0:
        new_data['deaths'] = save.get_death_counter()

    data[name] = new_data

    #print('Failed: ', save_name)
with open(os.path.join(DIRECTORY, 'info.txt'), 'w') as f:
    json.dump(data, f)
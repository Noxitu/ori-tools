import parsesave
import os
import shutil

saves = os.listdir('saves/0xp-orig')

def to_time(ts):
    return '{:02d}..{:02d}..{:02d}.{:d}'.format(*map(int, [ts//3600, ts%3600//60, ts%60//1, ts%1*10]))
for save_name in saves:
    try:
        path = 'saves/0xp-orig/' + save_name
        save = parsesave.Save(path)
        ts = ([0] + list(map(float, save_name[:-4].split('-colon-'))))[-3:]
        ts = ts[0]*3600 + ts[1]*60 + ts[2]
        ts = ts - 4*60 + 7 + .3
        
        target = 'saves/0xp/'+to_time(ts)+'.sav'
        print(path, target)
        shutil.copy(path, target)
    except:
        pass
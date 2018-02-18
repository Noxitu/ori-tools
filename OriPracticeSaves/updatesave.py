import os
import shutil
import stat

ORI_DATADIR_NAME = 'Ori and the Blind Forest DE'
ORI_SAVE_NAME = 'saveFile{id:d}.sav'

def ori_get_save_path(id=0):
    return os.path.join(os.getenv('LOCALAPPDATA'), ORI_DATADIR_NAME, ORI_SAVE_NAME.format(id=id))

def ori_replace_save(id, source_path):
    target_path = ori_get_save_path(id)
    os.chmod(target_path, stat.S_IREAD | stat.S_IWRITE)
    shutil.copy(source_path, target_path)
    os.chmod(target_path, stat.S_IREAD)

if __name__ == '__main__':
    source_path = R'D:\Sources\ori-tools\OriPracticeSaves\saveMisty.sav'
    #ori_replace_save(1, source_path)
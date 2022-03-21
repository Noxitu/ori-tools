import os
import pathlib
import re
import shutil
import tkinter as tk
from turtle import update

ROOT = pathlib.Path(__file__).parent
ICON_PATH = ROOT / 'Icons'
DLL_LIBRARY_PATH = ROOT / 'DLLs'
ORI_DLL_PATH = R'C:\Program Files (x86)\Steam\steamapps\common\Ori DE\oriDE_Data\Managed\Assembly-CSharp.dll'

LABEL_TEXT = 'Current DLL: {name}'


def main():
    library = {}

    app = tk.Tk()
    app.title('Ori DLL Swapper')
    
    ori_icon = tk.PhotoImage(file=ICON_PATH / 'Ori.png')  
    app.iconphoto(False, ori_icon)

    label = tk.Label(app, text=LABEL_TEXT, width=30)
    label.grid(row=0, column=0, padx=20, pady=20)

    def create_command(name):
        def command():
            shutil.copy2(library[name]['path'], ORI_DLL_PATH)
            update_label()
        return command

    def update_label():
        current_size = os.stat(ORI_DLL_PATH).st_size
        current_name, = [name for name, dll in library.items() if dll['size'] == current_size]
        label.config(text=LABEL_TEXT.format(name=current_name))

    for i, file in enumerate(DLL_LIBRARY_PATH.iterdir()):
        name = re.match('Assembly-CSharp-(.+).dll', file.name).group(1)
        button = tk.Button(app, text=name, command=create_command(name), width=30)
        button.grid(row=i + 1, column=0, padx=20, pady=10)

        library[name] = dict(
            name=name,
            path=file,
            size=os.stat(file).st_size,
        )
    
    update_label()
    tk.mainloop()


if __name__ == '__main__':
    main()

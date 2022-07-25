import os
from tkinter import *
import time
from os import walk
import pandas as pd
from csv import DictReader


def get_today_filepaths():
    file_paths = []
    for root, dirs, filenames in walk(os.path.join(os.getcwd(), 'data')):
        if len(dirs) == 0:
            mouse = root[-5:]
            for f in filenames:
                if f[5:15] == time.strftime("%Y-%m-%d"):
                    file_paths.append(os.path.join(mouse, f))
    return file_paths


def gen_data(file_paths):
    d = {}
    for f in file_paths:
        path = os.path.join(os.getcwd(), 'data', f)
        data = pd.read_csv(path, na_values=['None'], skiprows=3)
        num_reward = len(data[(data.key == 'reward') & (data.value == 1)])
        mouse = f[:5]
        if mouse in d.keys():
            d[mouse].append(num_reward)
        else:
            d[mouse] = [num_reward]
    return d


class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.label = Label(text="", fg="Black", font=("Helvetica", 18))
        self.label.place(x=40, y=50)
        self.update()

    def update(self):
        data = gen_data(get_today_filepaths())
        txt = '\n'.join([f'{key}: {", ".join(str(d) for d in data[key])}' for key in data])
        self.label.configure(text=txt)
        self.after(10000, self.update)


def run_gui():
    root = Tk()
    app = App(root)
    root.wm_title("Tracker")
    root.geometry("300x400")
    root.after(10000, app.update)
    root.mainloop()


if __name__ == '__main__':
    run_gui()

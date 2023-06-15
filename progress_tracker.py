import os
from tkinter import *
import time
from os import walk
import pandas as pd
from csv import DictReader, reader
import numpy as np
from datetime import date


def get_today_filepaths(days_back=0):
    file_paths = []
    for root, dirs, filenames in walk(os.path.join(os.getcwd(), 'data')):
        if len(dirs) == 0 and os.path.basename(root)[:2] == 'ES':
            mouse = os.path.basename(root)
            for f in filenames:
                if f == 'desktop.ini':
                    continue
                file_date = date(int(f[5:9]), int(f[10:12]), int(f[13:15]))
                dif = date.today() - file_date
                if dif.days <= days_back:
                    # if f[5:15] == time.strftime("%Y-%m-%d"):
                    file_paths.append(os.path.join(mouse, f))
    return file_paths


def gen_data(file_paths):
    d = {}
    for f in file_paths:
        if f[:5] == 'mouse':
            print('stop')
        path = os.path.join(os.getcwd(), 'data', f)
        data = pd.read_csv(path, na_values=['None'], skiprows=3)
        with open(path, 'r') as file:
            r = reader(file)
            info_keys = next(r)
            info_values = next(r)
        starts = np.where([True if s[0] == '{' else False for s in info_values])[0][::-1]
        ends = np.where([True if s[-1] == '}' else False for s in info_values])[0][::-1]
        for i in range(len(starts)):
            info_values = info_values[:starts[i]] + [",".join(info_values[starts[i]:ends[i] + 1])] + info_values[
                                                                                                     ends[i] + 1:]
        info = dict(zip(info_keys, info_values))
        num_reward = len(data[(data.key == 'reward') & (data.value == 1)])
        mouse = os.path.dirname(f)
        reward_string = f'{num_reward}({info["box"][-1]})'

        if mouse in d.keys():
            d[mouse].append(reward_string)
        else:
            d[mouse] = [reward_string]
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

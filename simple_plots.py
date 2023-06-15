from progress_tracker import get_today_filepaths, gen_data
from datetime import date
import os
from tkinter import *
import time
from os import walk
import pandas as pd
from csv import DictReader, reader
import numpy as np


def gen_data(file_paths):
    d = {}
    for f in file_paths:
        path = os.path.join(os.getcwd(), 'data', f)
        data = pd.read_csv(path, na_values=['None'], skiprows=3)
        mouse = os.path.dirname(f)

        if mouse in d.keys():
            d[mouse].append(data)
        else:
            d[mouse] = [data]
    return d


def simple_plots():
    data = gen_data(get_today_filepaths(1))


if __name__ == '__main__':
    simple_plots()

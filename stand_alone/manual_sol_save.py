import pickle
import RPi.GPIO as GPIO
from support_classes import *
from timescapes import *
from time import sleep


def save_change():
    with open('durations.pkl', 'wb') as f:
        durations = {
            1: 0.017,
            2: 0.01
        }
        pickle.dump(durations, f)


def test_sol(repeats=100, interval=.1):
    with open('durations.pkl', 'rb') as f:
        durations = pickle.load(f)
    GPIO.setmode(GPIO.BCM)
    ports = []
    exp_dist = {'distribution': exp_decreasing,
                'cumulative': 5,
                'staring_probability': 1}
    background_dist = {'distribution': 'background',
                       'rates': [.4, .8, .4, .8, .4, .8],
                       'duration': 5}
    port_dict = {
        # 'exp': Port(1, dist_info=exp_dist, duration=durations[1]),
        'background': Port(2, dist_info=background_dist, duration=durations[2])
    }
    ports = port_dict.values()
    try:
        for _ in range(repeats):
            for port in ports:
                port.sol_on()
                sleep(port.base_duration)
                port.sol_off()
                sleep(interval)
    finally:
        for port in ports:
            port.sol_off()


if __name__ == '__main__':
    save_change()
    test_sol()

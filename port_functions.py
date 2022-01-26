from support_classes import *
from time import sleep
from timescapes import *
import RPi.GPIO as GPIO
import random


def rate_set():
    rates = [
        [1, .8, .6, .4],
        [1, .8, .4, .6],
        [1, .6, .8, .4],
        [1, .6, .4, .8],
        [1, .4, .8, .6],
        [1, .4, .6, .8],

        [.8, 1, .6, .4],
        [.8, 1, .4, .6],
        [.8, .6, 1, .4],
        [.8, .6, .4, 1],
        [.8, .4, 1, .6],
        [.8, .4, .6, 1],

        [.6, 1, .8, .4],
        [.6, 1, .4, .8],
        [.6, .8, 1, .4],
        [.6, .8, .4, 1],
        [.6, .4, 1, .8],
        [.6, .4, .8, 1],

        [.4, 1, .8, .6],
        [.4, 1, .6, .8],
        [.4, .8, 1, .6],
        [.4, .8, .6, 1],
        [.4, .6, 1, .8],
        [.4, .6, .8, 1],
    ]
    shuffled_rates = [
        [.8, .6, .4, 1],  # ES015
        [1, .8, .6, .4],
        [.6, .4, 1, .8],
        [.4, 1, .8, .6],

        [.4, 1, .6, .8],  # ES016
        [.8, .6, 1, .4],
        [1, .8, .4, .6],
        [.6, .4, .8, 1],

        [1, .6, .8, .4],  # ES017
        [.6, 1, .4, .8],
        [.8, .4, .6, 1],
        [.4, .8, 1, .6],

        [.6, 1, .8, .4],  # ES019
        [.4, .8, .6, 1],
        [.8, .4, 1, .6],
        [1, .6, .4, .8],

        [1, .4, .8, .6],  # ES020
        [.6, .8, .4, 1],
        [.4, .6, 1, .8],
        [.8, 1, .6, .4],

        [.8, 1, .4, .6],
        [.4, .6, .8, 1],
        [.6, .8, 1, .4],
        [1, .4, .6, .8],

    ]


def test_led(ports, repeats=5):
    for port in ports:
        for _ in range(repeats):
            port.led_on()
            sleep(.2)
            port.led_off()
            sleep(.2)


def test_ir(ports, duration=10000):
    for _ in range(duration):
        for port in ports:
            head_change = port.head_status_change()
            lick_change = port.lick_status_change()
            if head_change == 1:
                print('head start')
            if head_change == -1:
                print('head end')
            if lick_change == 1:
                print('lick start')
            if lick_change == -1:
                print('lick end')
        sleep(.2)


def test(ports, functions):
    if 'ir' in functions:
        test_ir(ports)
    if 'led' in functions:
        test_led(ports)
    if 'sol' in functions:
        test_sol(ports)


def empty_sol(ports, repeats=10000, interval=.1):  # Don't use with 24V solenoids, they'll overheat
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


def test_sol(ports, repeats=100, interval=.1, one_at_a_time=False):
    if one_at_a_time:
        for port in ports:
            for _ in range(repeats):
                port.sol_on()
                sleep(port.base_duration)
                port.sol_off()
                sleep(interval)
    else:
        for _ in range(repeats):
            for port in ports:
                port.sol_on()
                sleep(port.base_duration)
                port.sol_off()
                sleep(interval)


def main():
    GPIO.setmode(GPIO.BCM)
    ports = []
    exp_dist = {'distribution': exp_decreasing,
                'cumulative': 5,
                'staring_probability': 1}
    background_dist = {'distribution': 'background',
                       'rates': random.shuffle([1, .8, .6, .4, .2]),
                       'duration': 10}
    # dists = [exp_dist, background_dist]
    # ports.append(Port(1, dist_info=dists[0]))
    # ports.append(Port(2, dist_info=dists[1]))
    port_dict = {
        'exp': Port(1, dist_info=exp_dist),
        # 'background': Port(2, dist_info=background_dist)
    }
    ports = port_dict.values()

    try:
        # test(ports, ['ir'])
        # test(ports, ['ir', 'led', 'sol'])
        # test(ports, ['led'])
        test(ports, ['sol'])
        # empty_sol(ports)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()

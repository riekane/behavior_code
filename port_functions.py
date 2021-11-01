from support_classes import *
from time import sleep
from timescapes import *
import RPi.GPIO as GPIO
import random


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


def empty_sol(ports):  # Don't use with 24V solenoids, they'll overheat
    try:
        for port in ports:
            port.sol_on()
        sleep(3000)
    finally:
        for port in ports:
            port.sol_off()


def test_sol(ports, repeats=1000, interval=.1, one_at_a_time=False):
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
    exp_dict = {'distribution': exp_decreasing,
                'cumulative': 5,
                'staring_probability': 1}
    background_dict = {'distribution': 'background',
                       'rates': random.shuffle([1, .8, .6, .4, .2]),
                       'duration': 10}
    dists = [exp_dict, background_dict]
    # dists = [background_dict, exp_dict]
    ports.append(Port(1, dist_info=dists[0]))
    ports.append(Port(2, dist_info=dists[1]))

    try:
        # test(ports, ['ir'])
        # test(ports, ['ir', 'led', 'sol'])
        test(ports, ['led'])
        # test(ports, ['sol'])
        # empty_sol(ports)  # Dont use with 24V solenoids
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()

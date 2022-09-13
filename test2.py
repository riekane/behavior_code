import time
import RPi.GPIO as GPIO
from time import sleep


# tests one of the sensors
def test_ir():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN)
    print(f'Port status: {GPIO.input(4)}')
    start_time = time.time()
    while time.time() - start_time < 100:
        sleep(0.5)
        print(f'Port status: {GPIO.input(4)}')


if __name__ == '__main__':
    test_ir()

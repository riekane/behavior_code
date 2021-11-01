import numpy as np


# This is the new one. It's a decreasing exponential multiplied by a straight line.
def lin_over_ex(x, cumulative=10, x_peak=1):
    b = 1 / x_peak
    a = b ** 2 * cumulative
    density = (a * x) / np.exp(b * x)
    return density


# This is the simple exponential decreasing
def exp_decreasing(x, cumulative=10, starting=1):
    a = starting
    b = a / cumulative
    density = a / np.exp(b * x)
    return density


def fixed_single(x, wait_time):
    if x > wait_time:
        reward = 1
    else:
        reward = 0
    return reward

import numpy as np

def exp_decreasing(x, cumulative=10, starting=1):
    a = starting
    b = a / cumulative
    density = a / np.exp(b * x)
    return density
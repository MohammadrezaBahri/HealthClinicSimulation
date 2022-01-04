import random
from math import log
from src.state import random_seed

random.seed(random_seed) # initial seed

def rand():
    r = random.random()
    random.seed(r)
    return r

def uniform(a, b):
    return a + (b-a)*rand()

def expopnential(e):
    return (-1/e)*log(1-rand())

def triangular(low, mode, high):
    r = rand()
    c = (mode - low) / (high - low)
    if r > c:
        r = 1.0 - r
        c = 1.0 - c
        low, high = high, low
    return low + (high - low) * ((r * c) ** 0.5)

def beta(a,b):
    rand()
    return random.betavariate(a,b)
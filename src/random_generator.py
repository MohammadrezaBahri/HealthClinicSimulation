import random
from math import log

random.seed(4) # initial seed

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
    x1 = rand()**(1/a)
    x2 = rand()**(1/b)

    while (x1+x2) > 1:
        x1 = rand()**(1/a)
        x2 = rand()**(1/b)

    #return (1 + (rand()/3)**(0.5))
    return x1 / (x1 + x2)

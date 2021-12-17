from itertools import count
from src.random_generator import rand

class Patient:

    _i = count(1)

    def __init__(self, arrival_Time: int) -> None:
        self.i = next(self._i) # first patient entering the clinic gets i=1 and for second one i=2 and so on
        self.arrival_Time = arrival_Time # in minutes
        self.priority = 1 if rand() < 0.6 else 3 # 1 or 3
        self.served = 0 # 0, 1 or 2

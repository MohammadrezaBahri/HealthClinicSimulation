from itertools import count
from src.random_generator import rand

class Patient:

    _i = count(1)

    def __init__(self, arrival_Time: int) -> None:
        self.i = next(self._i) # first patient entering the clinic gets i=1 and for second one i=2 and so on
        self.arrival_Time = arrival_Time # in minutes
        self.priority = 1 if rand() < 0.6 else 3 # 1 or 3 and will change to 12 or 32 after served once
        self.served = 0 # 0, 1 or 2
        self.first_service_start_time = None
        self.first_service_end_time = None
        self.second_service_start_time = None
        self.second_service_end_time = None


    def __str__(self) -> str:
        return f"Patient {self.i}"

    def __repr__(self) -> str:
        return str(self)

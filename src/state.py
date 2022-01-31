import src.headers as h

"""
NR: count of resting doctors 
NS: count of busy doctors
Q3, Q2, Q1: patients in queues
Time: simulation program time in minutes
FEL: future events list
"""

# initialization
Time = 0
Step = 0
Q3, Q2, Q1 = [], [], []
all_patients = []
NR, NS = 0, 0
FEL = [{h.Type: h.Arrival, h.Time: 0}]
SimulationEndTime = 28800 # minutes
Replication = 100
interarrival_time = 21 # exponential distribution mean
rest_time = 10
random_seed = 4

def initialize():
    global Time, Q3, Q2, Q1, NR, NS, FEL
    Step = 0
    Time = 0
    Q3, Q2, Q1 = [], [], []
    NR, NS = 0, 0
    FEL, TR = [{h.Type: h.Arrival, h.Time: 0}]
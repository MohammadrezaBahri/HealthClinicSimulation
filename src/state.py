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
NS = 0
FEL = [{h.Type: h.Arrival, h.Time: 0}]
warmUp_time = 3500 # minutes
SimulationEndTime = warmUp_time * 11 # minutes
Replication = 20
interarrival_time = 21 # exponential distribution mean
rest_time = 10
random_seed = 4

def initialize():
    global Time, Q3, Q2, Q1, NS, FEL
    Step = 0
    Time = 0
    Q3, Q2, Q1 = [], [], []
    NS = 0
    FEL = [{h.Type: h.Arrival, h.Time: 0}]
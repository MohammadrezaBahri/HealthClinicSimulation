import src.headers as h

"""
NR: count of resting doctors 
NS: count of busy doctors
Q3, Q2, Q1: patients in queues
Time: simulation program time in minutes
FEL: future events list
TR
"""

# initialization
Time = 0
Q3, Q2, Q1 = [], [], []
all_patients = []
NR, NS = 0, 0
FEL, TR = [{h.Type: h.Arrival, h.Time: 0}, {h.Type: h.RestAlert, h.Time: 300}], [300]
SimulationEndTime = 28800 # minutes

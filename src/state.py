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
NR, NS = 0, 0
FEL, TR = [{'Type': 'Arrival', 'Time': 0}], [300]

from numpy import average
from src import state, funcs
from src.patient import Patient
import src.headers as h
import pandas as pd
import os
import time
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

Path("./logs").mkdir(parents=True, exist_ok=True)
Path("./results").mkdir(parents=True, exist_ok=True)

try:
    f = open("logs\events.csv", "w")
    f.close()
except:
    pass

try:
    f = open("logs\FEL.txt", "w")
    f.close()
except:
    pass

f = open("logs\events.csv", "w")
f2 = open("logs\FEL.txt", "w")
f.write("Replication,step,Time,Event,Patient,NS,Q3,Q2,Q1\n")

def simulation(i, f, f2):
    while True:
        state.Step += 1
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Type])
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Time])
        current_event = state.FEL.pop(0)

        if current_event[h.Time] > state.SimulationEndTime:
            break
        
        if f2: f2.write(f"Replication: {i+1}, Time:{current_event[h.Time]}, FEL: {str(state.FEL)}\n")

        if current_event[h.Type] == h.Arrival:
            patient = Patient(current_event[h.Time])
            patient.rep = i
            funcs.Arrival(patient, current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},{patient},{state.NS},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.Departure:
            funcs.Departure(current_event[h.Patient], current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},{current_event[h.Patient]},{state.NS},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        else:
            raise Exception(f"Event {current_event} is invalid")

for i in range(1, 1 + state.Replication):
    os.system('cls')
    print(f"\nSimulating...\n|{'*'*i}{' '*(state.Replication-1-i)}| {100*(i+1)//state.Replication}%")
    state.initialize()
    simulation(i, f, f2)
    

f.close()
f2.close()

try:
    f = open("logs\patients.csv","w")
    f.close()
except:
    pass


f = open("logs\patients.csv","w")
f.write("Name,Replication,Priority,Arrival_time,first_service_start_time,first_service_end_time,second_service_start_time,second_service_end_time\n")

for patient in state.all_patients:
    f.write(f"{patient},{patient.rep},{patient.priority},{patient.arrival_Time},{patient.first_service_start_time},{patient.first_service_end_time},{patient.second_service_start_time},{patient.second_service_end_time}\n")

f.close()

print('Calculating KPIs ...')

# Calculating KPIs
patients = pd.read_csv('logs\patients.csv')
patients = patients[patients['Arrival_time'] > state.warmUp_time]
patients['stay_time'] = patients['second_service_end_time'] - patients['Arrival_time']
patients['first_q'] = patients['first_service_start_time'] - patients['Arrival_time']
pr1_patients = patients[patients['Priority'] == 12]
pr3_patients = patients[patients['Priority'] == 32]

events = pd.read_csv('logs\events.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events = events[events['Time'] > state.warmUp_time]
events['weight'] = events['next_time'] - events['Time']
events['wq1'] = events['Q1'] * events['weight']
events['wq2'] = events['Q1'] * events['weight']
events['wq3'] = events['Q1'] * events['weight']

stay_time1 = pr1_patients.groupby('Replication')['stay_time'].mean()
stay_time3 = pr3_patients.groupby('Replication')['stay_time'].mean()
p3_without_q = (pr3_patients[pr3_patients['Arrival_time'] == pr3_patients['first_service_start_time']].groupby('Replication')['Name'].count()) / (pr3_patients.groupby('Replication')['Name'].count())
p3_first_q = pr3_patients.groupby('Replication')['first_q'].mean()

avg_Q3 = events.groupby('Replication')['wq3'].sum()/events.groupby('Replication')['weight'].sum()
avg_Q2 = events.groupby('Replication')['wq2'].sum()/events.groupby('Replication')['weight'].sum()
avg_Q1 = events.groupby('Replication')['wq1'].sum()/events.groupby('Replication')['weight'].sum()

columns = ['Replication',\
    'average stay time for type 1 patients',\
        'average stay time for type 3 patients',\
            'Ratio of type 3 patients whom never stay in queue',\
                'average queue time for type 3 patients',\
                    'average Q1', 'average Q2', 'average Q3']
KPIs = pd.DataFrame([stay_time1,stay_time3,p3_without_q,p3_first_q,avg_Q1,avg_Q2,avg_Q3]).transpose().reset_index()
KPIs.columns = columns
KPIs.to_excel('results\KPIs.xlsx', index=False)

print('Done!')
time.sleep(3)
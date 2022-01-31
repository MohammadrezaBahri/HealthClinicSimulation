from src import state, funcs
from src.patient import Patient
import src.headers as h
import pandas as pd
import os
import time
from pathlib import Path

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
f.write("Rep,step,Time,Event,Patient,NS,Q3,Q2,Q1\n")

def simulation(i, f, f2):
    while True:
        state.Step += 1
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Type])
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Time])
        current_event = state.FEL.pop(0)

        if current_event[h.Time] > state.SimulationEndTime:
            break
        
        if f2: f2.write(f"Rep: {i+1}, Time:{current_event[h.Time]}, FEL: {str(state.FEL)}\n")

        if current_event[h.Type] == h.Arrival:
            patient = Patient(current_event[h.Time])
            patient.rep = i+1
            funcs.Arrival(patient, current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},{patient},{state.NS},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.Departure:
            funcs.Departure(current_event[h.Patient], current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},{current_event[h.Patient]},{state.NS},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        else:
            raise Exception(f"Event {current_event} is invalid")

for i in range(state.Replication):
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
pr1_patents = patients[patients['Priority'] == 12]
pr3_patents = patients[patients['Priority'] == 32]
events = pd.read_csv('logs\events.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']

KPI1 = (pr1_patents['second_service_end_time'] - pr1_patents['Arrival_time']).mean()
KPI2 = (pr3_patents[pr3_patents['Arrival_time'] == pr3_patents['first_service_start_time']].shape[0]) / (pr3_patents.shape[0]) 
KPI3 = (patients['second_service_end_time'] - patients['first_service_end_time']).mean() 
KPI4 = (pr3_patents['first_service_start_time'] - pr3_patents['Arrival_time']).mean()
max_Q3 = events['Q3'].max()
max_Q2 = events['Q2'].max()
max_Q1 = events['Q1'].max()
avg_Q3 = ((events['Q3'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q2 = ((events['Q2'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q1 = ((events['Q1'] * events['weight']).sum()) / (events['weight'].sum())
doctors_productivity = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 3

KPIs = pd.DataFrame([
    [h.KPI1, KPI1],\
    [h.KPI2, KPI2],\
    [h.KPI3, KPI3],\
    [h.KPI4, KPI4],\
    ['Max Q3', max_Q3],\
    ['Avg. Q3', avg_Q3],\
    ['Max Q2', max_Q2],\
    ['Avg. Q2', avg_Q2],\
    ['Max Q1', max_Q1],\
    ['Avg. Q1', avg_Q2],\
    ['Doctors productivity', doctors_productivity]],\
         columns=['KPI', 'Value'])

# calculating standard deviation
temp = pr1_patents[['Replication', 'second_service_end_time', 'Arrival_time']].copy()
temp['KPI1'] = temp['second_service_end_time'] - temp['Arrival_time']
temp = temp[['Replication','KPI1']].groupby('Replication').mean().reset_index()
KPI1_std = temp['KPI1'].std()

temp = patients[['Replication', 'second_service_end_time', 'first_service_end_time']].copy()
temp['KPI3'] = temp['second_service_end_time'] - temp['first_service_end_time']
temp = temp[['Replication','KPI3']].groupby('Replication').mean().reset_index()
KPI3_std = temp['KPI3'].std()

temp = pr3_patents[['Replication', 'first_service_start_time', 'Arrival_time']].copy()
temp['KPI4'] = temp['first_service_start_time'] - temp['Arrival_time']
temp = temp[['Replication','KPI4']].groupby('Replication').mean().reset_index()
KPI4_std = temp['KPI4'].std()

interval_estimation = pd.DataFrame([[h.KPI1,KPI1,KPI1_std],[h.KPI3,KPI3,KPI3_std],[h.KPI4,KPI4,KPI4_std]], columns=['KPI','mean','STD'])

# saving results
KPIs.to_excel('results\KPIs.xlsx', index=False)
interval_estimation.to_excel('results\interval_estimation.xlsx', index=False)

"""
#############################
# sensivity analysis
print('Doing sensivity analysis...')
# changing interarrival time
#############################
state.interarrival_time = 10
try:
    f = open("logs\events_interarrival_time_10.csv","w")
    f.close()
except:
    pass
f = open("logs\events_interarrival_time_10.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('logs\events_interarrival_time_10.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
max_Q3_2 = events['Q3'].max()
max_Q2_2 = events['Q2'].max()
max_Q1_2 = events['Q1'].max()
avg_Q3_2 = ((events['Q3'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q2_2 = ((events['Q2'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q1_2 = ((events['Q1'] * events['weight']).sum()) / (events['weight'].sum())
#############################
state.interarrival_time = 30
try:
    f = open("logs\events_interarrival_time_30.csv","w")
    f.close()
except:
    pass
f = open("logs\events_interarrival_time_30.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('logs\events_interarrival_time_30.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
max_Q3_3 = events['Q3'].max()
max_Q2_3 = events['Q2'].max()
max_Q1_3 = events['Q1'].max()
avg_Q3_3 = ((events['Q3'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q2_3 = ((events['Q2'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q1_3 = ((events['Q1'] * events['weight']).sum()) / (events['weight'].sum())
#############################
#############################
# changing rest time
#############################
state.interarrival_time = 21
state.rest_time = 1
try:
    f = open("logs\events_rest_time_1.csv","w")
    f.close()
except:
    pass
f = open("logs\events_rest_time_1.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('logs\events_rest_time_1.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
doctors_productivity4 = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 2
#############################
state.rest_time = 30
try:
    f = open("logs\events_rest_time_30.csv","w")
    f.close()
except:
    pass
f = open("logs\events_rest_time_30.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('logs\events_rest_time_30.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
doctors_productivity5 = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 2
#############################
#############################
# changing beta distribution "alpha" parameter
#############################
rest_time = 10
state.a = 3
try:
    f = open("logs\events_alpha_3.csv","w")
    f.close()
except:
    pass
f = open("logs\events_alpha_3.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('logs\events_alpha_3.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
max_Q3_6 = events['Q3'].max()
max_Q2_6 = events['Q2'].max()
max_Q1_6 = events['Q1'].max()
avg_Q3_6 = ((events['Q3'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q2_6 = ((events['Q2'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q1_6 = ((events['Q1'] * events['weight']).sum()) / (events['weight'].sum())
#############################
state.a = 5
try:
    f = open("logs\events_alpha_5.csv","w")
    f.close()
except:
    pass
f = open("logs\events_alpha_5.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('logs\events_alpha_5.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
max_Q3_7 = events['Q3'].max()
max_Q2_7 = events['Q2'].max()
max_Q1_7 = events['Q1'].max()
avg_Q3_7 = ((events['Q3'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q2_7 = ((events['Q2'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q1_7 = ((events['Q1'] * events['weight']).sum()) / (events['weight'].sum())
#############################
#############################
# saving results
interarrival_times = pd.DataFrame([['max Q3',max_Q3,max_Q3_2,max_Q3_3],\
    ['Avg. Q3',avg_Q3,avg_Q3_2,avg_Q3_3],\
        ['max Q2',max_Q2,max_Q2_2,max_Q2_3],\
            ['Avg. Q2',avg_Q2,avg_Q3_2,avg_Q2_3],\
                ['max Q1',max_Q1,max_Q1_2,max_Q1_3],\
                    ['Avg. Q1',avg_Q1,avg_Q1_2,avg_Q1_3]],\
    columns=['KPI',\
        'Value with avg. interarrival time 21',\
            'Value with avg. interarrival time 10',\
                'Value with avg. interarrival time 30'])

rest_times = pd.DataFrame([['Doctors productivity', doctors_productivity,doctors_productivity4,doctors_productivity5]],\
    columns=['KPI',\
        'Value with rest time 10',\
            'Value with rest time 1',\
                'Value with rest time 30'])

alpha_parameter = pd.DataFrame([['max Q3',max_Q3,max_Q3_6,max_Q3_7],\
    ['Avg. Q3',avg_Q3,avg_Q3_6,avg_Q3_7],\
        ['max Q2',max_Q2,max_Q2_6,max_Q2_7],\
            ['Avg. Q2',avg_Q2,avg_Q3_6,avg_Q2_7],\
                ['max Q1',max_Q1,max_Q1_6,max_Q1_7],\
                    ['Avg. Q1',avg_Q1,avg_Q1_6,avg_Q1_7]],\
    columns=['KPI',\
        'Value with alpha parameter 1',\
            'Value with alpha parameter 3',\
                'Value with alpha parameter 5'])

writer = pd.ExcelWriter('results\sensivity_analysis.xlsx', engine='xlsxwriter')

interarrival_times.to_excel(writer, sheet_name='interarrival time', index=False)
rest_times.to_excel(writer, sheet_name='rest time', index=False)
alpha_parameter.to_excel(writer, sheet_name='alpha parameter', index=False)

writer.save()
#############################
"""
print('Done!')
time.sleep(3)
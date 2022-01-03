from src import state, funcs
from src.patient import Patient
import src.headers as h
import pandas as pd
import os

try:
    f = open("events.csv", "w")
    f.close()
except:
    pass

try:
    f = open("FEL.txt", "w")
    f.close()
except:
    pass

f = open("events.csv", "w")
f2 = open("FEL.txt", "w")
f.write("Rep,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")

for i in range(state.Replication):
    os.system('cls')
    print(f"\nSimulating...\n|{'*'*i}{' '*(99-i)}| {i+1}%")
    state.initialize()
    while True:
        f2.write(f"Rep: {i+1}, FEL: {str(state.FEL)}\n")
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Type])
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Time])
        current_event = state.FEL.pop(0)

        if state.NR + state.NS > 2:
            print(f"NR: {state.NR} NS: {state.NS} at time {current_event[h.Time]}")

        if current_event[h.Time] > state.SimulationEndTime:
            break

        state.TR = sorted(state.TR)

        if current_event[h.Type] == h.Arrival:
            patient = Patient(current_event[h.Time])
            funcs.Arrival(patient, current_event[h.Time])
            f.write(f"{i},{current_event[h.Time]},{current_event[h.Type]},{patient},{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.Departure:
            funcs.Departure(current_event[h.Patient], current_event[h.Time])
            f.write(f"{i},{current_event[h.Time]},{current_event[h.Type]},{current_event[h.Patient]},{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.RestAlert:
            funcs.RestAlert(current_event[h.Time])
            f.write(f"{i},{current_event[h.Time]},{current_event[h.Type]},,{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue 
        
        elif current_event[h.Type] == h.SoR:
            funcs.SoR(current_event[h.Time]) 
            f.write(f"{i},{current_event[h.Time]},{current_event[h.Type]},,{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.EoR:
            funcs.EoR(current_event[h.Time])
            f.write(f"{i},{current_event[h.Time]},{current_event[h.Type]},,{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue 
        
        else:
            raise Exception(f"Event {current_event} is invalid")

f.close()
f2.close()

try:
    f = open("patients.csv","w")
    f.close()
except:
    pass


f = open("patients.csv","w")
f.write("Name,Priority,Arrival_time,first_service_start_time,first_service_end_time,second_service_start_time,second_service_end_time\n")

for patient in state.all_patients:
    f.write(f"{patient},{patient.priority},{patient.arrival_Time},{patient.first_service_start_time},{patient.first_service_end_time},{patient.second_service_start_time},{patient.second_service_end_time}\n")

f.close()

print('Calculating KPIs ...')

# Calculating KPIs
patients = pd.read_csv('patients.csv')
pr1_patents = patients[patients['Priority'] == 12]
pr3_patents = patients[patients['Priority'] == 32]
events = pd.read_csv('events.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']

KPI1 = (pr1_patents['second_service_end_time'] - pr1_patents['Arrival_time']).mean()
KPI2 = (pr3_patents[pr3_patents['Arrival_time'] == pr3_patents['first_service_start_time']].shape[0]) / (pr3_patents.shape[0]) 
KPI3 = (patients['second_service_end_time'] - patients['first_service_end_time']).mean() 
max_Q3 = events['Q3'].max()
max_Q2 = events['Q2'].max()
max_Q1 = events['Q1'].max()
avg_Q3 = ((events['Q3'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q2 = ((events['Q2'] * events['weight']).sum()) / (events['weight'].sum())
avg_Q1 = ((events['Q1'] * events['weight']).sum()) / (events['weight'].sum())
doctors_productivity = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 2 # Doctors productivity
KPI4 = (pr3_patents['first_service_start_time'] - pr3_patents['Arrival_time']).mean()

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

KPIs.to_excel('KPIs.xlsx', index=False)

print('Done!')

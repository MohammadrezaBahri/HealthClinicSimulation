from src import state, funcs
from src.patient import Patient
import src.headers as h
import pandas as pd
import os
import time

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
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")

def simulation(i, f, f2):
    while True:
        state.Step += 1
        state.TR = sorted(state.TR)
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Type])
        state.FEL = sorted(state.FEL,key=lambda event: event[h.Time])
        current_event = state.FEL.pop(0)

        if current_event[h.Time] > state.SimulationEndTime:
            break
        
        if f2: f2.write(f"Rep: {i+1}, FEL: {str(state.FEL)}\n")

        if current_event[h.Type] == h.Arrival:
            patient = Patient(current_event[h.Time])
            funcs.Arrival(patient, current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},{patient},{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.Departure:
            funcs.Departure(current_event[h.Patient], current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},{current_event[h.Patient]},{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.RestAlert:
            funcs.RestAlert(current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},,{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue 
        
        elif current_event[h.Type] == h.SoR:
            funcs.SoR(current_event[h.Time]) 
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},,{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
            continue
        
        elif current_event[h.Type] == h.EoR:
            funcs.EoR(current_event[h.Time])
            f.write(f"{i},{state.Step},{current_event[h.Time]},{current_event[h.Type]},,{state.NS},{state.NR},{len(state.Q3)},{len(state.Q2)},{len(state.Q1)}\n")
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
doctors_productivity = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 2
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

# sensivity analysis
print('Doing sensivity analysis...')
#############################
# changing interarrival time
#############################
state.interarrival_time = 10
try:
    f = open("events_interarrival_time_10.csv","w")
    f.close()
except:
    pass
f = open("events_interarrival_time_10.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('events_interarrival_time_10.csv')
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
    f = open("events_interarrival_time_30.csv","w")
    f.close()
except:
    pass
f = open("events_interarrival_time_30.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('events_interarrival_time_30.csv')
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
state.rest_time = 1
try:
    f = open("events_rest_time_1.csv","w")
    f.close()
except:
    pass
f = open("events_rest_time_1.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('events_rest_time_1.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
doctors_productivity4 = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 2
#############################
state.rest_time = 30
try:
    f = open("events_rest_time_30.csv","w")
    f.close()
except:
    pass
f = open("events_rest_time_30.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('events_rest_time_30.csv')
events['next_time'] = events['Time'].shift(-1, fill_value=state.SimulationEndTime).replace(0, state.SimulationEndTime)
events['weight'] = events['next_time'] - events['Time']
doctors_productivity5 = (((events['NS'] * events['weight']).sum()) / (events['weight'].sum())) / 2
#############################
#############################
# changing beta distribution "alpha" parameter
#############################
state.a = 3
try:
    f = open("events_alpha_3.csv","w")
    f.close()
except:
    pass
f = open("events_alpha_3.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('events_alpha_3.csv')
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
    f = open("events_alpha_5.csv","w")
    f.close()
except:
    pass
f = open("events_alpha_5.csv", "w")
f.write("Rep,step,Time,Event,Patient,NS,NR,Q3,Q2,Q1\n")
state.initialize()
simulation(1,f,None)
f.close()
events = pd.read_csv('events_alpha_5.csv')
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
writer = pd.ExcelWriter('sensivity_analysis.xlsx', engine='xlsxwriter')

pd.DataFrame().to_excel(writer, sheet_name='interarrival time')
pd.DataFrame().to_excel(writer, sheet_name='rest time')
pd.DataFrame().to_excel(writer, sheet_name='alpha parameter')

writer.save()
#############################

print('Done!')
time.sleep(5)
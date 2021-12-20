from src import state, funcs
from src.patient import Patient
import src.headers as h

while True:
    state.FEL = sorted(state.FEL, key=lambda event: event[h.Time])
    current_event = state.FEL.pop(0)

    if current_event[h.Time] > state.SimulationEndTime:
        break

    state.TR = sorted(state.TR)

    if current_event[h.Type] == h.Arrival:
        funcs.Arrival(Patient(current_event[h.Time]), current_event[h.Time]) 
        continue
    
    elif current_event[h.Type] == h.Departure:
        funcs.Departure(current_event[h.Patient], current_event[h.Time])
        continue
    
    elif current_event[h.Type] == h.RestAlert:
        funcs.RestAlert(current_event[h.Time])
        continue 
    
    elif current_event[h.Type] == h.SoR:
        funcs.SoR(current_event[h.Time]) 
        continue
    
    elif current_event[h.Type] == h.EoR:
        funcs.EoR(current_event[h.Time])
        continue 
    
    else:
        raise Exception(f"Event {current_event} is invalid")


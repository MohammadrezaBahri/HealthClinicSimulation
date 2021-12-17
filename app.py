from src import state, funcs
from patient import Patient

FEL = sorted(state.FEL, key=lambda x: x['Time'])
print(FEL)
current_event = FEL.pop(0)
print(current_event)

if current_event['Type'] == 'Arrival':
    pass 
elif current_event['Type'] == 'Departure':
    pass
elif current_event['Type'] == 'RestAlert':
    pass 
elif current_event['Type'] == 'SoR':
    pass 
elif current_event['Type'] == 'EoR':
    pass 
else:
    raise Exception(f"Event {current_event} is invalid")
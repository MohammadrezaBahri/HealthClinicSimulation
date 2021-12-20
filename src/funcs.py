import src.state as state
from src.patient import Patient
from src.random_generator import uniform, expopnential, triangular, beta
"""from enum import Enum

class events(Enum):
    Arrival = 1
    Departure = 2
    RestAlert = 3
    SoR = 4
    EoR = 5"""

?[{'Type': 'Arrival', 'Time': 0}, {'Type': 'Departure', 'Time': 10, 'patient': Patient(0)}]

def Arrival(patient: Patient, t: int) -> None:
    if patient.priority == 3:
        if ((len(state.Q3) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            patient.served += 1
            state.FEL.append(['Departure', patient, t + state.triangular(22,40,62)])
        else:
            state.Q3.append(patient)
    else:
        if ((len(state.Q3) == 0) and (len(state.Q2) == 0) and (len(state.Q1) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            patient.served += 1
            state.FEL.append(['Departure', patient, t + 3 + 40*beta(1, 3)])
        else:
            state.Q1.append(patient)
    state.FEL.append(['Arrival', t + expopnential(21)])


def Departure(patient: Patient, t: int) -> None:
    state.NS -= 1
    if state.TR[0] == t:
        state.NR += 1
    if patient.served == 0:
        if (state.NR + state.NS) < 2:
            if len(state.Q3) == 0:
                if len(state.Q2) == 0:
                    if len(state.Q1) == 0:
                        pass
                    else:
                        patient2 = state.Q1.pop(0)
                        state.NS += 1
                        state.FEL.append({'Type': 'Departure', 'Time': t + 3 + 40*beta(1, 3), 'patient': patient2})
                else:
                    patient2 = state.Q2.pop(0)
                    state.NS += 1
                    state.FEL.append({'Type': 'Departure', 'Time': ?, 'patient': patient2}) # unknown time
            else:
                patient2 = state.Q3.pop(0)
                state.NS += 1
                state.FEL.append({'Type': 'Departure', 'Time': t + triangular(22,40,62), 'patient': patient2})
        else:
            pass
    else:
        if (state.NR + state.NS) < 2:
            if len(state.Q3) == 0:
                state.NS += 1
                state.FEL.append({'Type': 'Departure', 'Time': ?, 'patient': patient}) # unknown time
            else:
                state.Q2.append(patient)
                patient2 = state.Q3.pop(0)
                state.NS += 1
                state.FEL.append({'Type': 'Departure', 'Time': t + triangular(22,40,62), 'patient': patient2})
        else:
            state.Q2.append(patient)


def RestAlert():
    pass


def SoR():
    pass


def EoR():
    pass

import src.state as state
from src.patient import Patient
from src.random_generator import uniform, expopnential, triangular, beta
import src.headers as h


def Arrival(patient: Patient, t: int) -> None:
    if patient.priority == 3:
        if ((len(state.Q3) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient})
        else:
            state.Q3.append(patient)
    else:
        if ((len(state.Q3) == 0) and (len(state.Q2) == 0) and (len(state.Q1) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            state.FEL.append({h.Type: h.Departure, h.Time: t + 3 + 40*beta(1, 3), h.Patient: patient})
        else:
            state.Q1.append(patient)
    state.FEL.append({h.Type: h.Arrival, h.Time: t + expopnential(1/5)}) ######################################## change 5 to 21


def Departure(patient: Patient, t: int) -> None:
    patient.served += 1
    if patient.priority == 1: patient.priority = 12
    elif patient.priority == 3: patient.priority = 32
    state.NS -= 1

    if state.TR[0] == t: # check here
        state.NR = 1
    
    if patient.served == 1:
        if (state.NR + state.NS) < 2:
            if len(state.Q3) == 0:
                if len(state.Q2) == 0:
                    if len(state.Q1) == 0:
                        pass
                    else:
                        patient2 = state.Q1.pop(0)
                        state.NS += 1
                        state.FEL.append({h.Type: h.Departure, h.Time: t + 3 + 40*beta(1, 3), h.Patient: patient2})
                else:
                    patient2 = state.Q2.pop(0)
                    state.NS += 1
                    _time = triangular(10,12,14) if patient2.priority == 32 else uniform(8,12)
                    state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient2})
            else:
                patient2 = state.Q3.pop(0)
                state.NS += 1
                state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient2})
        else:
            pass
    else:
        if (state.NR + state.NS) < 2:
            if len(state.Q3) == 0:
                state.NS += 1
                _time = triangular(10,12,14) if patient.priority == 32 else uniform(8,12)
                state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient})
            else:
                state.Q2.append(patient)
                patient2 = state.Q3.pop(0)
                state.NS += 1
                state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient2})
        else:
            state.Q2.append(patient)


def RestAlert(t):
    state.TR = [tr for tr in state.TR if tr > t]
    if t%480 == 300:
        if state.NS == 2:
            for event in state.FEL:
                if event[h.Type] == h.Departure:
                    first_departure = event
                    break
            if first_departure[h.Time] < end_of_shift(t):
                state.TR.append(first_departure[h.Time])
                state.FEL.append({h.Type: h.SoR, h.Time: state.TR[0]}) #check here
                state.FEL.append({h.Type: h.RestAlert, h.Time: state.TR[0] + 70}) #?
            else:
                pass
        else:
            state.TR.append(t)
            state.NR += 1
            if (t < (end_of_shift(t) -10)): # is there more than 10 mins to end of shift?
                state.FEL.append({h.Type: h.EoR, h.Time: t + 10})
            else:
                state.FEL.append({h.Type: h.EoR, h.Time: end_of_shift(t)})
            state.FEL.append({h.Type: h.RestAlert, h.Time: t + 70})
        state.FEL.append({h.Type: h.RestAlert, h.Time: t + 480})

    else:
        if state.NS == 2:
            for event in state.FEL:
                if event[h.Type] == h.Departure:
                    first_departure = event
                    break
            if first_departure[h.Time] < end_of_shift(t):
                state.TR.append(event[h.Time])
                state.FEL.append({h.Type: h.SoR, h.Time: state.TR[0]}) #check here
            else:
                pass
        else:
            state.TR.append(t)
            state.NR += 1
            if (t < (end_of_shift(t) -10)):
                state.FEL.append({h.Type: h.EoR, h.Time: t + 10})
            else:
                state.FEL.append({h.Type: h.EoR, h.Time: end_of_shift(t)})



def SoR(t: int):
    state.NR = 1
    if (t < (end_of_shift(t) -10)):
        state.FEL.append({h.Type: h.EoR, h.Time: t + 10})
    else:
        state.FEL.append({h.Type: h.EoR, h.Time: end_of_shift(t)})


def EoR(t):
    state.NR = 0
    if len(state.Q3) == 0:
        if len(state.Q2) == 0:
            if len(state.Q1) == 0:
                pass
            else:
                patient2 = state.Q1.pop(0)
                state.NS += 1
                state.FEL.append({h.Type: h.Departure, h.Time: t + 3 + 40*beta(1, 3), h.Patient: patient2})
        else:
            patient2 = state.Q2.pop(0)
            state.NS += 1
            _time = triangular(10,12,14) if patient2.priority == 32 else uniform(8,12)
            state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient2})
    else:
        patient2 = state.Q3.pop(0)
        state.NS += 1
        state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient2})


def end_of_shift(t: int) -> int:
    # returns the time this shift ends
    return ((t//480) + 1)*480

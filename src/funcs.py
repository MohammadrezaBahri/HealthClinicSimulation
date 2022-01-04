import src.state as state
from src.patient import Patient
from src.random_generator import uniform, expopnential, triangular, beta
import src.headers as h


def Arrival(patient: Patient, t: int) -> None:
    if patient.priority == 3:
        if ((len(state.Q3) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            patient.first_service_start_time = t
            state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient})
        else:
            state.Q3.append(patient)
    else:
        if ((len(state.Q3) == 0) and (len(state.Q2) == 0) and (len(state.Q1) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            patient.first_service_start_time = t
            state.FEL.append({h.Type: h.Departure, h.Time: t + 3 + 40*beta(state.a, state.b), h.Patient: patient})
        else:
            state.Q1.append(patient)
    state.FEL.append({h.Type: h.Arrival, h.Time: t + expopnential(1/state.inter_arrival_time)})


def Departure(patient: Patient, t: int) -> None:
    patient.served += 1
    if patient.priority == 1: 
        patient.priority = 12
        patient.first_service_end_time = t
    elif patient.priority == 3: 
        patient.priority = 32
        patient.first_service_end_time = t
    else:
        patient.second_service_end_time = t
        state.all_patients.append(patient)
    
    state.NS -= 1

    if t in state.TR: # check here
        state.NR = 1
    
    if patient.served == 2:
        if (state.NR + state.NS) < 2:
            if len(state.Q3) == 0:
                if len(state.Q2) == 0:
                    if len(state.Q1) == 0:
                        pass
                    else:
                        state.NS += 1
                        patient2 = state.Q1.pop(0)
                        patient2.first_service_start_time = t
                        state.FEL.append({h.Type: h.Departure, h.Time: t + 3 + 40*beta(state.a, state.b), h.Patient: patient2})
                else:
                    state.NS += 1
                    patient2 = state.Q2.pop(0)
                    patient2.second_service_start_time = t
                    _time = triangular(10,12,14) if patient2.priority == 32 else uniform(8,12)
                    state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient2})
            else:
                state.NS += 1
                patient2 = state.Q3.pop(0)
                patient2.first_service_start_time = t
                state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient2})
        else:
            pass
    else:
        if (state.NR + state.NS) < 2:
            if len(state.Q3) == 0:
                state.NS += 1
                patient.second_service_start_time = t
                _time = triangular(10,12,14) if patient.priority == 32 else uniform(8,12)
                state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient})
            else:
                state.Q2.append(patient)
                state.NS += 1
                patient2 = state.Q3.pop(0)
                patient2.first_service_start_time = t
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
            if (t < (end_of_shift(t) - state.rest_time)):
                state.FEL.append({h.Type: h.EoR, h.Time: t + state.rest_time})
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
            if (t < (end_of_shift(t) - state.rest_time)):
                state.FEL.append({h.Type: h.EoR, h.Time: t + state.rest_time})
            else:
                state.FEL.append({h.Type: h.EoR, h.Time: end_of_shift(t)})



def SoR(t: int):
    state.NR = 1
    if (t < (end_of_shift(t) - state.rest_time)):
        state.FEL.append({h.Type: h.EoR, h.Time: t + state.rest_time})
    else:
        state.FEL.append({h.Type: h.EoR, h.Time: end_of_shift(t)})


def EoR(t):
    state.NR = 0
    if len(state.Q3) == 0:
        if len(state.Q2) == 0:
            if len(state.Q1) == 0:
                pass
            else:
                state.NS += 1
                patient2 = state.Q1.pop(0)
                patient2.first_service_start_time = t
                state.FEL.append({h.Type: h.Departure, h.Time: t + 3 + 40*beta(state.a, state.b), h.Patient: patient2})
        else:
            state.NS += 1
            patient2 = state.Q2.pop(0)
            patient2.second_service_start_time = t
            _time = triangular(10,12,14) if patient2.priority == 32 else uniform(8,12)
            state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient2})
    else:
        state.NS += 1
        patient2 = state.Q3.pop(0)
        patient2.first_service_start_time = t
        state.FEL.append({h.Type: h.Departure, h.Time: t + triangular(22,40,62), h.Patient: patient2})


def end_of_shift(t: int) -> int:
    # returns the time this shift ends
    return ((t//480) + 1)*480

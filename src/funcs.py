import src.state as state
from src.patient import Patient
from src.random_generator import uniform, expopnential, triangular, beta
import src.headers as h


def Arrival(patient: Patient, t: int) -> None:
    if patient.priority == 3:
        if ((len(state.Q3) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            patient.first_service_start_time = t
            state.FEL.append({h.Type: h.Departure, h.Time: t + uniform(9, 20), h.Patient: patient})
        else:
            state.Q3.append(patient)
    else:
        if ((len(state.Q3) == 0) and (len(state.Q2) == 0) and (len(state.Q1) == 0) and ((state.NR + state.NS) < 2)):
            state.NS += 1 
            patient.first_service_start_time = t
            state.FEL.append({h.Type: h.Departure, h.Time: t + uniform(10, 30), h.Patient: patient})
        else:
            state.Q1.append(patient)
    state.FEL.append({h.Type: h.Arrival, h.Time: t + expopnential(1/state.interarrival_time)})


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

    if patient.served == 2:
        if (state.NR + state.NS) < 3:
            if len(state.Q3) == 0:
                if len(state.Q2) == 0:
                    if len(state.Q1) == 0:
                        pass
                    else:
                        state.NS += 1
                        patient2 = state.Q1.pop(0)
                        patient2.first_service_start_time = t
                        state.FEL.append({h.Type: h.Departure, h.Time: t + uniform(10, 30), h.Patient: patient2})
                else:
                    state.NS += 1
                    patient2 = state.Q2.pop(0)
                    patient2.second_service_start_time = t
                    _time = triangular(15, 60, 105) if patient2.priority == 32 else triangular(10, 18, 26)
                    state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient2})
            else:
                state.NS += 1
                patient2 = state.Q3.pop(0)
                patient2.first_service_start_time = t
                state.FEL.append({h.Type: h.Departure, h.Time: t + uniform(9, 20), h.Patient: patient2})
        else:
            pass
    else:
        if (state.NR + state.NS) < 3:
            if len(state.Q3) == 0:
                state.NS += 1
                patient.second_service_start_time = t
                _time = triangular(15, 60, 105) if patient.priority == 32 else triangular(10, 18, 26)
                state.FEL.append({h.Type: h.Departure, h.Time: t + _time, h.Patient: patient})
            else:
                state.Q2.append(patient)
                state.NS += 1
                patient2 = state.Q3.pop(0)
                patient2.first_service_start_time = t
                state.FEL.append({h.Type: h.Departure, h.Time: t + uniform(9, 20), h.Patient: patient2})
        else:
            state.Q2.append(patient)


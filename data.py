from dataclasses import dataclass
import pickle

@dataclass
class Student:
    pc: str
    name: str
    klads: set

@dataclass
class Data:
    students: dict
    status: str # reg | init | run
    
def save():
    with open("data.pkl", "wb") as dbf:
        pickle.dump(data, dbf)
        

try:
    with open("data.pkl", "rb") as dbf:
        data: Data = pickle.load(dbf)
except Exception as e:
    data: Data = Data({}, "reg")
    save()
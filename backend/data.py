import pickle
from dataclasses import dataclass

@dataclass
class Data:
    users: list
    configured:bool
    pcs:dict
    

def save():
    with open("data.pkl", "wb") as dbf:
        pickle.dump(data, dbf)
try:
    with open("data.pkl", "rb") as dbf:
        data: Data = pickle.load(dbf)
except Exception as e:
    data: Data = Data([], False, {})
    save()
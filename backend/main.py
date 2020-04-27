from fastapi import FastAPI
from batfish import LibBatfish

app = FastAPI()

data = [
    {"name": "table1",
    "num": 5,
    "size": "big",
    "color": "green",
    "legs": 6},
    {"name": "table2",
     "num": 10,
     "size": "small",
     "color": "red",
     "legs": 7},
     {"name": "table3",
     "num": 12,
     "size": "little",
     "color": "blue",
     "legs": 9}

]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/about")
async def about():
    return {"message": "v.0.0.01b"}

@app.get("/api")
async def getall():
    return data

@app.get("/api/{id}")
async def getone(id: int):
    if id >= len(data):
        return None
    else: 
        return data[id]



import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from batfish import LibBatfish


NETWORK_NAME = "bf1"
SNAPSHOT_NAME = "snapshot-01"
SNAPSHOT_DIR = './networks/bf1'

app = FastAPI()

class aclData(BaseModel):
    srcIps: str
    dstIps: str
    dstPorts: str = None
    ipProtocols: str = "TCP,UDP"

@app.post("/api/check_acl")
def check_acl(data: aclData):
    try:
        LibBatfish.init_existed_snapshot(NETWORK_NAME, SNAPSHOT_NAME)
    except:
        return ":x: **batfish:** can't init snapshot"

    try:
        return LibBatfish.testACL(data.dict())
    except:
        return ":x: **batfish:** can't check acl. perhaps wrong request"
    

@app.get("/")
async def root():
    return {"message": "batfish backend"}

@app.get("/about")
async def about():
    return {"message": "v.0.0.01b"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


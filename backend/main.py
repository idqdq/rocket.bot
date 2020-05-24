import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from ipaddress import ip_address
from os import environ
from batfish import LibBatfish
from findport import FindPortByAddress, FindPortByMac

BF_HOSTNAME = environ.get("BF_HOSTNAME") if environ.get("BF_HOSTNAME") else "localhost"
NETWORK_NAME = environ.get("BF_NETWORK_NAME") if environ.get("BF_NETWORK_NAME") else "bf1" 
SNAPSHOT_NAME = environ.get("BF_SNAPSHOT_NAME") if environ.get("BF_SNAPSHOT_NAME") else "snapshot-01"
SNAPSHOT_DIR = environ.get("BF_SNAPSHOT_DIR") if environ.get("BF_SNAPSHOT_DIR") else "./bf_snapshots/networks/bf1"

app = FastAPI()

class aclData(BaseModel):
    srcIps: str
    dstIps: str
    dstPorts: str = None
    ipProtocols: str = "TCP,UDP"

class aceData(BaseModel):
    acl: str
    device: str
    lines: int = 4 # default. returns 4 lines

def InitBatfish():
    try:
        LibBatfish.init_existed_snapshot(NETWORK_NAME, SNAPSHOT_NAME)
        return True
    except:
        return False


@app.post("/api/check_acl")
def check_acl(data: aclData):       
    if InitBatfish():
        try:
            return LibBatfish.testACL(data.dict())
        except:
            return ":x: **batfish:** can't check acl. perhaps wrong request"
    
    return ":x: **batfish:** can't init snapshot"


# @netbot acl unreachable VL20_OUT n7k1 5 - prints 5 lines of unreachable ace's of the given acl
@app.post("/api/check_unreachable_ace")  
def check_unreachable_ace(data: aceData):    
    if InitBatfish():
        try:
            return LibBatfish.getUnreachableACE(data.dict())
        except:
            return ":x: **batfish:** can't check acl. perhaps wrong request"
    
    return ":x: **batfish:** can't init snapshot"


# @netbot init - init a batfish snapshot (needed if running first time or if config files were changed)
@app.get("/api/initbf")
def init_bf_snapshot():
    try:
        LibBatfish.init_new_snapshot(NETWORK_NAME, SNAPSHOT_NAME, SNAPSHOT_DIR, BF_HOSTNAME)
        return ":white_check_mark: snapshot has been initialized successfully"
    except:
        return ":x: **batfish** can't init snapshot"


# @netbot findport ( name | IP ) - shows the port the requested device is connected to 
@app.get("/api/findport")
def findport(address: str):
    try:
        return FindPortByAddress(address)    
    except:
        return ":x: internal error!"
    

# @netbot findport mac macaddress site_id - find the port (by mac) the requested device is connected to 
class macData(BaseModel):
    mac: str
    site: int = 1

@app.post("/api/findportbymac")
def findportbymac(data: macData):
    try:
        return FindPortByMac(data.mac, data.site)
    except:
        return ":x: internal error!"


@app.get("/")
async def root():
    return {"message": "batfish backend"}


@app.get("/about")
async def about():
    return {"message": "v.0.0.01b"}

# comment it out in case of debugging
#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)


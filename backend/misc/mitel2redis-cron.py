#/usr/bin/env python3
# the script does ssh to the PBX (Mitel) run a command (extension_info) and parses output to a dictionary
# then put that dictionary into a Redis
#
# The Output sample: 
#
#(venv) nryzhkov@rigel:~$ ssh ryzhkoff@10.1.90.1 '/opt/eri_sn/bin/extension_info -d 1200..1222 -p --terminal-info'
# Warning: No matching group found, level is 0
# Extension Info
# Dir        Terminal Revision           Vendor                              Terminal                  
#            Type                        Info                                Identity                  
# 1202       SIP      6.2-HF02BG18       Mitel SIP-DECT                      sip:1202@10.1.191.1;instance=urn:uuid:1F102ACA-0E00-0100-8000-0300a3e4b8f5
# 1204       SIP      5.0.0.2036         6865i                               sip:1204@10.1.93.142;instance=urn:uuid:00000000-0000-1000-8000-00085D54150D
# 1206       SIP      4.2.0.2023         6869i                               sip:1206@10.1.93.152;instance=urn:uuid:00000000-0000-1000-8000-00085D4A970B
# 1218       SIP      6.2-HF02BG18       Mitel SIP-DECT                      sip:1218@10.1.191.1;instance=urn:uuid:1F102ACA-0E00-0100-8000-03028698cd9a
# 1219       SIP      5.0.0.2036         6865i                               sip:1219@10.1.93.7;instance=urn:uuid:00000000-0000-1000-8000-00085D51D799
# 1220       SIP      6.2-HF02BG18       Mitel SIP-DECT                      sip:1220@10.1.191.1;instance=urn:uuid:1F102ACA-0E00-0100-8000-030242debfa7
# Warning: No matching group found, level is 0
# 

import os, socket, re
from ssh2.session import Session

host = "10.1.90.1"
user = "ryzhkoff"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, 22))

session = Session()
session.handshake(sock)
session.userauth_publickey_fromfile(user, "/home/nryzhkov/.ssh/id_rsa")
#session.agent_auth(user) # <-- auth by ssh keys if users match on both side
#session.userauth_password(user,passwd)

channel = session.open_session()
channel.execute('/opt/eri_sn/bin/extension_info -d all -p --terminal-info')

out = ""
size, data = channel.read()

while size > 0:    
    out += data.decode("utf-8") 
    size, data = channel.read()    
channel.close()
#print(out)

baza = {}
for num,line in enumerate(out.split('\n')):
    # filter out strings with wrong TYPE 
    if line[11:14] != 'SIP': continue
        
    res = re.split(r'[:@;-]', line.split(' ')[-1])    

    if len(res)>=3 :
        baza[res[1]] = dict(ip=res[2], mac=res[-1] if res[2] != res[-1] else '000000000000')     

# now put it to Redis
import redis, json
r = redis.Redis()
with r.pipeline() as pipe:
    for id, data in baza.items():
        pipe.set(id, json.dumps(data))
    pipe.execute()
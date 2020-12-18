#!/usr/bin/env python3
# the script does ssh to the PBX (Mitel) run a command (extension_info) and parses output to a dictionary
# then put that dictionary into a local Redis (@netbot port phone function to work)
# and additionally transforms the dict to a csv file and sends that file by email
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
# script is executed weekly by cron (/etc/cron.weekly/mitel2redis)

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

baza = {}
for num,line in enumerate(out.split('\n')):
    # filter out strings with wrong TYPE 
    if line[11:14] != 'SIP': continue    
    res = re.split(r'[:@;-]', line.split()[-1])

    # ignore EDN (have no idea what is it anyway)
    if res[1] == 'EDN':
        res.pop(1)

    if len(res)>=3 :
        baza[res[1]] = dict(ip=res[2], mac=res[-1] if res[2] != res[-1] else '000000000000')     


# now put it to Redis
import redis, json
r = redis.Redis()
with r.pipeline() as pipe:
    for id, data in baza.items():
        pipe.set(id, json.dumps(data))
    pipe.execute()


# create csv file
import csv

field_names = ['number', 'ip', 'mac']
with open('/tmp/mitel_extensions_output.csv', 'w') as output:
    writer = csv.DictWriter(output, fieldnames=field_names)
    writer.writeheader()
    writer.writerows([ dict(number=key, ip=val['ip'], mac=val['mac']) for key,val in baza.items()])


# send file by email
import email, smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_server = "algol.msk.vbrr.loc"
sender_email = "nryzhkov@rigel.msk.vbrr.loc"
receiver_email = "=?utf-8?B?0KDRi9C20LrQvtCyINCd0LjQutC+0LvQsNC5INCS0LjRgtCw0LvRjNC10LI=?= =?utf-8?B?0LjRhw==?= <Ryzhkov@vbrr.ru>,\
    =?utf-8?B?0JrRg9Cx0LvQuCDQodC10YDQs9C10Lkg0JLQsNC70LXQvdGC0LjQvdC+0LI=?= =?utf-8?B?0LjRhw==?= <Kubli_SV@vbrr.ru>, \
    =?utf-8?B?0J/RgNC+0YHRgtC40L0g0JvQtdC+0L3QuNC0INCS0LvQsNC00LjQvNC40YA=?= =?utf-8?B?0L7QstC40Yc=?= <Prostin_LV@vbrr.ru>"

subject = "Mitel Phone extensions numbers with their IP and MACs"
body = "CSV file attached"

message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

filename = "/tmp/mitel_extensions_output.csv" 
with open(filename, "r") as attachment:
    part = MIMEBase("text", "csv")
    part.set_payload(attachment.read())
part.add_header("Content-Disposition", f"attachment; filename= {filename}")
message.attach(part)
text = message.as_string()

try:
    server = smtplib.SMTP(smtp_server)
    server.ehlo() 
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
except Exception as e:
    print(e)

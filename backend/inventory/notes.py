# notes

host = 'catalyst19'
user = 'admin'
pasw = '$$$$$$'

vlan = 21
mac = 'f4ce.46f3.523a'
cmd = 'show mac address-table vlan {} | i {}'.format(vlan,mac)

import napalm

driver = napalm.get_network_driver("ios")

with driver(host, user, pasw) as device:

    device.open()

    cli_cmd = [cmd]
    res = device.cli(cli_cmd)

# res
#  {'show mac address-table vlan 21 | i f4ce.46f3.523a': '21    f4ce.46f3.523a    DYNAMIC     Po48'}

# res[cmd[0]].split()[-1]
# 'Po48'

"""
1. gethostbyname => IP
2. look for arp in redis if its empty fetch arp from the core and put it back to redis (TTL value?)
3. get mac from arp
4. look for fdb in redis

----------------------------------------------------------------------------------------------------------

N7K1# sh ip arp vlan 21 | i 10.2.1.96
10.2.1.96       00:16:29  4ccc.6a55.f1b5  Vlan21          

out = '10.2.1.96       00:16:29  4ccc.6a55.f1b5  Vlan21'
mac = out.split()[2]  # <== 4ccc.6a55.f1b5



In [11]: macout = '''
    ...:  Note: MAC table entries displayed are getting read from software. 
    ...:  Use the 'hardware-age' keyword to get information related to 'Age'  
    ...:  
    ...:  Legend:  
    ...:         * - primary entry, G - Gateway MAC, (R) - Routed MAC, O - Overlay MAC 
    ...:         age - seconds since last seen,+ - primary entry using vPC Peer-Link, 
    ...:         (T) - True, (F) - False ,  ~~~ - use 'hardware-age' keyword to retrieve age info  
    ...:    VLAN     MAC Address      Type      age     Secure NTFY Ports/SWID.SSID.LID 
    ...: ---------+-----------------+--------+---------+------+----+------------------ 
    ...: * 21       0050.569e.3d38    dynamic     ~~~      F    F  Po231 
    ...: '''                                                                                                                                         

In [12]: from ntc_templates.parse import parse_output
    ...: fsm = parse_output(platform="cisco_nxos", command="show mac address-table", data=macout)                                                       

In [13]: fsm                                                                                                                                         
Out[13]: 
[{'vlan': '21',
  'mac': '0050.569e.3d38',
  'type': 'dynamic',
  'age': '~~~',
  'secure': 'F',
  'ntfy': 'F',
  'ports': 'Po231'}]

In [14]: fsm[0]['ports']                                                                                                                             
Out[14]: 'Po231'



Switch-31#sh mac address-table address 4c:cc:6a:55:f1:b5 vlan 21

In [22]: macout = ''' 
    ...:           Mac Address Table 
    ...: ------------------------------------------- 
    ...:  
    ...: Vlan    Mac Address       Type        Ports 
    ...: ----    -----------       --------    ----- 
    ...:   21    4ccc.6a55.f1b5    DYNAMIC     Gi1/0/15 
    ...: Total Mac Addresses for this criterion: 1 
    ...: '''                                                                                                                                      

In [23]: fsm = parse_output(platform="cisco_ios", command="show mac address-table", data=macout)                                                     

In [24]: fsm                                                                                                                                         
Out[24]: 
[{'destination_address': '4ccc.6a55.f1b5',
  'type': 'DYNAMIC',
  'vlan': '21',
  'destination_port': 'Gi1/0/15'}]



"""

# playing with batfish on n7k1 and n7k2 configs
#
# snapshot file tree:
# 
# .
# └── networks
#     └── bf1
#         └── configs
#             ├── n7k1.cfg
#             └── n7k2.cfg

import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq

bf_session.host = 'localhost'
bf_set_network('bf1')
SNAPSHOT_DIR = './networks/bf1'
bf_init_snapshot(SNAPSHOT_DIR, name='snapshot-01', overwrite=True)

load_questions()

result = bfq.nodeProperties().answer().frame() 
result.head(5)
'''                                                                                                                                                           
   Node AS_Path_Access_Lists Authentication_Key_Chains Community_Lists  TACACS_Servers TACACS_Source_Interface                                         VRFs Zones
0  n7k1                   []                        []              []              []                    None           ['SWIFT', 'default', 'management']    []
1  n7k2                   []                        []              []              []                    None  ['GARS-DTLN-SHAB', 'default', 'management']    []
'''
# check an ACL filter for a given flow
result = bfq.searchFilters(headers=HeaderConstraints(srcIps='10.2.1.88', dstIps='10.1.2.214', dstPorts="80",  ipProtocols=['TCP', 'UDP']), action='permit', filters='VL20_OUT').answer().frame()                                                                                                                                                  
'''
status: TRYINGTOASSIGN
.... no task information
status: CHECKINGSTATUS
.... no task information
status: ASSIGNED
.... 2020-04-20 15:09:30.973000+03:00 Begin job.
status: TERMINATEDNORMALLY
.... 2020-04-20 15:09:30.973000+03:00 Begin job.

In [88]: result                                                                                                                                                                   
Out[88]: 
   Node Filter_Name                                               Flow  Action                           Line_Content                                              Trace
0  n7k1    VL20_OUT  start=n7k1 [10.2.1.88:0->10.1.2.214:80 TCP len...  PERMIT  300 permit ip 10.2.1.0/24 10.1.2.0/24  - Matched line 300 permit ip 10.2.1.0/24 10.1....
1  n7k2    VL20_OUT  start=n7k2 [10.2.1.88:0->10.1.2.214:80 TCP len...  PERMIT  300 permit ip 10.2.1.0/24 10.1.2.0/24  - Matched line 300 permit ip 10.2.1.0/24 10.1....
'''
result = bfq.testFilters(headers=HeaderConstraints(srcIps='10.2.1.88', dstIps='10.50.1.163', dstPorts="80",  ipProtocols=['TCP', 'UDP']), filters='VL20_OUT').answer().frame()                                                                                                                                                                    
'''
status: TRYINGTOASSIGN
.... no task information
status: CHECKINGSTATUS
.... no task information
status: CHECKINGSTATUS
.... 2020-04-20 15:24:35.843000+03:00 Begin job.
status: CHECKINGSTATUS
.... 2020-04-20 15:24:35.843000+03:00 Begin job.
status: TERMINATEDNORMALLY
.... 2020-04-20 15:24:35.843000+03:00 Begin job.

In [90]: result                                                                                                                                                                   
Out[90]: 
   Node Filter_Name                                               Flow Action              Line_Content                                    Trace
0  n7k2    VL20_OUT  start=n7k2 [10.2.1.88:49152->10.50.1.163:80 TC...   DENY  5980 deny ip any any log  - Matched line 5980 deny ip any any log
1  n7k2    VL20_OUT  start=n7k2 vrf=management [10.2.1.88:49152->10...   DENY  5980 deny ip any any log  - Matched line 5980 deny ip any any log
2  n7k1    VL20_OUT  start=n7k1 [10.2.1.88:49152->10.50.1.163:80 TC...   DENY  5980 deny ip any any log  - Matched line 5980 deny ip any any log
3  n7k1    VL20_OUT  start=n7k1 vrf=management [10.2.1.88:49152->10...   DENY  5980 deny ip any any log  - Matched line 5980 deny ip any any log
'''



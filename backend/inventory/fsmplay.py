import textfsm

output = """
-------------------------------------------------------------------------------
MAC Address    VLAN/VSI                          Learned-From        Type      
-------------------------------------------------------------------------------
0008-5d51-bd39 160/-                             GE2/0/32            dynamic   

-------------------------------------------------------------------------------
Total items displayed = 1
"""

with open("huawei_display_mac-address.textfsm") as t:
    fsm = textfsm.TextFSM(t)
    result = fsm.ParseText(output)

    res = dict(zip(fsm.header, result[0]))

print(res)  #{'MAC': '0008-5d51-bd39', 'VLAN': '160', 'IF': 'GE2/0/32'}


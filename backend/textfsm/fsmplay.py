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

# Juniper
#VLAN              MAC address       Type         Age Interfaces
#  COMMON            00:08:5d:51:c0:5e Learn          0 ge-0/0/11.0
#
#{master:0}
output = '  COMMON            00:08:5d:51:c0:5e Learn          0 ge-0/0/11.0\n\n{master:0}'


with open('juniper_show_ethernet-switching_table.textfsm') as t:
    fsm = textfsm.TextFSM(t)
    result = fsm.ParseText(output)

    res = dict(zip(fsm.header, result[0]))

    print(res)

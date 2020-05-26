# temporary test file to figure out how to ssh upon huawei switches faster

import napalm, textfsm

def get_port_by_mac_huawei(host, mac, vlan=None):
    driver = napalm.get_network_driver(host['platform'])
    #with driver(host, user, pasw, optional_args={'ssh_config_file': '~/.ssh/ssh_config'}) as device:
    with driver(host['hostname'], host['username'], host['password']) as device:
        device.open()
        cli_cmd = f'display mac-address {mac} vlan {vlan}' if vlan else f'display mac-address {mac}'
        res = device.cli([cli_cmd])
                
        if res:
            output = res[cli_cmd]
            with open("textfsm/huawei_display_mac-address.textfsm") as t:
                fsm = textfsm.TextFSM(t)
                result = fsm.ParseText(output)

                res = dict(zip(fsm.header, result[0]))
                return {'port': res['IF'], 'vlan': res['VLAN']}

from findport import InitInventory

hosts = InitInventory()

mac = '1c66-6d8f-9e41'
print(get_port_by_mac_huawei(hosts['shab-4a'], mac, 160))
# notes #####################################################################################################
#### NAPALM #################################################################################################
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

# huawei uses napalm-huawei-vrp driver
# it has to be installed manually by pip3 install napam-huawei-vrp
#In [6]: get_port_by_mac_huawei(shab4a, mac, 160)
#res = {'MAC': '1c66-6d93-211b', 'VLAN': '160', 'IF': 'GE0/0/24'}


###############################################################################################################
# SCRAPLI #####################################################################################################
#ios: sh mac address-table address 0001.6cd5.ad67 vlan 21
#res = [{'destination_address': '0001.6cd5.ad67', 'type': 'STATIC', 'vlan': '21', 'destination_port': 'Gi1/0/17'}]
#nxos: sh mac address-table vlan 21 address 4c:cc:6a:55:f1:b5
#res = [{'vlan': '21', 'mac': '4ccc.6a55.f1b5', 'type': 'dynamic', 'age': '~~~', 'secure': 'F', 'ntfy': 'F', 'ports': 'Po31'}]

from scrapli.driver.core import IOSXEDriver, NXOSDriver, JunosDriver

def get_port_by_mac(host, mac, vlan=None):

    if host['platform'] not in ('ios', 'nxos'):
        return get_port_by_mac_huawei(host, mac, vlan)
    
    platform_map = {
      'ios': {
        'driver': IOSXEDriver,
        'cmd': f'sh mac address-table address {mac} vlan {vlan}' if vlan else f'sh mac address-table address {mac}',
        'port': 'destination_port'
      },
      'nxos': {
        'driver': NXOSDriver,
        'cmd': f'sh mac address-table vlan {vlan} address {mac}' if vlan else f'sh mac address-table address {mac}',
        'port': 'ports'
      }
    }

    platform = platform_map[host['platform']]
    res = QuerySwitch(host, platform)
    if res:
        return { 'port': res[0][platform['port']], 'vlan': res[0]['vlan'] }
    else:
        return None


def get_mac_by_ip(host, ip):
    platform_map = {
      'ios': {
        'driver': IOSXEDriver,
        'cmd': f'sh ip arp {ip}',
        'mac': 'mac',
        'interface': 'interface'
      },
      'nxos': {
        'driver': NXOSDriver,
        'cmd': f'sh ip arp {ip}',        
        'mac': 'mac',
        'interface': 'interface'
      }
    }

    platform = platform_map[host['platform']]
    res = QuerySwitch(host, platform)
    
    if res:
        mac = res[0][platform['mac']]
        ifName = res[0][platform['interface']]
        vlan = int(''.join(x for x in ifName if x.isdigit())) # transform Vlan221 to 221
        return { 'mac': mac, 'vlan': vlan }
    else:
        return None


def QuerySwitch(host, platform):
    my_device = { 
        "host": host['hostname'],
        "auth_username": host['username'],
        "auth_password": host['password'],
        "auth_strict_key": False,
        "ssh_config_file": True,
    }   
    
    conn = platform['driver'](**my_device)    
   
    conn.open()
    response = conn.send_command(platform['cmd'])
    
    return response.textfsm_parse_output()


def get_port_by_mac_junos(host, mac, vlan=None):

    if host['platform'] not in ('ios', 'nxos'):
        return get_port_by_mac_huawei(host, mac, vlan)
    
    platform_map = {
      'ios': {
        'driver': IOSXEDriver,
        'cmd': f'sh mac address-table address {mac} vlan {vlan}' if vlan else f'sh mac address-table address {mac}',
        'port': 'destination_port'
      },
      'nxos': {
        'driver': NXOSDriver,
        'cmd': f'sh mac address-table vlan {vlan} address {mac}' if vlan else f'sh mac address-table address {mac}',
        'port': 'ports'
      }
    }

    platform = platform_map[host['platform']]
    res = QuerySwitch(host, platform)
    if res:
        return { 'port': res[0][platform['port']], 'vlan': res[0]['vlan'] }
    else:
        return None

"""
Juniper ssh by privkey
In [16]: my_device = {
    ...:     'host': 'ex2200-205',
    ...:     'auth_username': 'rancid',
    ...:     "auth_private_key": "~/rocket/rancid_rsa",
    ...:     "auth_strict_key": False,
    ...:     "ssh_config_file": True,
    ...:     "timeout_transport": 20,
    ...:     }
"""



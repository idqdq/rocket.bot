from ipaddress import ip_address, ip_network
import socket, netaddr
import json, yaml
from scrape import get_mac_by_ip, get_port_by_mac

def InitInventory():
    with open('inventory/hosts.yml') as h, open('inventory/groups.yml') as g:
        try:
            hosts = yaml.safe_load(h)
            groups = yaml.safe_load(g)
        except yaml.YAMLError as e:
            print(e)

    # enrich host data with group data
    for host in hosts.values():
        for group in host['groups']:
            if groups['groups'].get(group):
                val = groups['groups'][group]
                for k,v in val.items():
                    host[k] = v
    return hosts

#In [61]: getSiteCore(siteID=2)                                                                                                                                                     
#Out[61]: 'shab-core'
#In [62]: getSiteCore(ip='10.1.2.3')                                                                                                                                                
#Out[62]: 'n7k1'
def getSiteCore(**kwargs): # {ip: ip} or {siteID: siteID}
    with open('inventory/site_network.yml') as f:
        try:
            sites = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    
    if kwargs.get('ip'):
        ip = kwargs['ip']
        ip  = ip_address(ip)

        for site in sites['sites']:
            for net in site['networks']:
                net = ip_network(net)
                if ip in net:
                    return site['core']        
    
    elif kwargs.get('siteID'):
        siteID = kwargs['siteID']
        for site in sites['sites']:
            if site['siteID'] == siteID:
                return site['core']
    return None


def ValidateMac(mac):
    try:
        mac = netaddr.EUI(mac)        
        return True
    except:
        return False # ":x: incorrect mac address format"


def ConvertMac(mac, platform):
    class mac_hua(netaddr.mac_cisco): pass
    mac_hua.word_sep = '-'

    map = { "ios": netaddr.mac_cisco,
            "nxos": netaddr.mac_cisco,
            "huawei_vrp": mac_hua}
    mac = netaddr.EUI(mac)
    mac.dialect = map[platform]
    return mac


# public func
def FindPortByAddress(address):

    try:
        ip = ip_address(address)
    except:
        try:
            ip = socket.gethostbyname(address)
            ip = ip_address(ip)
        except:
            return False, f":x: address {address} incorect or doesn't exist"

    core = getSiteCore(ip=ip)
    if not core:
        return f":x: address {address} doesn't exist in the network"

    hosts = InitInventory()

    res = get_mac_by_ip(hosts['core'], ip)
    if not res:
        return f":x: address {address} doesn't exist at the moment"
    
    return  FindPortRecursively(hosts, core, res['mac'], res['vlan'])


#public func
def FindPortByMac(mac, siteID):

    core = getSiteCore(siteID=siteID)
    if not core:
        return f":x: mac address {mac} doesn't exist in the network"
    if not ValidateMac(mac):
        return f":x: mac address {mac} is not valid"

    hosts = InitInventory()

    return FindPortRecursively(hosts, core, mac)

    
def FindPortRecursively(hosts, switch, mac, vlan=None, shift=""):
    
    res = get_port_by_mac(hosts[switch], mac, vlan)  # res = {'port': port, 'vlan': vlan}
    if not res:
        return f":x: {shift}[{switch}]() no mac found"

    port = res['port']
    vlan = res['vlan']
    shift += f"[{switch}]({port})"

    newswitch = hosts[switch]['data']['children'].get(port)
    if newswitch:
        shift = shift + " => "
        FindPortRecursively(hosts, newswitch, mac, vlan, shift)
    else:
        return shift


# [n7k1](Po12) => [catalyst19](Po4) => [catalyst101](fa0/1)
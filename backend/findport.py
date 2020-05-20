from ipaddress import ip_address, ip_network
import socket, netaddr
import json, yaml

def getSiteByIP(ip):
    with open('inventory/site_network.yml') as f:
        try:
            nets = yaml.safe_load(f)
        except yaml.YAMLError as e: 
            print(e)
    
    ip  = ip_address(ip)

    for net in nets['sites']:    
        for subnet in net['networks']:
            subnet = ip_network(subnet)
            if ip in subnet: 
                return net['name'], net['core']                
            
    return None, None


def InitInventory():
    with open('inventory/hosts.yml') as h, open('inventory/groups.yml') as g:
        try:
            hosts = yaml.safe_load(h)
            groups = yaml.safe_load(g)
        except yaml.YAMLError as e: 
            print(e)

    # enrich host data with group data
    for host in hosts:        
        for group in host['groups']: 
            if groups['groups'].get(group): 
                val = groups['groups'][group] 
                for k,v in val.items(): 
                    host[k] = v        
    return hosts
    

def ValidateMac(mac, vendor):
    try: 
        mac = netaddr.EUI(mac) 
        mac.dialect = netaddr.mac_cisco
        mac = str(mac)
        return True, mac
    except:
        return Fail, ":x: incorrect mac address format"


def ConvertMac(mac, platform):
    class mac_hua(netaddr.mac_cisco): pass
    mac_hua.word_sep = '-'
    
    map = { "cisco": netaddr.mac_cisco,
            "huawei": mac_hua}
    mac = netaddr.EUI(mac)
    mac.dialect = map[platform]
    return mac



def FindMac(address):
    mac, site = '', 0
    try:
        ip = ip_address(address)
    except:
        try:
            ip = socket.gethostbyname(address)
            ip = ip_address(ip)
        except:
            return False, f"address {address} incorect or doesn't exist"

    site, core = getSiteByIP(ip)
    mac = getMacByIP(ip, core)
    
    return mac, site, core

def FindPort(mac, site):

    hosts = InitInventory()

    def FindPortRecursively(mac, switch, shift=""):
        pass

    return ":warning: the feature hasn't been impemented yet"


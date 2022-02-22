const rmap = {
    "hi" : "hey",
    "thanks" : "You are welcome",
    "bot" : "Come'on - of course NO!! :robot:",
    "bye" : "See ya ... :mask:",
    "привет": "сам привет",
    "func1": func1,
    "meme": meme,
    "zabbix": zabgraf,
    "md": check_md,
    "acl": check_acl,
    "port":findport,
    "ddos": ddos,
};
// help method that returns a set of keys
rmap.help = function() {return Object.keys(rmap).join(', ');}

function func1(args) { 
    return args.join("-");
}

// ************** batfish query section ****************//
const fetch = require('node-fetch');
const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://127.0.0.1:8000/api/";

// Use: @netbot acl any 10.1.2.0/24 [3389] | [3389 (tcp | udp)] 
// rule is based on a batfishe's HeaderConstraints class params
// https://batfish.readthedocs.io/en/latest/datamodel.html#pybatfish.datamodel.flow.HeaderConstraints
// srcIps (str) – Source location/IP
// dstIps (str) – Destination location/IP
// dstPorts – Destination ports as list of ranges, (e.g., "22,53-99")
// ipProtocols – List of well-known IP protocols (e.g., TCP, UDP, ICMP)

async function check_acl(args) {

    //@netbot acl help
    if (args[0] && args[0].toUpperCase() == "HELP") {
        return `## acl help
***acl help*** - prints this;  
***acl init*** - reinit BatFish snapshot (needed after routers configs were changed);  

---

***acl unreachable*** - prints unreachable ACEs for the given *ACL* and *DEVICE*  
command format: *ACL_name Router_name [ lines to return ]*  
*example*:
> @botname acl unreachable VL20_OUT n7k1 5
---
***acl*** - check if a packet can pass through a network policies
command format: *src_addr dst_addr [ dst_port | dst_port (tcp|udp)]*  
*example*: 
> @botname acl 10.2.2.0/24 10.1.102.102 3389 tcp
        `
    }

    //@netbot init
    else if (args[0] && args[0].toUpperCase() == "INIT") {
        try {
            const response = await fetch(BACKEND_API_URL + 'initbf');
            const json = await response.json();
            return json;
        }
        catch (err) {
            return err;
        }
    }

    //@netbot acl unreachable VL20_OUT n7k1 5 - prints 5 lines of unreachable ace's of the given acl
    else if (args[0] && args[0].toUpperCase() == "UNREACHABLE") {
     
        if (3 > args.length || args.length > 4 || (args[3] && isNaN(args[3]))) {
            return ":robot: Incorrect argument numbers or types!\nUse: @BOTNAME acl unreachable ACLNAME DEVICE [ LINES TO RETURN ]";
        }

        const jObj = {};
        jObj["acl"] = args[1];
        jObj["device"] = args[2];
        if (args[3]) jObj["lines"] = args[3];

        try {
            const response = await fetch(BACKEND_API_URL + "check_unreachable_ace",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jObj)
                });
            const json = await response.json();

            return json;
        }
        catch (err) {
            return err;
        }
    }

    //@netbot acl 10.2.3.4 10.1.2.0/24 - find and print a filter that permits or blocks the packet with the given parameters
    else {
        const IpAddrPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)($|\/(3[0-2]|[1-2][0-9]|[0-9])$)/;
        const jkeys = ["srcIps", "dstIps", "dstPorts", "ipProtocols"];
        const IpProtos = ["tcp", "udp"];
        const jObj = {};

        if (2 > args.length || args.length > 4) {
            return ":robot: Incorrect argument numbers!\nUse: @BOTNAME acl 10.2.3.4 10.1.2.0/24 [3389] | [3389 tcp]";
        }

        for (let index = 0; index < args.length; index++) {
            let el = args[index];
            if (index == 0 || index == 1) {
                if (el == 'any') {
                    el = '0.0.0.0';
                }
                if (!IpAddrPattern.test(el)) {
                    return `:robot: Incorrect IP address ${el}`;
                }
            }
            if (index == 2) {
                if (0 > el || el > 65535)
                    return `:robot: Incorrect port number ${el}`;
            }

            if (index == 3) {
                if (IpProtos.indexOf(el) == -1)
                    return `:robot: Incorrect ip protocol ${el}`;
            }

            jObj[jkeys[index]] = el;
        };
        //console.log(jObj);
        //return JSON.stringify(jObj);

        try {
            const response = await fetch(BACKEND_API_URL + "check_acl",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jObj)
                });
            const json = await response.json();
            return json;
        }
        catch (err) {
            return err;
        }
    }
}


async function findport(args) {

    // @netbot findport help
    if (args[0] && args[0].toUpperCase() == "HELP") {
        return `## port help
***port help*** - prints this;  
***port hostname*** - finds the switch and the access port the device with name *hostname* is connected to  
***port ip_address*** - finds the switch and the access port the device with ip address *ip_address* is connected to  
***port mac mac_address site_id*** - finds the switch and the access port the device with mac address *mac_address* is connected to.  
> **site_id**: { 1 : such, 2 : shab, 3 : arbat, 10 : SPB, 20 : Samara }  
***port phone 1234*** - finds the switch and the access port the phone device with the number 1234 is connected to.  
*example*:  
> @botname port 10.2.1.96
> @botname port mac 00:11:22:33:44:55 0
> @botname port phone 1234`
    }
    
    // @netbot port mac MAC site_id | site_id is optional. default is 0
    else if (args[0] && args[0].toUpperCase() == "MAC" && args[1]){ 
        const jObj = {};
        jObj['mac'] = args[1];
        jObj['site'] = args[2] || 0;

        try {
            const response = await fetch(BACKEND_API_URL + "findportbymac/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jObj)
            });            
            const json = await response.json();
            return json;
        }
        catch (err) {
            return err;
        }
    }
    
    // @netbot port phone 1234
    else if (args[0] && args[0].toUpperCase() == "PHONE" && args[1]){ 
        try {
            const response = await fetch(BACKEND_API_URL + "findportbyphone/" + args[1]);
            const json = await response.json();
            return json;
        }
        catch (err) {
            return err;
        }
    }

    // @netbot port (FQDN | IP)
    else if (args[0]) {
        try {
            const response = await fetch(BACKEND_API_URL + "findport/" + args[0]);
            const json = await response.json();
            return json;
        }
        catch (err) {
            return err;
        }
    }

}

async function ddos(args) {
    
    // @netbot ddos help
    if (args[0] && args[0].toUpperCase() == "HELP") {
        return `## port help
***ddos help*** - prints this;  
***ddos token*** - cover or uncover a service under the Kasperski antiDDoS umbrella
*example*:  
> @botname ddos eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoic3RyaW5nIiwicHJpbV9JUCI6IjE5OC41MS4xMDAuNDIiLCJzdWJzdF9JUCI6IjE5OC41MS4xMDAuNDIiLCJUU0lHIjoic3RyaW5nIiwiZGRvcyI6dHJ1ZSwiZXhwIjoxNjMzNTI1MjE2fQ.3upwY-c79z-J3aiGw50seEMhqnjRD1U-F6pZQh55Nu4
`
    }
    //
    else if (args[0]){
        const DDOS_BACKEND_API_URI = 'http://10.2.1.96:8000';
        const API_PATH = '/api/ddosornotddosjwt?token='
        try {
            const response = await fetch(DDOS_BACKEND_API_URI + API_PATH + args[0]);                     
            const json = await response.json();
            return json;
        }
        catch (err) {
            return err;
        }
    }
}

// **************** vsyakaya fignya *****************///

function meme() {
    return {
        "text": "ooops!", "emoji": ":poop:",
        "attachments": [
            {
                "color": "#00AA00",
                "text": "мемчик",
                "image_url": "https://bostonglobe-prod.cdn.arcpublishing.com/resizer/Oyo4TykIQr-wDW3ztz1XsFYa18s=/1024x0/arc-anglerfish-arc2-prod-bostonglobe.s3.amazonaws.com/public/Y5GUIDYVWJGVFP5MWNYJR5375I.png",
            }
        ]
    }
}
function zabgraf() {
    return {
        "text": "Проблемы Zabbix",
        "attachments": [
            {
                "color": "#00AA00",
                "text": "Проблемы Zabbix",
                //"collapsed": true,
                "message_link": "https://zabgraf.vbrr.ru/render/d-solo/bV5WXWqZk/zabbix-problemy?orgId=1&panelId=2&height=800",
                "image_url": "https://zabgraf.vbrr.ru/render/d-solo/bV5WXWqZk/zabbix-problemy?orgId=1&panelId=2&height=800",
            }
        ]
    }
}

function check_md() {
    return `|    | Node   | Filter_Name   | Flow                                                  | Action   | Line_Content                          | Trace                                                |
    |---:|:-------|:--------------|:------------------------------------------------------|:---------|:--------------------------------------|:-----------------------------------------------------|
    |  0 | n7k1   | VL20_OUT      | start=n7k1 [10.2.1.88:0->10.1.2.214:80 TCP length=20] | PERMIT   | 300 permit ip 10.2.1.0/24 10.1.2.0/24 | - Matched line 300 permit ip 10.2.1.0/24 10.1.2.0/24 |
    |  1 | n7k2   | VL20_OUT      | start=n7k2 [10.2.1.88:0->10.1.2.214:80 TCP length=20] | PERMIT   | 300 permit ip 10.2.1.0/24 10.1.2.0/24 | - Matched line 300 permit ip 10.2.1.0/24 10.1.2.0/24 |`;
}


module.exports = rmap;

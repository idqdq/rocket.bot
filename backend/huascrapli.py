# temporary test file to figure out how to ssh upon huawei switches faster

import logging
import time

from scrapli.driver import GenericDriver
from scrapli.driver.core import IOSXEDriver
from scrapli.driver.network_driver import PrivilegeLevel

logging.basicConfig(filename="scrapli.log", level=logging.DEBUG)
logger = logging.getLogger("scrapli")

def main():
    
    PRIVS = {
    "exec": (PrivilegeLevel(r"^[<a-z0-9.\-@()/:]{1,48}[#>$]\s*$", "exec", "", "", "", False, "",)),
    "privilege_exec": (
        PrivilegeLevel(
            r"^[<a-z0-9.\-@()/:]{1,48}[#>$]\s*$",
            "privilege_exec", "exec", "disable", "enable", True, "Password:", )),
    "configuration": (
        PrivilegeLevel(
            r"^\[[a-z0-9.\-@/:]{1,32}\]$",
            "configuration", "privilege_exec", "quit", "system-view", False, "", )),
    }

    mydevice = {
        "host": "192.168.98.1",
        "auth_username": "ansible",
        "auth_password": "ansible",
        "auth_strict_key": False,        
        "ssh_config_file": True,
        "timeout_socket": 20,
        "timeout_transport": 20,
        "privilege_levels": PRIVS
    }
     
    conn = IOSXEDriver(**mydevice)

    conn.open()
    print(conn.get_prompt())
    print(conn.send_command("display version").result)
    conn.close()


if __name__ == "__main__":
    main()
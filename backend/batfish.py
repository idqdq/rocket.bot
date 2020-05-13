import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq

from ipaddress import ip_address

class LibBatfish(object):
    net2acl = {
        "10.1.0": {"in": "VL33_IN", "out": "VL33_OUT"},
        "10.1.2": {"out": "VL20_OUT"},
        "10.1.3": {"out": "VL26_OUT"},
        "10.1.7": {"in": "VL19_IN", "out": "VL19_OUT"},
        "10.1.8": {"in": "VL13_IN", "out": "VL13_OUT"},
        "10.1.54": {"in": "VL54_IN", "out": "VL54_OUT"},
        "10.1.60": {"out": "VL60_OUT"},
        "10.1.61": {"in": "VL61_IN", "out": "VL61_OUT"},
        "10.1.62": {"in": "VL62_IN", "out": "VL62_OUT"},
        "10.1.72": {"in": "VL72_IN", "out": "VL72_OUT"},
        "10.1.102": {"out": "VL102_OUT"},
        "10.1.105": {"in": "QUALYS_IN"},
        "10.1.208": {"out": "VL208_OUT"},
        "192.168.40": {"in": "VL16_IN", "out": "VL16_OUT"},
        "192.168.20": {"in": "VL17_IN"},
    }

    def init_new_snapshot(network, snapshot, snapshot_dir, host="localhost"):
        bf_session.host = host
        bf_set_network(network)
        bf_init_snapshot(snapshot_dir, snapshot, overwrite=True)
        load_questions()

    def init_existed_snapshot(network, snapshot):
        bf_set_network(network)
        bf_set_snapshot(snapshot)
        load_questions()

    def testACL(data):
        hc = HeaderConstraints(**data)
        filters = LibBatfish.getAclNames(data["srcIps"], data["dstIps"])
        if (filters):
            filters = ",".join(filters)
            res = bfq.testFilters(headers=hc,filters=filters,nodes="/n7k/").answer().frame()
            return res.to_markdown()
        else:
            return ":white_check_mark: There is no acl filters applied to the flow"

    def getAclNames(src, dst):
        filters = []

        src = ".".join(src.split(".")[:3])
        dst = ".".join(dst.split(".")[:3])

        x = LibBatfish.net2acl.get(src)
        if (x):
            y = x.get("in")
            if (y): 
                filters.append(y)

        x = LibBatfish.net2acl.get(dst)
        if (x): 
            y = x.get("out")
            if (y): 
                filters.append(y)

        return filters

    def getUnreachableACE(data):
        # returns unreachable ACEs in the given ACL for a device
        res = bfq.filterLineReachability(filters=data["acl"], nodes=data["device"]).answer().frame()
        if not res.empty:
            return res.head(data["lines"]).to_markdown()
        else:
            return f':white_check_mark: There is no unreachable ACE for ACL: {data["acl"]}'

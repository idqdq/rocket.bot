import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq


class LibBatfish(object):
    pass


# result = bfq.testFilters(headers=HeaderConstraints(srcIps='10.2.1.88', dstIps='10.50.1.163', dstPorts="80",  ipProtocols=['TCP', 'UDP']), filters='VL20_OUT').answer().frame()                                                                                                                                                                    

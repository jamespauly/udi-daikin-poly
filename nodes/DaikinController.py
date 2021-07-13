

"""
Get the polyinterface objects we need.  Currently Polyglot Cloud uses
a different Python module which doesn't have the new LOG_HANDLER functionality
"""
import asyncio

import utilities

try:
    from polyinterface import Controller,LOG_HANDLER,LOGGER
except ImportError:
    import pgc_interface as polyinterface
import logging
from pydaikin.discovery import Discovery
from nodes import DaikinNode
from DaikinInterface import DaikinInterface

# IF you want a different log format than the current default
LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class DaikinController(Controller):
    def __init__(self, polyglot):
        super(DaikinController, self).__init__(polyglot)
        self.name = 'Daikin Controller'

    def start(self):
        serverdata = self.poly.get_server_data(check_profile=True)
        LOGGER.info('Started udi-daikin-poly NodeServer {}'.format(serverdata['version']))

        self.check_params()
        self.discover()
        self.setDriver('ST', 1)
        self.set_debug_level(self.getDriver('GV1'))

    def shortPoll(self):
        self.query()

    def longPoll(self):
        self.query()

    def query(self,command=None):
        LOGGER.debug("Query sensor {}".format(self.address))
        # for node in self.nodes:
        #     self.nodes[node].reportDrivers()

        for node in self.nodes:
            if self.nodes[node] is not self:
                self.nodes[node].query()

            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        discovery = Discovery()
        devices = discovery.poll(stop_if_found=None, ip=None)
        for device in iter(devices):
            end_ip = device['ip'][device['ip'].rfind('.') + 1:]
            self.addNode(DaikinNode(self, self.address, end_ip, device['name'], device['ip']))

    def delete(self):
        LOGGER.info('Deleting Daikin controller node.  Deleting sub-nodes...')
        for node in self.nodes:
            if node.address != self.address:
                self.nodes[node].delete()

    def stop(self):
        LOGGER.debug('Daikin NodeServer stopped.')

    def set_module_logs(self,level):
        logging.getLogger('urllib3').setLevel(level)

    def set_debug_level(self,level):
        LOGGER.debug('set_debug_level: {}'.format(level))
        if level is None:
            level = 30
        level = int(level)
        if level == 0:
            level = 30
        LOGGER.info('set_debug_level: Set GV1 to {}'.format(level))
        self.setDriver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        if level <= 10:
            LOGGER.setLevel(logging.DEBUG)
        elif level == 20:
            LOGGER.setLevel(logging.INFO)
        elif level == 30:
            LOGGER.setLevel(logging.WARNING)
        elif level == 40:
            LOGGER.setLevel(logging.ERROR)
        elif level == 50:
            LOGGER.setLevel(logging.CRITICAL)
        else:
            LOGGER.debug("set_debug_level: Unknown level {}".format(level))
        if level < 10:
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            # This is the polyinterface default
            LOG_HANDLER.set_basic_config(True,logging.WARNING)

    def check_params(self):
        self.removeNoticesAll()

    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        LOGGER.debug("cmd_set_debug_mode: {}".format(val))
        self.set_debug_level(val)

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'SET_DM': cmd_set_debug_mode
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV1', 'value': 10, 'uom': 25} # Debug (Log) Mode, default=30=Warning
    ]

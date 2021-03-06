import asyncio

import utilities

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
from DaikinInterface import DaikinInterface

LOGGER = polyinterface.LOGGER

class DaikinNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, ip):
        self.ip = ip
        super(DaikinNode, self).__init__(controller, primary, address, name)

# TODO: Integration in fan mode.
    async def process_fan_mode(self, mode):
        try:
            LOGGER.debug('Process_fan_mode incoming value: ' + str(mode))
            daikin_control = DaikinInterface(self.ip, False)
            await daikin_control.get_control()
            c_mode = mode
            LOGGER.debug('c_mode: ' + str(mode))
            if c_mode == '10':
                c_mode = 'A'
            settings = {'f_rate': c_mode}
            await daikin_control.set(settings)
            self.setDriver("GV3", mode)
        except Exception as ex:
            LOGGER.exception("Could not refresh diakin sensor %s because %s", self.address, ex)

    async def process_mode(self, mode):
        try:
            LOGGER.debug('Process_mode incoming value: ' + str(mode))
            daikin_control = DaikinInterface(self.ip, False)
            settings = {}
            if int(mode) == 0:
                settings = {'mode': 'off'}
            else:
                settings = {'mode': utilities.to_daikin_mode_value(mode)}
            print(settings)
            await daikin_control.set(settings)
            self.setDriver('CLIMD', mode)
        except Exception as ex:
            LOGGER.exception("Could not refresh diakin sensor %s because %s", self.address, ex)

    async def process_temp(self, temp):
        try:
            daikin_control = DaikinInterface(self.ip, False)
            await daikin_control.get_control()
            control = daikin_control.values
            LOGGER.debug('Process_temp temp : ' + str(temp))
            LOGGER.debug('Process_temp stemp: ' + str(control['stemp']))
            if control['stemp'] != 'M':
                LOGGER.debug('process_temp stemp is numeric: ' + str(control['stemp']))
                settings = {'stemp': utilities.fahrenheit_to_celsius(temp)}
                await daikin_control.set(settings)
                self.setDriver("CLISPC", temp)
        except Exception as ex:
            LOGGER.exception("Could not refresh diakin sensor %s because %s", self.address, ex)

    async def process(self):
        try:
            daikin_sensor = DaikinInterface(self.ip, False)
            await daikin_sensor.get_sensor()
            sensor = daikin_sensor.values
            daikin_control = DaikinInterface(self.ip, False)
            await daikin_control.get_control()
            control = daikin_control.values
            LOGGER.debug('Inside Temp: ' + str(utilities.celsius_to_fahrenheit(sensor['htemp'])))
            self.setDriver('ST', utilities.celsius_to_fahrenheit(sensor['htemp']))
            LOGGER.debug('stemp: ' + str(control['stemp']))
            if control['stemp'] != 'M':
                self.setDriver('CLISPC', utilities.celsius_to_fahrenheit(control['stemp']))
                LOGGER.debug('Set Temp: ' + str(control['stemp']))
            LOGGER.debug('Process Mode: ' + str(control['mode']))
            LOGGER.debug('ISY process mode: ' + str(utilities.to_isy_mode_value(control['mode'])))
            if int(control['pow']) == 1:
                self.setDriver('CLIMD', utilities.to_isy_mode_value(int(control['mode'])))
            else:
                self.setDriver('CLIMD', 0)
            LOGGER.debug('Fan Speed: ' + str(control['f_rate']))
            LOGGER.debug('ISY Fan Speed: ' + str(utilities.to_isy_fan_mode_value(control['f_rate'])))
            c_mode = control['f_rate']
            if c_mode == 'A':
                c_mode = 10
            LOGGER.debug('c_mode: ' + str(c_mode))
            self.setDriver('GV3', c_mode)
        except Exception as ex:
            LOGGER.exception("Could not refresh diakin sensor %s because %s", self.address, ex)

    def cmd_set_temp(self, cmd):
        asyncio.run(self.process_temp(cmd['value']))

    def cmd_set_mode(self, cmd):
        asyncio.run(self.process_mode(cmd['value']))

    def cmd_set_fan_mode(self, cmd):
        asyncio.run(self.process_fan_mode(cmd['value']))

    def query(self):
        LOGGER.debug("Query sensor {}".format(self.address))
        asyncio.run(self.process())
        self.reportDrivers()

    def start(self):
        self.query()

# FIXME: Seem that shortpoll is not called in the Node object.  Need to investigate.
    def shortPoll(self):
        LOGGER.debug('shortPoll')
        self.query()

    drivers = [{'driver': 'ST', 'value': 0, 'uom': '17'},  # Current Temp
               {'driver': 'CLISPC', 'value': 0, 'uom': '17'},  # Set Cool Point
               {'driver': 'CLIMD', 'value': 0, 'uom': '67'},  # Current Mode
               {'driver': 'GV3', 'value': 0, 'uom': '25'}  # Set Fan Mode
        ]

    commands = {
        'SET_TEMP': cmd_set_temp,
        'SET_MODE': cmd_set_mode,
        'SET_FAN_MODE': cmd_set_fan_mode
    }

    id = 'daikinnode'

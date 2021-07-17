#!/usr/bin/env python
import udi_interface
import sys
"""
Import the polyglot interface module. This is in pypy so you can just install it
normally. Replace pip with pip3 if you are using python3.

Virtualenv:
pip install polyinterface

Not Virutalenv:
pip install polyinterface --user

*I recommend you ALWAYS develop your NodeServers in virtualenv to maintain
cleanliness, however that isn't required. I do not condone installing pip
modules globally. Use the --user flag, not sudo.
"""
LOGGER = udi_interface.LOGGER
"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""

""" Grab My Controller Node """
from nodes import DaikinController

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([DaikinController])
        """
        Instantiates the Interface to Polyglot.
        The name doesn't really matter unless you are starting it from the
        command line then you need a line Template=N
        where N is the slot number.
        """
        polyglot.start()
        """
        Starts MQTT and connects to Polyglot.
        """
        control = DaikinController(polyglot, 'controller', 'controller', 'Daikin Controller')
        """
        Creates the Controller Node and passes in the Interface
        """
        control.runForever()
        """
        Sits around and does nothing forever, keeping your program running.
        """
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
    sys.exit(0)

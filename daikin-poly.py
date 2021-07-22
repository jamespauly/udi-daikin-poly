#!/usr/bin/env python
import polyinterface
import sys

LOGGER = polyinterface.LOGGER

from nodes import DaikinController

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Daikin')
        polyglot.start()
        control = DaikinController(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
    sys.exit(0)

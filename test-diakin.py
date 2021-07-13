from pydaikin.discovery import Discovery
from DaikinInterface import DaikinInterface
import asyncio



discovery = Discovery()
devices = discovery.poll(stop_if_found=None, ip=None)

for device in iter(devices):
    print(device['ip'])
    print(device['mac'])


async def show_something():

    #appl = Appliance("192.168.86.58", True)
    daikin_control = DaikinInterface("192.168.86.58", False)
    daikin_sensor = DaikinInterface("192.168.86.58", False)

    await daikin_control.get_control()
    control = daikin_control.values
    await daikin_sensor.get_sensor()
    sensor = daikin_sensor.values

    settings = {'pow': '0', 'mode': 'off', 'stemp': control['stemp'], 'shum': control['shum']}

    await daikin_control.set(settings)
    #loop = asyncio.get_event_loop()

    print('test')

    #await daikinBRP069.set(settings = None)


if __name__ == '__main__':
    asyncio.run(show_something())

#print(devices)

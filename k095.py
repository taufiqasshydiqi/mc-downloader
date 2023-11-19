import minimalmodbus
import pandas as pd
import asyncio
import os

from gpiozero import RGBLED
from gpiozero import LED
from datetime import datetime
from colorzero import Color

PROD = False
FILENAME = './log.xlsx'
INTERVAL = 5

# modbus rtu communication paramater setup
BAUDRATE = 9600
BYTESIZES = 8
STOPBITS = 1
TIMEOUT = 0.5
PARITY = minimalmodbus.serial.PARITY_NONE
MODE = minimalmodbus.MODE_RTU
SLAVEID = 1

if (PROD):
    power_led = LED(4)
    signalling = RGBLED(17,27,22)

    device = minimalmodbus.Instrument('/dev/ttyUSB0', SLAVEID)
    device.serial.baudrate = BAUDRATE
    device.serial.bytesize = BYTESIZES
    device.serial.parity = PARITY
    device.serial.stopbits = STOPBITS
    device.serial.timeout = 0.5
    device.mode = MODE
    device.clear_buffers_before_each_transaction = True

    power_led.on()

async def get_data():
    try:
        data = device.read_registers(30256,110,3)

        # Arrange data
        log = {
            # "tanggal": datetime.now().strftime("%d/%m/%Y"),
            "timestamp": datetime.now().isoformat(),
        }

        # Write data
        newLog = pd.DataFrame(data=log, columns=log.keys(), index=[0])
        print(newLog)            
        
        if (not os.path.exists(FILENAME)):
            newLog.to_excel(FILENAME, index=False)
        else:
            logFile = pd.read_excel(FILENAME)
            newLogFile = pd.concat([logFile, newLog]).reset_index(drop=True)
            newLogFile.to_excel(FILENAME, index=False)

        # Signaling if success
        if (PROD) : signalling.blink(on_time=.5, off_time=0.5, on_color=Color('green'), n=1)

    except Exception as e:
        if (PROD) : signalling.blink(on_time=.5, off_time=0.5, on_color=Color('red'), n=1)
        print(e)

# Create an event loop
loop = asyncio.get_event_loop()
# Run the wrapper function until it completes or is cancelled
loop.run_until_complete(get_data())
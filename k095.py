import minimalmodbus
import pandas as pd
import asyncio
import os

from gpiozero import RGBLED
from gpiozero import LED
from gpiozero import DigitalInputDevice
from datetime import datetime
from colorzero import Color

PROD = False
FILENAME = './log.xlsx'
INTERVAL = 5
MODULE = {
    '0000' : 'K095',
    '0001' : 'UNICONN',
    '0010' : 'VORTEX VMC 100',
    '0011' : 'VORTEX VMC 200',
}
INSTRUMENT = MODULE['0000']

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
    bit_0 = DigitalInputDevice(18)
    bit_1 = DigitalInputDevice(23)
    bit_2 = DigitalInputDevice(24)
    bit_3 = DigitalInputDevice(25)
    
    in_switch = str(int(bit_3)) + str(int(bit_2)) + str(int(bit_1)) + str(int(bit_0))
    INSTRUMENT = MODULE[in_switch]

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
        match INSTRUMENT:
            case "K095":
                log = {
                    # "tanggal": datetime.now().strftime("%d/%m/%Y"),
                    "timestamp": datetime.now().isoformat(),
                    "live_phase_a_amps" : data[3],
                    "live_phase_b_amps" : data[4],
                    "live_phase_c_amps" : data[5],
                    "live_ac_volts" : data[7],
                    "calculated_cb_volts" : data[8],
                    "live_ba_volts" : data[9],
                    "live_120v_supply_volts" : data[10],
                    "live_analog_loop_2" : data[11],
                    "live_analog_loop_1" : data[12],
                    "live_supply_frequency" : data[13],
                    "live_backspin_frequency" : data[14],
                    "live_leg-ground_unbalance" : data[16],
                    "live_voltage_unbalance" : data[17],
                    "live_current_unbalance" : data[18],
                    "average_amps_(all_3_phases)" : data[30],
                    "average_volts_(all_3_phases)" : data[31],
                    "power_factor" : data[32],
                    "kwh_ms" : data[107],
                    "kwh_ls" : data[108],
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
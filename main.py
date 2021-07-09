import subprocess
import datetime
import re

def decode(mac_addr, valueStr):
    valueBinary = bytes.fromhex(valueStr[:])
    batt = valueBinary[2] & 0b01111111
    isTemperatureAboveFreezing = valueBinary[4] & 0b10000000
    temp = ( valueBinary[3] & 0b00001111 ) / 10 + ( valueBinary[4] & 0b01111111 )
    if not isTemperatureAboveFreezing:
        temp = -temp
    humid = valueBinary[5] & 0b01111111

    now = datetime.datetime.now().timestamp()

    sensorValue = {
        'SensorType': 'SwitchBot',
        'EpochTime': now,
        'MacAddr': mac_addr,
        'Temperature': temp,
        'Humidity': humid,
        'Battery': batt
    }
    print(sensorValue)

cmd = 'bluetoothctl scan on'
c = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)

key_id = '00000d00-0000-1000-8000-00805f9b34fb'
LEN_DATA = 6
CON_STR_OFFSET = 49

device_line = re.compile(r'Device (([0-9A-Z]{2}[ :])+).*\n')
hex_str = re.compile(r'(([0-9A-Z]{2} )+)')

mark = 0
mac_addr = ''
while True:
    line_as_bytes = c.stdout.readline()
    line = line_as_bytes.decode('utf-8')
    m1 = device_line.search(line)
    m2 = hex_str.search(line)
    if m1:
        mac_addr = m1.group(1).strip().lower()
    elif m2:
        line = m2.group(1)
    else:
        continue
    if mark >= 2:
        try:
            if mark == 2:
                data = line.replace(' ', '')
                decode(mac_addr, data)
        except:
            pass
        finally:
            mark = 0
    if key_id in line or mark > 0:
        mark += 1


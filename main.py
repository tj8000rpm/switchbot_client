#!/usr/bin/python3
import datetime
import json
import pexpect
import pexpect.exceptions
import re
import sys


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


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
    print("switchbot_client: {}".format(json.dumps(sensorValue)), flush=True)


print('switchbot_client: start damoen', flush=True)
#logging.debug('start bluetoothctl and scan on')
p = pexpect.spawn("bluetoothctl")
p.sendline("scan on")

key_id = '00000d00-0000-1000-8000-00805f9b34fb'
LEN_DATA = 6
CON_STR_OFFSET = 49

device_line = re.compile(r'Device (([0-9A-Za-z]{2}[ :])+).*$')
hex_str = re.compile(r'(([0-9A-Za-z]{2} )+)')

mark = 0
mac_addr = ''

print('switchbot_client: start listning', flush=True)

try:
    while True:
        p.expect(r'[\r\n]', timeout=3600)
        line = p.before.decode().strip()
        splits = re.split(r'[\r\n]', line)
        for line in splits:
            sys.stdout.flush()
            plain_line = escape_ansi(line.strip('\r\n'))
            print(plain_line, flush=True)
            if len(plain_line) == 0:
                continue
            if '[bluetooth]#' in plain_line:
                continue
            m1 = device_line.search(plain_line)
            m2 = hex_str.search(plain_line)
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

except pexpect.EOF:
    pass        
finally:
    p.sendline("quit")


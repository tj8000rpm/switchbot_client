#!/usr/bin/python3
import pexpect
import re
import datetime
import pexpect.exceptions


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
    print(sensorValue)


#device_line = r'Device (([0-9A-Z]{2}[ :])+).*[\n\r]'

delimiter = '_special_delm_'

p = pexpect.spawn("bluetoothctl")

p.sendline("scan on")

val_count = {'00000d00-0000-1000-8000-00805f9b34fb': 6}
stored = {}
try:
    while True:
        p.expect(r'[\r\n]', timeout=3600)
        line = p.before.decode().strip()
        splits = re.split(r'[\r\n]', line)
        for line in splits:
            plain_line = escape_ansi(line.strip('\r\n'))
            if len(plain_line) == 0:
                continue
            if '[bluetooth]#' in plain_line:
                continue
            data = plain_line.split(' ')
            if len(data) != 6:
                continue
            if data[0] != '[CHG]' or data[1] != 'Device':
                continue
            mac = data[2]
            adv_type = data[3]
            data_key = data[4].strip(':').lower()
            data_value = data[5]
            key = mac + delimiter + adv_type
            if key not in stored and data_key == "key":
                if data_value not in val_count:
                    continue
                stored[key] = [val_count.get(data_value, 0), ""]
            if key in stored and data_key == "value":
                stored[key][0]-=1
                stored[key][1]+=data_value[2:]

                if stored[key][0] == 0:
                    decode(mac, stored[key][1])
                    #print("* {} : {} ".format(mac, stored[key][1]))
                    del stored[key]
except pexpect.EOF:
    pass        
finally:
    p.sendline("quit")

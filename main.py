#!/usr/bin/env python3

import socket
import time
import sys

HOST = '192.168.0.154'  # The server's hostname or IP address
PORT = 23        # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.settimeout(0.25)


def send_command(fn, cmd):
    raw_send = cmd.encode('utf-8')
    sending = cmd.strip()
    print(f'> {fn} sending "{sending}"')
    s.sendall(raw_send)
    timed_out = False
    data_str = None
    while not timed_out:
        try:
            data = s.recv(1024)
            data_str = data.decode('utf-8').strip()
            print(f'< received "{data_str}"')
        except TimeoutError:
            timed_out = True
    return data_str


def send_command_bytes(fn, raw_send):
    sending = raw_send.decode('utf-8').strip()
    print(f'> {fn} sending "{sending}"')
    s.sendall(raw_send)
    try:
        data = s.recv(1024)
        data_str = data.decode('utf-8').strip()
        print(f'< received "{data_str}"')
        return data_str
    except TimeoutError:
        return None


def fooling():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'?V\r')
        data = s.recv(1024)
        print(f"{ data.decode('utf-8') }")

        # time.sleep(3)fix referencing error introduced by [[User:    except TimeoutError:
        #         return None]]

        s.sendall(b'15FN\r')
        data = s.recv(1024)
        print(f"{ data.decode('utf-8') }")
        data = s.recv(1024)
        print(f"{ data.decode('utf-8') }")

        # time.sleep(3)

        # s.sendall(b'02FN\r')
        data = s.recv(1024)
        print(f"{ data.decode('utf-8') }")
        data = s.recv(1024)
        print(f"{ data.decode('utf-8') }")

        print(f"Arguments count: {len(sys.argv)}")
        for i, arg in enumerate(sys.argv):
            print(f"Argument {i:>6}: {arg}")


def power_on():
    s.sendall(b'\r')
    time.sleep(0.5)
    send_command('power_on', 'PO\r')


def power_off():
    send_command('power_off', 'PF\r')


def set_input(input):

    codes = {
        'DVD': '04',
        'BD': '25',
        'TV': '05',
        'DVR': '15',
        'VIDEO1': '10',
        'VIDEO2': '14',
        'HDMI1': '19',
        'HDMI2': '20',
        'HDMI3': '21',
        'HDMI4': '22',
        'HDMI5': '23',
        'HMG': '26',       # internet radio "Home Media Gallery"
        'iPOD': '17',
        'XM': '18',
        'CD': '01',
        'TAPE': '03',
        'TUNER': '02',
        'PHONO': '00',
        'MULTI': '12',
        'ADAPTER': '33',
        'SIRIUS': '27',
        'HDMI': '31',      # HDMI "cyclic"
    }
    send_command('input', codes[input] + 'FN\r')

def volume_up():
    send_command('volume_up', 'VU\r')


def volume_down():
    send_command('volume_down', 'VD\r')


def get_volume():
    current = ''
    while current[:3] != 'VOL':
        current = send_command('get_volume', '?V\r')
    level = (int(current[3:]) / 2.0) - 80
    return level


def set_volume(decibels):
    val = 1 + (80 + decibels) * 2
    cmd = str(int(val)) + 'VL\r'
    send_command('volume', cmd)


def mute(muted):
    cmd = 'MO\r' if muted else 'MF\r'
    send_command('mute', cmd)


def tuner_preset_number(num):
    send_command('tuner_preset_number', str(num) + 'TP\r')


def tuner_preset_direct(target_class, target_number):
    # cycle the class until we get the one we want
    currently = ''
    while currently[:2] != 'PR':
        currently = send_command('tuner_preset_direct', '?PR\r')

    current_class = currently[2]
    while current_class != target_class:
        currently = send_command('tuner_present_direct', 'TC\r')
        current_class = currently[2]

    # class is set, set the number
    tuner_preset_number(target_number)


def tuner_set_amfm(toAM):
    target = 'A' if toAM else 'F'

    # get frequency
    currently = send_command('tuner_set_amfm', '?FR\r')

    # need a change?
    if currently[2] != target:
        send_command('tuner_set_amfm', 'TB\r')


def tuner_set_direct(toAM, frequency):
    tuner_set_amfm(toAM)


set_input("TUNER")


power_on()
set_input("CD")
set_volume(-37.0)


print(f"volume is {get_volume()} db")

tuner_preset_direct('B', 3)
time.sleep(5)

tuner_preset_direct('A', 1)
time.sleep(5)

# power_off()

# set_input("TV")
# time.sleep(5)
# set_input("DVR")

# mute(True)
# time.sleep(5)
# mute(False)

# set_input("TUNER")
# tuner_preset_number(5)
# time.sleep(5)
# tuner_preset_number(2)
# time.sleep(5)
# set_input("DVR")

# tuner_preset_direct("D05")

# data = s.recv(1024)
# print(f"1> {data.decode('utf-8')}")
# data = s.recv(1024)
# print(f"2> {data.decode('utf-8')}")

# power_off()

set_input("TUNER")
tuner_preset_number(1)

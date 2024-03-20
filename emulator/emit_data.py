import json
import os
import socket
import sys
import time
import random
import threading


sensors = [9827821511462234, 3935342901247781]

template_0 = '545a004d24240407010100000123456789012345140b110a2a2c00000022030a04600000279300000fa' \
           '10a0460000027b6000015bb0a0460000027b6000012a3000baa00193701750123024d0100063fa20d0a'

template_1 = '545a004d24240407010100000123456789012345140b110a2a2c00000022030a04600000279300000fa' \
             '10a0460000027b6000015bb0a0460000027b6000012a3000baa00193701750123024d0100063fa20d0a'


def hex2bin(h): return bin(int(h, 16))[2:].zfill(len(h) * 4)


def set_temperature(dd): return '{:04X}'.format((dd * 10) & ((1 << 12) - 1))


def set_humidity(ddd): return '{:04X}'.format(ddd & ((1 << 12) - 1))


def generate_batch():
    batch = []
    for i in range(0, 20):
        sensor_no = i % 2
        imea = sensors[sensor_no]
        if sensor_no == 0:
            n = set_temperature((random.randint(-2, 10) + 35))
            m = set_humidity((random.randint(-10, 3) + 45))
            k = template_0[0:24] + str(imea).rjust(16, '0') + template_0[40:]
        else:
            n = set_temperature((random.randint(-2, 10) + 5))
            m = set_humidity((random.randint(-10, 3) + 80))
            k = template_1[0:24] + str(imea).rjust(16, '0') + template_1[40:]
        kd = k[0:40] + '160411' + str('{:02x}'.format(i)) + '0000' + k[52:]
        batch.append(kd[0:144] + str(n) + str(m) + kd[152:])
    return batch


def sock_recv(s):
    while True:
        try:
            received = str(s.recv(1024), 'utf_8')
            print(received)
        except socket.error:
            print('Socket error: %s' % socket.error)
            break


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = dir_path + os.path.sep + 'config.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            host = config['host']
            port = config['port']
    except IOError:
        sys.exit('Could not load configuration file.')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        t = threading.Thread(target=sock_recv, args=(sock,), daemon=True)
        t.start()
        try:
            while True:
                for data in generate_batch():
                    time.sleep(15)
                    sock.sendall(bytes.fromhex(data))
        except socket.error:
            print('Socket error: %s' % socket.error)
            sock.close()
            sys.exit('Terminating execution...')
        except KeyboardInterrupt:
            sock.close()
            sys.exit('Received keyboard interrupt. Terminating execution...')

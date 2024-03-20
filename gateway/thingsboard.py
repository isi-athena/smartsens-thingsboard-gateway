import json
import os
import socket
import socketserver
import sys
import time
from datetime import datetime

import paho.mqtt.client as paho

from sensors_protocol.parser import parse_input, convert_input
from sensors_protocol.responses import ack_reply, rtc_time_reply, clear_flash, reboot

mqtt_client = None
tb_broker = None
tb_port = None


def send_data_thingsboard(client, data, key):
    client.username_pw_set(key)
    client.connect(tb_broker, tb_port, keepalive=60)
    client.publish('v1/devices/me/telemetry', data)


class SimpleTCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.data = None

    def handle(self):
        try:
            self.data = self.request.recv(2048)
            self.handle_data()
        except socket.error:
            print('Socket error: %s' % socket.error)

    def handle_data(self):
        print('{} wrote: {}'.format(self.client_address[0], self.data))
        self.data, valid = convert_input(self.data)
        if valid == 1:
            out = parse_input(self.data)
            timer2 = rtc_time_reply().encode('utf_8')
            ack = ack_reply(out['Packet_index']).encode('utf_8')
            self.request.sendall(timer2)
            self.request.sendall(ack)
            print('Temperature: {} | Humidity: {} | Packet_index: {}'.format(out['temperature'], out['humidity'],
                                                                             out['Packet_index']))
            real_t = datetime.fromisoformat(str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())))
            sensor_time = datetime.fromisoformat(out['RTC_time'])
            delay = (real_t - sensor_time).total_seconds()
            out['delay'] = (real_t - sensor_time).total_seconds()
            send_data_thingsboard(mqtt_client, json.dumps(out), out['IMEI'])
            if delay > 300:
                self.request.sendall(clear_flash().encode('utf_8'))
            if out['Packet_index'] > 9000:
                self.request.sendall(reboot().encode('utf_8'))
            print('received: {} | packet created {} | diff sec: {}'.format(real_t, sensor_time, delay))
        elif valid == 2:
            print('response received WIP (for more info) {}'.format(self.data))
            ack = ack_reply(1).encode('utf_8')
            self.request.sendall(ack)
        else:
            print('Invalid')
            self.request.sendall('Invalid packet'.encode('utf_8'))
            self.data = None


class ThreadingTCPHandler(SimpleTCPHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):
        while True:
            try:
                self.data = self.request.recv(2048)
                self.handle_data()
            except socket.error:
                print('Socket error: %s' % socket.error)
                break


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = dir_path + os.path.sep + 'config.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            tb_broker = config['thingsboard']['broker']
            tb_port = config['thingsboard']['port']
            sockserver_address = (config['socketserver']['host'], config['socketserver']['port'])
    except IOError:
        sys.exit('Could not load configuration file.')

    mqtt_client = paho.Client('control1')
    if config['socketserver']['threading']:
        print('Starting Threading TCP Server...')
        sockserver = socketserver.ThreadingTCPServer(sockserver_address, ThreadingTCPHandler)
    else:
        print('Starting Simples TCP Server...')
        sockserver = socketserver.TCPServer(sockserver_address, SimpleTCPHandler)

    with sockserver:
        try:
            sockserver.serve_forever()
        except KeyboardInterrupt:
            sys.exit('Received keyboard interrupt. Terminating execution...')

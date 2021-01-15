import pickle
import json
import socket
import random
import sys
import time

HOST = '192.168.43.195'  # The socket server's hostname or IP address
PORT = 65423        # The port used by the server
node_host = '192.168.43.195'
node_port = 8001
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind((node_host, node_port))
client.connect((HOST, PORT))
moisture = 800

while(1):
    command = client.recv(1024).decode('utf-8')
    if command == "R": # connect to socket
        print("Connected")
    elif command == "A": # transfer 10 data
        print("get ACK")
        count = moisture
        while(1):
            for i in range(10):
                print(count)
                client.send(str(count).encode('utf-8'))
                time.sleep(0.05)
                count -= 1
                if i == 9:
                    time.sleep(0.05)
                    client.send("end".encode('utf-8'))
            break
    elif(( command == "1" ) | (command == "2") | (command == "3") | (command == "4") | (command == "5") | (command == "6") | (command == "7") | (command == "8") | (command == "9")): # watering
        print("W command: "+command)
        moisture -= 200

        

import pickle
import json
import socket
import random
import sys
import time
import select
import tty
import termios
import PySimpleGUI as sg
HOST = '192.168.43.195'  # The socket server's hostname or IP address
PORT = 65423        # The port used by the server

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.setblocking(False)
node_host = '192.168.43.21'
node_port = 19224
sequence = 8505

layout = []

def data_transfer(data):
    temp = data[1:-1].split(",")
    temp[0] = time.ctime(float(temp[0]))
    temp = ",".join(temp)
    return temp

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)

is_connected = False
try:
    tty.setcbreak(sys.stdin.fileno())
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if command == "R":
                is_connected = True
                print("connect success")
            elif "get data" in command:
                current_data = command.split(" ")[2]
                print("current data: ",data_transfer(current_data))
            elif "get sequence:" in command:
                datas = command.split(" ")[2:]
                print("data sequence: ", str(list( data_transfer(x) for x in datas)) )
            elif "need water" in command:
                print("need water")
        except:
            pass
        if(is_connected == True):
            if isData():
                c = sys.stdin.readline()
                if c == "register\n":
                    client.send(("register"+" "+str(node_host)+" " +str(node_port)).encode('utf-8'))
                elif c == "transfer\n":
                    client.send(("transfer" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
                elif c == "getsequence\n":
                    client.send(("getsequence" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
                elif c == "exit\n":
                    client.send(("exit").encode('utf-8'))
                elif c == "connect\n":
                    client.send(("connect" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


        

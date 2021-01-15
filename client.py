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
import eel
import matplotlib.pyplot as plt
import matplotlib
import datetime
HOST = '192.168.43.32'  # The socket server's hostname or IP address
PORT = 65423        # The port used by the server
client_host = '192.168.43.195'
client_port = 4000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind((client_host,client_port))
client.connect((HOST, PORT))
client.setblocking(False)
node_host = '192.168.43.21'
node_port = 19224
sequence = 8505




def data_transfer(data):
    temp = data[1:-1].split(",")
    temp[0] = time.ctime(float(temp[0]))
    temp = ",".join(temp)
    
    return temp

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

#old_settings = termios.tcgetattr(sys.stdin)

is_connected = False

f = open("client_data.txt", "r")
node_list = list(list(x.split(" ")) for x in f.readlines())
for i in range(len(node_list)-1):
    node_list[i][2] = node_list[i][2][:-1]
f.close()







@eel.expose #用decorator的方式，將JS要呼叫的PY function暴露給eel, 讓eel當作一個library  去給JS使用
def connect(IP):
    global CLIENT_COMMAND
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    is_connected = True
    client.send(("connect" + " " + node_host + " " + node_port).encode('utf-8'))
    #CLIENT_COMMAND = "connect"

def write_data():
    global node_list
    string = "\n".join(list(" ".join(x) for x in node_list))
    f = open("client_data.txt", "w")
    f.write(string)
    f.close()
    print("writing client_data")

def add_node(name, IP):
    global node_list
    f = open("client_data.txt", "w")
    node_list.append([name ,IP.split(" ")[0],IP.split(" ")[1]])
    write_data()



@eel.expose
def watering(IP, volume):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("watering"+" "+str(node_host)+" " +str(node_port) + " " + str(volume)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "WATER send success" in command:
                print(command)
                break
        except:
            pass

@eel.expose
def register(name, IP):
    print(IP)
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("register"+" "+str(node_host)+" " +str(node_port)).encode('utf-8'))
    add_node(name, IP)

    #CLIENT_COMMAND = "register"
@eel.expose
def transfer(IP):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    global CLIENT_COMMAND
    client.send(("transfer" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "get data" in command:
                current_data = command.split(" ")[2][:-1]
                need_water = command.split(" ")[2][-1]
                print("current data: ",data_transfer(current_data))
                return [data_transfer(current_data),need_water]
                break
        except:
            pass
    #CLIENT_COMMAND = "transfer"
@eel.expose
def exit():
    global CLIENT_COMMAND
    client.send(("exit").encode('utf-8'))
    #CLIENT_COMMAND = "exit"
@eel.expose
def predict(IP):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("predict" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "predict" in command:
                predict_data = command[8:]
                predict_data = time.ctime(float(predict_data))
                print("predict num: " + str(predict_data))
                return str(predict_data)
                break
        except:
            pass

@eel.expose
def auto_watering(IP, volume):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("set-auto" + " "+str(node_host) + " " + str(node_port)+" " + str(volume)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "auto success" in command:
                print("auto send success")
                break
        except:
            pass

@eel.expose
def set_cycle(IP, cycle):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("set-cycle" + " "+str(node_host) + " " + str(node_port) + " " + str(cycle)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "set-cycle success" in command:
                print("set-cycle send success")
                break
        except:
            pass
@eel.expose
def anti_auto_watering(IP):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("anti-auto" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "anti-auto success" in command:
                print("anti-auto send success")
                break
        except:
            pass

@eel.expose
def ask_auto(IP):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("ask-auto" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "auto true" in command:
                return "1"
                break
            elif "auto false" in command:
                return "0"
                break
        except:
            pass

@eel.expose
def last_interval(IP):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    client.send(("interval" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "interval" in command:
                interval_data = command.split(" ")[1]
                last_record = command.split(" ")[2]
                last_record = time.ctime(float(last_record))
                interval_data = str(datetime.timedelta(seconds=int(float(interval_data))))
                print("interval: " + interval_data)
                print("last record: " + last_record)
                return [interval_data,last_record]
                break
        except Exception as e:
            if ("Resource temporarily unavailable" not in str(e)):
                print(e)
@eel.expose
def sethighbound(IP):
    client.send(("sethighbound" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "sethighbound" in command:
                highbound = command.split(" ")[1]
                return highbound
                break
        except:
            pass
@eel.expose
def get_nodes():
    result = list(" ".join(x) for x in node_list)
    return result
@eel.expose
def getsequence(IP):
    node_host = IP.split(" ")[0]
    node_port = IP.split(" ")[1]
    global CLIENT_COMMAND
    client.send(("getsequence" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
    while(1):
        try:
            command = client.recv(1024).decode('utf-8')
            if "get sequence" in command:
                if((len(command.split(" "))>=3) & (command.split(" ")[2] != "")):
                    datas = command.split(" ")[2:]
                    highbound = int(float(datas[-1].split("?")[1]))
                    datas[-1] = datas[-1].split("?")[0]
                    print(datas)
                    print(highbound)
                    x = []
                    y = []
                    if datas[0] == "":
                        fig = plt.figure()
                        plt.plot_date([], [],linestyle="-", marker=".", color='b')
                        plt.axhline(y=highbound, color='r')
                        plt.gcf().autofmt_xdate()
                        fig.savefig("web/sequence.png")
                        time.sleep(0.01)
                    else:
                        for i in datas:
                            transferred = i[1:-1].split(",")
                            print(transferred)
                            temp = time.localtime(float(transferred[0]))
                            record_time = datetime.datetime(temp.tm_year, temp.tm_mon, temp.tm_mday, temp.tm_hour, temp.tm_min, temp.tm_sec)
                            x.append(record_time)
                            y.append(int(float(transferred[1])))
                        fig = plt.figure()
                        dates = matplotlib.dates.date2num(x)
                        temp_dates = matplotlib.dates.date2num([x[0],x[-1]])
                        plt.plot_date(dates, y,linestyle="-", marker=".", color='b')
                        plt.axhline(y=highbound, color='r')
                        plt.gcf().autofmt_xdate()
                        fig.savefig("web/sequence.png")
                        time.sleep(0.01)
                        print("data sequence: ", str(list( data_transfer(x) for x in datas)) )
                    return datas
                else:
                    fig = plt.figure()
                    plt.plot_date([], [],linestyle="-", marker=".", color='b')
                    highbound = float(command.split(" ")[3])
                    print("no recorded data")

                    return []
                break
        except Exception as e:
            if("Resource temporarily unavailable" not in str(e)):
                print(e)
eel.init('web') # eel.init(網頁的資料夾)
eel.start('main.html',size = (600,400)) #eel.start(html名稱, size=(起始大小))
    #CLIENT_COMMAND = "getsequence"
#try:
    #tty.setcbreak(sys.stdin.fileno())
"""
while(1):
    print(CLIENT_COMMAND)
    time.sleep(1)
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
        global CLIENT_COMMAND
        if CLIENT_COMMAND == "register":
            client.send(("register"+" "+str(node_host)+" " +str(node_port)).encode('utf-8'))
            CLIENT_COMMAND = "nothing"
        elif CLIENT_COMMAND == "transfer":
            client.send(("transfer" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
            CLIENT_COMMAND = "nothing"
        elif CLIENT_COMMAND == "getsequence":
            client.send(("getsequence" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
            CLIENT_COMMAND = "nothing"
        elif CLIENT_COMMAND == "exit":
            client.send(("exit").encode('utf-8'))
            CLIENT_COMMAND = "nothing"
        elif CLIENT_COMMAND == "connect":
            client.send(("connect" + " "+str(node_host) + " " + str(node_port)).encode('utf-8'))
            CLIENT_COMMAND = "nothing"
#finally:
    #termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
"""


        

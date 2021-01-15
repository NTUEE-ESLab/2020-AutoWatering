import pickle
import json
import socket
import random
import time
import rpi_server as rp
import numpy as np
from scipy.optimize import curve_fit

HOST = '192.168.43.32'  # The socket server's hostname or IP address
PORT = 65423        # The port used by the server


data = ''
common_cycle = 6*60*60
common_highbound = 750
connect = 0

clients = []
node_clients = []
get_permission = []
data_map = {}
node_client_map = {}
conn_addr_map = {}
client_state_map = {}
auto_list = []
cycle_map = {}
start_time_map = {}
volume_map ={}

filter_size = 10
random_range = 10000
max_size = 30

high_bound = 100


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(False)
s.bind((HOST, PORT))
s.listen()
start_time = time.time()

def tuple_transfer(a, b):
    print(type(b))
    temp = (a,b)
    print(temp)
    temp = str(temp)
    print(temp)
    temp = ''.join(temp.split(' '))
    return temp

def is_unwater(data, host):
    temp_high = 100
    for i in rp.member_list:
        if i._host == host:
            temp_high = i._high_bound
    if int(data) > temp_high:
        return True
    else:
        return False

def is_equal(addr_1, addr_2):
    if str(addr_1) == str(addr_2):
        return True
    else:
        return False

def string_to_tuple(string):
    return tuple(string[1:-1].split(","))

def fit_func(x, a, b):
        return a * x + b

def fit_func_inv(high_bound, a, b):
    return (high_bound - b)/a

def predict(data_array, high_bound):
    x = np.array([])
    y = np.array([])
    for i in data_array:
        x = np.append(x, np.float(i[0]))
        y = np.append(y, np.float(i[1]))
    print(x)
    print(y)

    if (y[-1] - y[-10] <= 100):
        print("can't predict")
        return([-1, -1, -1])

    params = curve_fit(fit_func, x[-10:-1], y[-10:-1])
    [a, b] = params[0]
    print([a, b])

    y_fit = []
    for i in x:
        y_fit.append(fit_func(i, a, b))
    x_p = fit_func_inv(high_bound, a , b)
    print(time.ctime(x[-1]))
    print(time.ctime(x_p))
    return([a, b, x_p])

while(1):
    try:
        client, addr = s.accept()
        print("Client address:" , addr)
        clients.append((client, addr))
        client.send("R".encode('utf-8'))
        client_state_map[client] = "floating"
        is_node = False
        for i in rp.member_list:
            if(is_equal(addr[0], i._host) & (is_equal(addr[1], i._client_port) == False)):
                node_clients.append((client, addr))
                cycle_map[str(addr[0])] = common_cycle
                start_time_map[str(addr[0])] = float(string_to_tuple(i._data_array[-1])[0])
                is_node = True
                node_client_map[client] = None
                conn_addr_map[client] = addr
                break
        if(is_node == True):
            clients.remove((client, addr))
            del client_state_map[client]
        print("node num:", len(node_clients))
        print("clients: ",clients)
        print("node clients: ", node_clients)
    except:
        pass
    for (conn, (host, port)) in clients:
        conn.setblocking(False)
        try:
            command = conn.recv(1024).decode('utf-8')
            if "register" in command: 
                node_host = command.split(" ")[1]
                node_port = command.split(" ")[2]
                if(len(rp.member_list) >= random_range*0.8):
                    random_range *= 10
                sequence = random.randint(0, random_range)
                for i in rp.member_list:
                    sequence_2 = i._id
                    while(sequence_2 == sequence):
                        sequence = random.randint(0, random_range)
                rp.register(sequence, node_host, node_port, host, port, max_size)
                for (node_conn, (_host, _port)) in clients:
                    if(is_equal(_host, node_host) & (is_equal(_port, port) == False)):
                        node_clients.append((node_conn, (_host, _port)))
                        cycle_map[str(_host)] = common_cycle
                        start_time_map[str(_host)] = time.time()
                        clients.remove((node_conn, (_host, _port)))
                        node_client_map[node_conn] = conn
                        conn_addr_map[node_conn] = (_host, _port)
                        print("transform success")
                        break
                print("register success")
            elif "connect" in command:
                print(command)
                certificate  = False
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin connecting")
                        print("Client Address: ",host, port)
                        print("Node Address: ", node_host, node_port)
                        print("clients: ",clients)
                        print("node clients: ", node_clients)
                        node_client_map[node_conn] = conn
                        data_map[node_conn] = ()
                        conn_addr_map[node_conn] = (node_host, node_port)
                        client_state_map[conn] = "floating"
                        print("setting link data success")
                        break
                if(certificate == False):
                    for i in rp.member_list:
                        if(is_equal(_host, i._host)):
                            conn.send("Node unconnected.".encode('utf-8'))
                            break
            elif "transfer" in command: 
                print("transfer mode")
                certificate  = False
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin transfer")
                        get_permission.append((node_conn, (node_host, node_port)))
                        client_state_map[conn] = "transfer"
                        node_conn.send("A".encode('utf-8'))
                        print("ACK send success")
                        break
            elif "getsequence" in command:
                print("sequence mode")
                certificate  = False
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin getsequence")
                        get_permission.append((node_conn, (node_host, node_port)))
                        client_state_map[conn] = "getsequence"
                        node_conn.send("A".encode('utf-8'))
                        break
            elif "exit" in command:
                conn.close()
                for i in node_client_map.keys():
                    if node_client_map[i] == conn:
                        node_client_map[i] = None
                del client_state_map[conn]
                clients.remove((conn, (host, port)))
            elif "predict" in command:
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                for i in rp.member_list:
                    if (is_equal(_host, i._host)):
                        _t_predict = predict(list(string_to_tuple(x) for x in i._data_array), int(float(i._high_bound)))[-1]
                        conn.send(("predict " + str(_t_predict)).encode('utf-8'))
            elif "sethighbound" in command:
                print("setHighBound mode")
                certificate  = False
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin setHighBound")
                        get_permission.append((node_conn, (node_host, node_port)))
                        client_state_map[conn] = "setHighBound"
                        node_conn.send("A".encode('utf-8'))
                        conn.send(("setHighBound success").encode(utf-8))
                        print("setHighBound success")
                        break
            elif "watering" in command:
                print("watering mode")
                certificate  = False
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                _volume = command.split(" ")[3]
                print("volume: "+_volume)
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        rp.add_checkpoint(node_host, time.time())
                        certificate = True
                        print("Begin watering")
                        #get_permission.append((node_conn, (node_host, node_port)))
                        #client_state_map[conn] = "watering"
                        node_conn.send((str(_volume)).encode('utf-8'))
                        conn.send("WATER send success".encode("utf-8"))
                        print(str(node_host) + "," + str(node_port)+","+str(_volume))
                        print("WATER send success")
                        break
            elif "interval" in command:
                print("interval mode")
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                for i in rp.member_list:
                    if(is_equal(_host, i._host)):
                        if((i._pwt[0] != 0) & (i._pwt[1] != 0)):
                            interval = i._pwt[0] - i._pwt[1]
                        else:
                            interval = 0
                        conn.send(("interval"+" "+str(interval) + " " + str(i._pwt[0])).encode('utf-8'))
                        print("interval send success")
            elif "set-auto" in command:
                print("auto mode")
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                _volume = command.split(" ")[3]                
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin auto")
                        auto_list.append(str(_host))
                        volume_map[str(_host)] = _volume
                        conn.send(("auto success").encode('utf-8'))
                        print("auto success")
                        print(auto_list)
                        break
            elif "anti-auto" in command:
                print("anti-auto mode")
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]                
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin anti-auto")
                        auto_list.remove(str(node_host))
                        conn.send(("anti-auto success").encode('utf-8'))
                        print("anti-auto success")
                        print(auto_list)
                        break
            elif "ask-auto" in command:
                print("ask auto mode")
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                print((_host,_port))
                if(str(_host) in auto_list):
                    conn.send("auto true".encode('utf-8'))
                    print("auto exist")
                else:
                    conn.send("auto false".encode('utf-8'))   
                    print("auto non-exist")
            elif "set-cycle" in command:
                print("set-cycle mode")
                _host = command.split(" ")[1]
                _port = command.split(" ")[2]
                cycle = command.split(" ")[3]
                for (node_conn, (node_host, node_port)) in node_clients:
                    if(is_equal(_host, node_host)):
                        certificate = True
                        print("Begin set-cycle")
                        cycle_map[str(node_host)] = int(float(cycle))
                        print("cycle: "+cycle)
                        conn.send(("set-cycle success").encode('utf-8'))
                        print("set-cycle success")
                        break






        except Exception as e:
            if ("Resource temporarily unavailable" not in str(e)):
                print(e)

    for (conn, (host, port)) in node_clients:
        conn.setblocking(False)
        try:
            warn = False
            command = conn.recv(1024).decode('utf-8')
            if((conn, (host, port)) in get_permission): 
                if ((command != '') & (command != "end")):
                    if("transfer" not in command):
                        print('Received from socket node client: ', command)
                        data_map[conn] = tuple(list(data_map[conn]) + [float(command)])
                elif command == "end":
                    print("end")
                    data = rp.filter(list(data_map[conn]))
                    temp_data = data
                    if(is_unwater(data, host)):
                        warn = True
                    data = tuple_transfer(time.time(), data)
                    data_array = rp.datas(conn_addr_map[conn])
                    data_map[conn] = ()
                    get_permission.remove((conn, (host, port)))
                    client_conn = node_client_map[conn]
                    if client_conn != None:
                        if client_state_map[client_conn] == "transfer":
                            if warn:
                                client_conn.send(("get data: "+str(data)+str(1)).encode('utf-8'))
                            else:
                                client_conn.send(("get data: "+str(data)+str(0)).encode('utf-8'))
                            print("transferring data success")
                            client_state_map[client_conn] = "floating"
                        elif client_state_map[client_conn] == "getsequence":
                            data_array = " ".join(data_array)
                            highbound = common_highbound
                            for i in rp.member_list:
                                if(is_equal(i._host,host)):
                                    highbound = i._high_bound
                                    break
                            client_conn.send(('get sequence: '+str(data_array) + "?"+str(highbound)).encode('utf-8'))
                            print("getsequence success")
                            client_state_map[client_conn] = "floating"
                        elif client_state_map[client_conn] == "setHighBound":
                            client_conn.send(("sethighbound: "+str(temp_data)).encode('utf-8'))
                            for i in rp.member_list:
                                if (is_equal(host, i._host)):
                                    rp.add_high_bound(host,temp_data)
                                    print("setHighBound success")
                                    break
                            client_state_map[client_conn] = "floating"
                        else:
                            print("routine writing")
                            if(str(host) in auto_list):
                                if warn:
                                    if str(host) in volume_map.keys():
                                        print("sss" + str(volume_map[str(host)]))
                                        conn.send((str(volume_map[str(host)])).encode('utf-8'))
                                    else:
                                        print("qqqqq")
                                        conn.send("1".encode('utf-8'))
                                    rp.add_checkpoint(host, time.time())
                            rp.add_member_data(conn_addr_map[conn], data)

                    else:
                        print("routine writing")
                        if(str(host) in auto_list):
                            if warn:
                                if str(host) in volume_map.keys():
                                    print("sss" + str(volume_map[str(host)]))
                                    conn.send((str(volume_map[str(host)])).encode('utf-8'))
                                else:
                                    print("qqqqq")
                                    conn.send("1".encode('utf-8'))
                                rp.add_checkpoint(host, time.time())
                        rp.add_member_data(conn_addr_map[conn], data)
                     
        except Exception as e:
            if ("Resource temporarily unavailable" not in str(e)):
                print(e)
    for (conn, (host, port)) in node_clients:
        current_time = time.time()
        if( (current_time - start_time_map[str(host)])>= cycle_map[str(host)]):
            print("Node Address: ", host, port)
            print("routine working")
            get_permission.append((conn, (host, port)))
            data_map[conn] = ()
            conn.send("A".encode('utf-8'))
            start_time_map[str(host)] = time.time()

            


    



    







            



import pickle
import json
import socket
import random
import time
import rpi_server as rp

HOST = '192.168.43.195'  # The socket server's hostname or IP address
PORT = 65423        # The port used by the server


data = ''
connect = 0

clients = []
node_clients = []
get_permission = []
data_map = {}
node_client_map = {}
conn_addr_map = {}
client_state_map = {}

filter_size = 10
random_range = 10000
max_size = 10

high_bound = 100


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(False)
s.bind((HOST, PORT))
s.listen()
start_time = time.time()

def tuple_transfer(a, b):
    temp = (a,b)
    temp = str(temp)
    temp = "".join(temp.split(" "))
    return temp

def is_unwater(data):
    if int(data) > high_bound:
        return True
    else:
        return False

def is_equal(addr_1, addr_2):
    if str(addr_1) == str(addr_2):
        return True
    else:
        return False
while(1):
    try:
        client, addr = s.accept()
        print("Client address:" , addr)
        clients.append((client, addr))
        client.send("R".encode('utf-8'))
        client_state_map[client] = "floating"
        is_node = False
        for i in rp.member_list:
            if(is_equal(addr[0], i._host)):
                node_clients.append((client, addr))
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
                rp.register(sequence, node_host, node_port, host, port,max_size)
                for (node_conn, (_host, _port)) in clients:
                    if(is_equal(_host, node_host)):
                        node_clients.append((node_conn, (_host, _port)))
                        clients.remove((node_conn, (_host, _port)))
                        print("transform success")
                        break
                print("register success")
                print(sequence)
            elif "connect" in command:
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
                        break
                if(certificate == False):
                    for i in member_list:
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
                        node_conn.send("ACK".encode('utf-8'))
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
                        node_conn.send("ACK".encode('utf-8'))
                        break
            elif "exit" in command:
                conn.close()
                for i in node_client_map.keys():
                    if node_client_map[i] == conn:
                        node_client_map[i] = None
                del client_state_map[conn]
                clients.remove((conn, (host, port)))
                


        except:
            pass

    for (conn, (host, port)) in node_clients:
        conn.setblocking(False)
        try:
            warn = False
            command = conn.recv(1024).decode('utf-8')
            if((conn, (host, port)) in get_permission): 
                if ((command != '') & (command != "end")):
                    if("transfer" not in command):
                        print('Received from socket node client: ', command)
                        data_map[conn] = tuple(list(data_map[conn]) + [command])
                elif command == "end":
                    print("end")
                    data = rp.filter(list(data_map[conn]))
                    warn = is_unwater(data)
                    data = tuple_transfer(time.time(), data)
                    data_array = rp.datas(conn_addr_map[conn])
                    data_map[conn] = ()
                    get_permission.remove((conn, (host, port)))
                    client_conn = node_client_map[conn]
                    if client_conn != None:
                        if(warn == True):
                            client_conn.send("need water".encode('utf-8'))
                            print(client_state_map[client_conn])
                        if client_state_map[client_conn] == "transfer":
                            client_conn.send(("get data: "+str(data)).encode('utf-8'))
                            print("transferring data success")
                            client_state_map[client_conn] = "floating"
                        elif client_state_map[client_conn] == "getsequence":
                            data_array = " ".join(data_array)
                            client_conn.send(("get sequence: "+str(data_array)).encode('utf-8'))
                            print("getsequence success")
                            client_state_map[client_conn] = "floating"
                        else:
                            print("routine writing")
                            rp.add_member_data(conn_addr_map[conn], data)

                    else:
                        print("routine writing")
                        rp.add_member_data(conn_addr_map[conn], data)
                     
        except:
            pass

    end_time = time.time()
    if((end_time - start_time) >= 10):
        for (conn, (host, port)) in node_clients:
            print("Node Address: ", host, port)
            print("routine working")
            get_permission.append((conn, (host, port)))
            data_map[conn] = ()
            conn.send("A".encode('utf-8'))
        start_time = time.time()

            


    



    







            



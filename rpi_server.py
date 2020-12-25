DRY_HIGHBOUND = 100
member_list = []
class member:
    def __init__(self, sequence, host, port, client_host, client_port,max_size):
        self._id = sequence
        self._host = host
        self._port = port
        self._data_max_size = max_size
        self._data_array = []
        self._client_host = client_host
        self._client_port = client_port
    def add_data(self, data):
        if(len(self._data_array)+1 <= self._data_max_size):
            self._data_array.append(data)
        else:
            self._data_array.pop(0)
            self._data_array.append(data)
    def add_multiple_data(self, datas):
        self._data_array = datas


def read_data():
    f = open("data.txt", "r")
    input_data = list(x[:-1] for x in f.readlines())
    input_data = list(x.split(' ') for x in input_data)
    for i in input_data:
        print(i)
    sequence = None
    host = None
    port = None
    max_size = None
    data_array = []
    for i in range(len(input_data)):
        if i % 2 == 0:
            sequence = int(input_data[i][0])
            host = input_data[i][1]
            port = input_data[i][2]
            client_host = input_data[i][3]
            client_port = input_data[i][4]
            max_size = int(input_data[i][5])
        else:
            member_list.append(member(sequence, host, port, client_host, client_port, max_size))
            for j in input_data[i]:
                if j != '':
                    add_member_data((host, port), j)
    f.close()
def write_data():
    f = open("data.txt", "w")
    string = ""
    for i in member_list:
        string = string +  (str(i._id) + " " + str(i._host) + " " + str(i._port) + " " + str(i._client_host) +" " + str(i._client_port) + " "+ str(i._data_max_size) + "\n")
        string = string +  (' '.join(str(x) for x in i._data_array)+"\n")
    string = string
    f.write(string)
    f.close()

def register(sequence, host, port, client_host, client_port, max_size):
    member_list.append(member(sequence, host, port, client_host, client_port, max_size))
    write_data()

def delete_member(sequence):
    for i in range(len(member_list)):
        if member_list[i]._id == sequence:
            del member_list[i]
            break
    write_data()

def filter(datas):
    data = sorted(datas)
    data = data[int(len(data)/2)]
    return data

def dry_monitor():
    record = []
    for i in member_list:
        if i.data_array[-1] >= DRY_HIGHBOUND:
            record.append(i)
    return record

def add_member_data(addr, data):
    index = -1
    for i in range(len(member_list)):
        if(str(member_list[i]._host) == str(addr[0])):
            index = i
            break
    member_list[index].add_data(data)
    write_data()
    return member_list[index]._data_array

def datas(addr):
    index = -1
    for i in range(len(member_list)):
        if(str(member_list[i]._host) == str(addr[0])) :
            index = i
            break
    return member_list[i]._data_array

def member_init():
    read_data()

def print_datas():
    string = ""
    for i in member_list:
        string = string +  (str(i._id) + " " + str(i._host) + " " + str(i._port) + " " + str(i._data_max_size) + "\n")
        string = string +  (' '.join(str(x) for x in i._data_array)+"\n")
    string = string
    print(string)


print('Get backend')
read_data()




    


     
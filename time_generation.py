import time
import datetime
import matplotlib
import matplotlib.pyplot as plt
import random
import math
import numpy as np


def generate_data_dist(interval, num, begin):
    begin_time = time.strptime(begin, "%m/%d/%Y, %H:%M:%S")
    begin_time_sec = time.mktime(begin_time)
    record_time = []
    for i in range(1,num):
        temp_time_sec = begin_time_sec + interval*i
        record_time.append(temp_time_sec)
    return record_time



def plot_time_random(record, low, high):
    list_of_datetimes = []
    values = []
    for i in record:
        temp = time.localtime(i)
        date_temp = datetime.datetime(temp.tm_year, temp.tm_mon, temp.tm_mday, temp.tm_hour, temp.tm_min)
        list_of_datetimes.append(date_temp)
    for i in range(len(list_of_datetimes)):
        values.append(random.randint(low, high))
    dates = matplotlib.dates.date2num(list_of_datetimes)
    plt.plot_date(dates, values)
    plt.gcf().autofmt_xdate()
    plt.show()

def plot_time_exp_decay(record, initial_value, last_value):
    list_of_datetimes = []
    values = []
    initial_base = 0
    initial_base = record[0]
    last_base = record[-1]
    interval = last_base - initial_base
    tau = -interval/np.log(last_value/initial_value)
    print("tau is ",tau)
    for i in range(len(record)):
        temp = time.localtime(record[i])
        temp_value = initial_value*np.exp((initial_base - record[i])/tau)
        if i > 0:
            delta =  random.randint(-10,10)
            while(temp_value+delta >= values[-1]):
                delta = random.randint(-10,10)
            temp_value += delta
        date_temp = datetime.datetime(temp.tm_year, temp.tm_mon, temp.tm_mday, temp.tm_hour, temp.tm_min)
        list_of_datetimes.append(date_temp)
        values.append(temp_value)
    dates = matplotlib.dates.date2num(list_of_datetimes)
    fig = plt.figure()
    plt.plot_date(dates, values)
    plt.gcf().autofmt_xdate()
    #plt.show()
    fig.savefig("web/test.png")
    new_record = []
    for i in range(len(record)):
        new_record.append((record[i],values[i]))
    print(new_record)

if __name__ == '__main__':
    hour = 3
    record = generate_data_dist(hour*60*60, 10, "12/25/2020, 14:57:52")
    print("plot begin")
    plot_time_exp_decay(record, 200, 80)
    print("plot end")





    




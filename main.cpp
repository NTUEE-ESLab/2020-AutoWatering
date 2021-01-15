/* WiFi Example
 * Copyright (c) 2018 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */



#include "mbed.h"
#include "TCPSocket.h"
#include <string.h>
//#include "TCPServer.h"


#define WIFI_IDW0XX1    2

#if (defined(TARGET_DISCO_L475VG_IOT01A) || defined(TARGET_DISCO_F413ZH))
#include "ISM43362Interface.h"
ISM43362Interface wifi(false);

#else // External WiFi modules

#if MBED_CONF_APP_WIFI_SHIELD == WIFI_IDW0XX1
#include "SpwfSAInterface.h"
SpwfSAInterface wifi(MBED_CONF_APP_WIFI_TX, MBED_CONF_APP_WIFI_RX);
#endif // MBED_CONF_APP_WIFI_SHIELD == WIFI_IDW0XX1

#endif

#define SCALE_MULTIPLIER    0.004

AnalogIn humid(A1);
DigitalOut CCVGOLTA(D5);

const char *sec2str(nsapi_security_t sec)
{
    switch (sec) {
        case NSAPI_SECURITY_NONE:
            return "None";
        case NSAPI_SECURITY_WEP:
            return "WEP";
        case NSAPI_SECURITY_WPA:
            return "WPA";
        case NSAPI_SECURITY_WPA2:
            return "WPA2";
        case NSAPI_SECURITY_WPA_WPA2:
            return "WPA/WPA2";
        case NSAPI_SECURITY_UNKNOWN:
        default:
            return "Unknown";
    }
}

void acc_server(NetworkInterface *net)
{
    TCPSocket socket;
    SocketAddress addr("192.168.43.32", 65423);
    SocketAddress addr_cli("192.168.43.21", 8787);
    nsapi_error_t response;

    char recv_buffer[1];
    char acc_json[64];

    // Open a socket on the network interface, and create a TCP connection to addr
    response = socket.open(net);
    if (0 != response){
        printf("Error opening: %d\n", response);
    }

    /*response = socket.bind("192.168.43.195:65431");
    if (0 != response){
        printf("Error binding: %d\n", response);
    }*/

    response = socket.connect(addr);
    if (0 != response){
        printf("Error connecting: %d\n", response);
    }


    socket.set_blocking(0);
    /*while (1){
        int data = humid*200;
        printf("%d\n", data);
        
        int len = sprintf(acc_json,"%d", data);

            
        response = socket.send(acc_json,len);
        if (0 >= response){
            printf("Error sending: %d\n", response);
        }
        ThisThread::sleep_for(500ms);
        sample_count ++;
        if (sample_count == 10){
            break;
        }

    }*/

    while (1){
        response = socket.recv(recv_buffer, 1);
        if (0 >= response){
            //printf("Error receiving: %d\n", response);
        }
        if (strcmp(recv_buffer, "R") == 0){
            printf("Get Request\n");
            memset(recv_buffer, 0, 1);
        }
        else if (strcmp(recv_buffer, "A") == 0){
            printf("Get ACK\n");
            char data_c[3];
            for (int i=0; i<10; i++){
                int data = humid * 800;
                sprintf(data_c, "%d", data);
                printf("data: %s\n", data_c);
                socket.send(data_c, 3);
                ThisThread::sleep_for(100ms);
                if (i == 9){
                    ThisThread::sleep_for(300ms);
                    socket.send("end", 3);
                    printf("End message sent\n");
                }
            }
            memset(recv_buffer, 0, 1);
        }
        else if ((strcmp(recv_buffer, "1") == 0)){
            printf("Water %s\n", recv_buffer);
            memset(recv_buffer, 0, 1);
            CCVGOLTA.write(1);
            ThisThread::sleep_for(2700ms);
            CCVGOLTA.write(0);
        }
        else if ((strcmp(recv_buffer, "2") == 0)){
            printf("Water %s\n", recv_buffer);
            memset(recv_buffer, 0, 1);
            CCVGOLTA.write(1);
            ThisThread::sleep_for(5400ms);
            CCVGOLTA.write(0);
        }
        else if ((strcmp(recv_buffer, "3") == 0)){
            printf("Water %s\n", recv_buffer);
            memset(recv_buffer, 0, 1);
            CCVGOLTA.write(1);
            ThisThread::sleep_for(8100ms);
            CCVGOLTA.write(0);
        }
        else if ((strcmp(recv_buffer, "4") == 0)){
            printf("Water %s\n", recv_buffer);
            memset(recv_buffer, 0, 1);
            CCVGOLTA.write(1);
            ThisThread::sleep_for(10800ms);
            CCVGOLTA.write(0);
        }
        else{
            memset(recv_buffer, 0, 1);
        }
        ThisThread::sleep_for(50ms);
    }

 
    socket.close();
}

int main()
{


    printf("\nConnecting to %s...\n", MBED_CONF_APP_WIFI_SSID);
    //wifi.set_network("192.168.130.105","255.255.255.0","192.168.130.254");
    int ret = wifi.connect(MBED_CONF_APP_WIFI_SSID, MBED_CONF_APP_WIFI_PASSWORD, NSAPI_SECURITY_WPA_WPA2);
    if (ret != 0) {
        printf("\nConnection error\n");
        return -1;
    }

    printf("Success\n\n");
    printf("MAC: %s\n", wifi.get_mac_address());
    printf("IP: %s\n", wifi.get_ip_address());
    printf("Netmask: %s\n", wifi.get_netmask());
    printf("Gateway: %s\n", wifi.get_gateway());
    printf("RSSI: %d\n\n", wifi.get_rssi());  


    acc_server(&wifi);

}
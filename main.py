import socket
import struct
import time
import datetime

NTP_server = '0.ru.pool.ntp.org'
DIFF1900_1970 = 2208988800  # seconds since 1 January 1900
SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
NTP_EPOCH = datetime.date(1900, 1, 1)
NTP_DELTA = (SYSTEM_EPOCH - NTP_EPOCH).days * 24 * 3600
PACKET_FORMAT = "!B B B b 11I"


def ntp_to_system_time(date):
    """convert a NTP time to system time"""
    return date - NTP_DELTA


def system_to_ntp_time(date):
    """convert a system time to a NTP time"""
    return date + NTP_DELTA


def sntp_query(tr_time, version=4, mode=3):
    packed = struct.pack(PACKET_FORMAT,
                         (0 << 6 | version << 3 | mode), 0, 0, 0,
                         0, 0, 0, 0,
                         0, 0, 0, 0,
                         0,
                         int(tr_time),
                         int(abs(tr_time - int(tr_time)) * 2 ** 32)
                         )
    return packed


def sntp_get_time(iterations):
    deltas = []
    server_time = 0
    for i in range(iterations):
        #print(i)
        time.sleep(1)
        connect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = sntp_query(system_to_ntp_time(time.time()))
        connect.sendto(message, (NTP_server, 123))

        # build the destination timestamp
        answer = connect.recvfrom(1024)  # вернет пару (data, address)
        #server_time = 0
        dest_timestamp = time.time()
        if answer[0]:
            #print('Received from: ', answer[1])
            unpacked = struct.unpack(PACKET_FORMAT,
                                     answer[0][0:struct.calcsize(PACKET_FORMAT)])
            orig_time = ntp_to_system_time(unpacked[9] + float(unpacked[10]) / 2 ** 32)
            recv_timestamp = ntp_to_system_time(unpacked[11] + float(unpacked[12]) / 2 ** 32)
            tx_timestamp = ntp_to_system_time(unpacked[13] + float(unpacked[14]) / 2 ** 32)
            #print('Originate timestamp:', datetime.datetime.fromtimestamp(orig_time))
            #print("Receive timestamp:", datetime.datetime.fromtimestamp(recv_timestamp))
            #print('Transmit timestamp:', datetime.datetime.fromtimestamp(tx_timestamp))
            #print('Destination timestamp:', datetime.datetime.fromtimestamp(dest_timestamp))
            delta = ((dest_timestamp - orig_time) - (tx_timestamp - recv_timestamp)) / 2.0
            deltas.append(delta)
            server_time = tx_timestamp
            curr_time = tx_timestamp + delta
            #print('Correct time according to server:', datetime.datetime.fromtimestamp(curr_time))
    #print(deltas)
    average_delta = sum(deltas)/len(deltas)
    curr_time = server_time + average_delta
    print('Correct time: ', datetime.datetime.fromtimestamp(curr_time))


sntp_get_time(3)

import logging
from time import sleep
import datetime
import sys
import struct
import socket


def parse_packet(pkt):
    b0 = pkt[0]
    li = (b0 >> 6) & 3
    vn = (b0 >> 3) & 7
    mode = b0 & 7
    stratum = pkt[1]
    poll = pkt[2]
    precision = struct.unpack('!b', pkt[3:4])[0]
    root_delay = struct.unpack('!i', pkt[4:8])[0] / 2**16
    root_disp = struct.unpack('!i', pkt[8:12])[0] / 2**16
    ref_id = pkt[12:16].decode('ascii', errors='replace')
    ref_sec, ref_frac = struct.unpack('!II', pkt[16:24])
    orig_sec, orig_frac = struct.unpack('!II', pkt[24:32])
    recv_sec, recv_frac = struct.unpack('!II', pkt[32:40])
    xmit_sec, xmit_frac = struct.unpack('!II', pkt[40:48])

    ref_time = ref_sec - 2208988800 + ref_frac / 2**32 if ref_sec else 0
    orig_time = orig_sec - 2208988800 + orig_frac / 2**32 if orig_sec else 0
    recv_time = recv_sec - 2208988800 + recv_frac / 2**32 if recv_sec else 0
    xmit_time = xmit_sec - 2208988800 + xmit_frac / 2**32 if xmit_sec else 0
    
    return [b0, li, vn, mode, stratum, poll, precision, root_delay, root_disp, ref_id,
            ref_sec, orig_sec, recv_sec, xmit_sec, ref_time, orig_time, recv_time, xmit_time ]



def log_ntp_client(address):
    currentDt = datetime.datetime.now()
    f = currentDt.strftime("%Y%m%d%H%M%S") + ".ntplog"
    logger = logging.getLogger(f)
    
    logging.basicConfig(format="%(asctime)s %(message)s", filename=f, encoding="utf-8", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("ntp").setLevel(logging.DEBUG)

    logger.debug("Starting ntp log...")
    #ntp = NtpArena(addresses=[address])
    
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    ntp_request = b'\x1b' + 47 * b'\0'
    #print(ntp_request)
    while True:
        
        sock.sendto(ntp_request, (address, 123))
        response = sock.recv(48)

        logger.info(parse_packet(response))
        
        sleep(10)




 
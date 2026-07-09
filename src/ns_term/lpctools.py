import serial
from serial import Serial
import time
from typing import Tuple

SYNCHRO_START = b"?"
SYNCHRO =  b"Synchronized\r\n"
SYNCHRO_OK = b"OK\r\n"
DATA_BLOCK_OK = b"OK\r\n"
DATA_BLOCK_RESEND = b"RESEND\r\n"
SYNCHRO_ECHO_OFF = b"A 0\r\n"
#ISP_ABORT = ""  /* Not handled */
UNLOCK = b"U 23130\r\n"
READ_UID = b"N\r\n"
READ_PART_ID = b"J\r\n"
READ_BOOT_VERSION = b"K\r\n"



serial_fd : Serial = None


def isp_open(baudrate:int, serial_device: str | None = None) -> int:
    global serial_fd
    if serial_device == None:
        print("no serial device given")
        return -2
    
    try:
        serial_fd = serial.Serial(serial_device, baudrate, timeout=0.1)
    except Exception as e:
        raise e
    
    return 0

def isp_close():
    global serial_fd
    if serial_fd:
        serial_fd.close()
        serial_fd = None

def isp_write(buf: bytes, buf_size: int) -> int:
    '''returns n written'''
    global serial_fd
    try:
        return serial_fd.write(buf)
    except TimeoutError:
        pass
    


def isp_empty_buffer():
    
    while(unused != b"\r" and unused != b"\n"):
        try:
            unused = serial_fd.read(1)
        except TimeoutError:
            break
        
    

def isp_read(buf_size: int) -> Tuple[bytes, int]:
            
    try:
        data = serial_fd.read(buf_size)

    except TimeoutError:
        print("timed out")
        return data, len(data)
        
    return data, len(data)


def test():
    
    isp_open(115200, "/dev/ttyUSB0")
    
    if (isp_write(READ_UID, len(READ_UID)) != len(READ_UID)):
        print("unable to send READ_UID")
        return -5
    rsp, nb = isp_read( len(READ_UID))
    if (nb == 0):
        print("error reading sync answer")
        return -4

    print("buf: ", rsp.decode("utf-8", errors="ignore"))
    
    
test()

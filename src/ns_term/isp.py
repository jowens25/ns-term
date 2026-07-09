import serial
from serial import Serial
import time

SYNCHRO_START = "?"
SYNCHRO =  b"Synchronized\r\n"
SYNCHRO_OK = "OK\r\n"
DATA_BLOCK_OK = "OK\r\n"
DATA_BLOCK_RESEND = "RESEND\r\n"
SYNCHRO_ECHO_OFF = "A 0\r\n"
#ISP_ABORT = ""  /* Not handled */
UNLOCK = "U 23130\r\n"
READ_UID = "N\r\n"
READ_PART_ID = "J\r\n"
READ_BOOT_VERSION = "K\r\n"

error_codes = {
    "0": "CMD_SUCCESS",
	"1":"INVALID_COMMAND",
	"2":"SRC_ADDR_ERROR",
	"3":"DST_ADDR_ERROR",
	"4":"SRC_ADDR_NOT_MAPPED",
	"5":"DST_ADDR_NOT_MAPPED",
	"6":"COUNT_ERROR",
	"7":"INVALID_SECTOR",
	"8":"SECTOR_NOT_BLANK",
	"9":"SECTOR_NOT_PREPARED_FOR_WRITE_OPERATION",
	"10":"COMPARE_ERROR",
	"11":"BUSY",
	"12":"PARAM_ERROR",
	"13":"ADDR_ERROR",
	"14":"ADDR_NOT_MAPPED",
	"15":"CMD_LOCKED",
	"16":"INVALID_CODE",
	"17":"INVALID_BAUD_RATE",
	"18":"INVALID_STOP_BIT",
	"19":"CODE_READ_PROTECTION_ENABLED"}




def isp_read(s: Serial, len: int) -> str:
    rsp = s.read(len).decode("utf-8", errors="ignore")
    print(f"reading {len} : {rsp}")
    return rsp

    
def isp_write(s: Serial, msg: str):
    print(f"writing {msg}")

    return s.write(msg.encode("utf-8", errors="ignore"))
    
    
    

def isp_ret_code(code: str, verbose: bool) -> int:
    
    code = code.strip("\r\n")
    
    try:
        ret = int(code)
        if verbose:
            print(f"Received error code: {ret}: {error_codes.get(code)}")
        return ret
    except ValueError as e:
        print(e)
        return -1
    
def isp_empty_buffer(s: Serial):
    
   s.read_until(b"\r")
            
def str_len(msg: str) -> int: 
    return len(msg.strip("\r\n"))

def isp_connect(crystal_freq:int = 12000, verbose:bool = False) -> int:
    
    dev = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
    
    # send sync request
    if isp_write(dev, SYNCHRO_START) != len(SYNCHRO_START):
        print("unable to send sync request")
        return -5
    
    # wait for answer
    rsp = isp_read(dev, len(SYNCHRO))
    
    # check answer, and ack if ok
    if rsp == SYNCHRO:
        
        isp_write(dev, SYNCHRO)
    else:
        
        print("unable to syncronize, no synchro received")
        
        return -3
    
    # empty read buffer (echo is on)
    isp_empty_buffer(dev)

    # read reply (OK)
    rsp = isp_read(dev, len(SYNCHRO_OK))
    
    if rsp != SYNCHRO_OK:
        print("unable to synchronize, synchro not acknowledged")
        return -2
    
    # docs says we should send xtal .. send anything is ok
    isp_write(dev, str(crystal_freq)+"\r\n")
    
    # empty read buffer (echo is on)
    
    isp_empty_buffer(dev)

    # read reply (OK)
    rsp = isp_read(dev, len(SYNCHRO_OK))
    
    if rsp != SYNCHRO_OK:
        print("Unable to synchronize, crystal frequency not acknowledged")
        return -2
    
    # turn off echo
    isp_write(dev, SYNCHRO_ECHO_OFF)
    
    # empty read buffer (echo still on)
    isp_empty_buffer(dev)
    
    rsp = isp_read(dev, 3)
    
    print(rsp)
    
    print(isp_ret_code(rsp, True))
    
    print("Device session openned")
    
    return 0
        

def isp_send_cmd_no_args(dev: Serial, cmd: str) -> int:
    
    if isp_write(dev, cmd) != len(cmd):
        print(f"unable to send {cmd}")
        return -5
    
    time.sleep(0.005)
    
    rsp = isp_read(dev, 3)
    
    return isp_ret_code(rsp, True)

def isp_cmd_part_id(dev: Serial):
    
    ret = isp_send_cmd_no_args(dev, READ_PART_ID)
    if ret != 0:
        print("read part id error")
        return ret
    rsp = isp_read(dev, 15)
    
    part_id = int(rsp)
    print(f"address_range_low: { part_id:#010x}")

    

def test():

    dev = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

    isp_cmd_part_id(dev)
    
    
test()
import serial
from serial import Serial


serial_fd : Serial | None = None

def isp_serial_open(baudrate: int, serial_device: str) -> int:
    global serial_fd
    if len(serial_device) <= 0:
        print("no serial device given")
        return -2
    
    serial_fd = serial.Serial(serial_device, baudrate, timeout=0.1)
    
    if not serial_fd.is_open:
        print("unable to open port")
        serial_fd = None
        return -1
    
    return 0


def isp_serial_close():
    global serial_fd
    
    if serial_fd:
        serial_fd.close()
    serial_fd = None
    
    
def isp_serial_write(buf: str) -> int:
    global serial_fd
    return serial_fd.write(buf.encode("utf-8", errors="ignore"))


next_read_char = b""
def isp_serial_empty_buffer():
    global serial_fd, next_read_char
    
    unused = b""
    
    while (unused != b"\r" and unused !=b"\n"):
        
        try:
            unused = serial_fd.read(1)
        except TimeoutError:
            break
        if len(unused) == 0:
            print("eof")
            return
        
    if unused == b"\r":
        unused = serial_fd.read(1)
        
    if unused == b"\n":
        return
    
    next_read_char = unused
    
def isp_serial_read(min_read: int):
    global next_read_char
    
    rsp = b""
    
    if next_read_char != b"":
        rsp += next_read_char
        next_read_char = b""
    
    try:
        data = serial_fd.read(min_read)
    except TimeoutError:
        return
    
    
    return data, len(data)




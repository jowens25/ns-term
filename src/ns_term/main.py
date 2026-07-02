import importlib.metadata

import typer
import serial.tools.list_ports
from serial import Serial

import sys
app = typer.Typer()



@app.command()
def version():
    typer.echo(importlib.metadata.version("ns-term"))



@app.command()
def ports():
    for port in sorted(serial.tools.list_ports.comports()):

        if port.description != "n/a":
            print(port.device)


@app.command()
def listen(_port, _baud):

    ser = serial.Serial(_port, baudrate=_baud, timeout=1)

    while(True):
        print(ser.readline().decode(encoding="utf-8", errors="ignore"), end="")


def read_reg(ser: Serial, addr: int, data: list[int]) -> str:
    write_data = ""
    write_data += "$RC,"
    write_data += f"{addr:#010x}"

    cs = 0
    for a in write_data:
        if a != "$":
            cs = cs ^ ord(a)
    write_data += "*"
    write_data += f"{cs:02x}"
    write_data += "\r\n"

    #print(f"write data: {write_data}")

    ser.write(write_data.encode(encoding="utf-8", errors="ignore"))

    rsp = ser.readline().decode(encoding="utf-8", errors="ignore")

    if rsp:
        if rsp.startswith("$RR"):
            data[0] = int(rsp.split("*")[0].split(",")[2], 16)
            return 0
        else:
            return -1


Ucm_Config_BlockSize = 16
Ucm_Config_TypeInstanceReg = 0x00000000
Ucm_Config_BaseAddrLReg =                          0x00000004
Ucm_Config_BaseAddrHReg =                          0x00000008
Ucm_Config_IrqMaskReg =                            0x0000000C
Ucm_CoreConfig_ConfSlaveCoreType = 1

def read_cores(ser):

    temp_data = [0]

    for i in range(255):
        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_TypeInstanceReg)), temp_data)):

            if ((i == 0) and ((((temp_data[0] >> 16) & 0x0000FFFF) != Ucm_CoreConfig_ConfSlaveCoreType) or (((temp_data[0] >> 0) & 0x0000FFFF) != 1))):
                print("ERROR: not a conf block at the address expected")
                break
                
            elif (temp_data[0] == 0):
                break
            else:
                print(f"core_type: { ((temp_data[0] >> 16) & 0x0000FFFF)}")
                print(f"core_instance_nr: { ((temp_data[0] >> 0) & 0x0000FFFF)}")

        else:
            break


        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_BaseAddrLReg)), temp_data)):
        
            print(f"address_range_low: { temp_data[0]:#010x}")
        
        else:
        
            break
            

        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_BaseAddrHReg)), temp_data)):
            print(f"address_range_high: {temp_data[0]:#010x}")
        else:
            break
            

        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_IrqMaskReg)), temp_data)):
            print(f"interrupt_mask: { temp_data[0]:#010x}")
        else:
            break
                            



@app.command()
def cores(port, baud):

    ser = serial.Serial(port, baudrate=baud, timeout=1)

    ser.write("$CC\r\n".encode(encoding="utf-8", errors="ignore"))

    print(ser.readline())

    read_cores(ser)


@app.command()
def hello():
    """
    hello
    """
    print("Hello world!")


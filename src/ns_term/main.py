import importlib.metadata

import typer
import serial.tools.list_ports
from serial import Serial

import sys
app = typer.Typer()



NtpClientRegisters = {
    "AddressLow": 0x00000000,
"ControlReg":                        0x00000000,
"StatusReg":                         0x00000004,
"VersionReg":                        0x0000000C,
"CountControlReg":                   0x00000010,
"CountReqReg":                       0x00000014,
"CountRespReg":                      0x00000018,
"CountRespMissedReg":                0x0000001C,
"ConfigControlReg":                  0x00000080,
"ConfigModeReg":                     0x00000084,
"ConfigVlanReg":                     0x00000088,
"ConfigMac1Reg":                     0x0000008C,
"ConfigMac2Reg":                     0x00000090,
"ConfigIpReg":                       0x00000094,
"ConfigIpv61Reg":                    0x00000098,
"ConfigIpv62Reg":                    0x0000009C,
"ConfigIpv63Reg":                    0x000000A0,
"ConfigServerMac1Reg":               0x000000A4,
"ConfigServerMac2Reg":               0x000000A8,
"ConfigServerIpReg":                 0x000000AC,
"ConfigServerIpv61Reg":              0x000000B0,
"ConfigServerIpv62Reg":              0x000000B4,
"ConfigServerIpv63Reg":              0x000000B8,
"ConfigSubnetMaskReg":               0x000000BC,
"ConfigSubnetMaskv61Reg":            0x000000C0,
"ConfigSubnetMaskv62Reg":            0x000000C4,
"ConfigSubnetMaskv63Reg":            0x000000C8,
"ConfigGatewayIpReg":                0x000000CC,
"ConfigGatewayIpv61Reg":             0x000000D0,
"ConfigGatewayIpv62Reg":             0x000000D4,
"ConfigGatewayIpv63Reg":             0x000000D8,
"ConfigFilterCoefB0Reg":             0x000000DC,
"ConfigFilterCoefB1Reg":             0x000000E0,
"ConfigFilterCoefB2Reg":             0x000000E4,
"ConfigFilterCoefA1Reg":             0x000000E8,
"ConfigFilterCoefA2Reg":             0x000000EC,
"ConfigPiFactorPReg":                0x000000F0,
"ConfigPiFactorIReg":                0x000000F4,
"UtcInfoControlReg":                 0x00000100,
"UtcInfoReg":                        0x00000104,
"OffsetFromServerReg":               0x00000200,
"MeanRoundtripDelayReg":             0x00000204,
}


CoreTypes = {
1: "ConfSlave",                
2: "ClkClock",                 
3: "ClkSignalGenerator",       
4: "ClkSignalTimestamper",     
5: "IrigSlave",                
6: "IrigMaster",               
7: "PpsSlave",                 
8: "PpsMaster",                
9: "PtpOrdinaryClock",         
10: "PtpTransparentClock",      
11: "PtpHybridClock",           
12: "RedHsrPrp",                
13: "RtcSlave",                 
14: "RtcMaster",                
15: "TodSlave",                 
16: "TodMaster",                
17: "TapSlave",                 
18: "DcfSlave",                 
19: "DcfMaster",                
20: "RedTsn",                   
21: "TsnIic",                   
22: "NtpServer",                
23: "NtpClient",                
25: "ClkFrequencyGenerator",    
26: "SynceNode",                
27: "PpsClkToPps",              
28: "PtpServer",                
29: "PtpClient",                
30: "ClkDynamicControl",        
10000: "PhyConfiguration",         
10001: "I2cConfiguration",         
10002: "IoConfiguration",          
10003: "EthernetTestplat",         
10004: "MinSwitch",                
10005: "Eeprom",                   
10006: "Mux",                      
20000: "ConfExt",                  
}




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

NtpServerRegisters = {
    "AddressLow": 0x00000000,
    "ControlReg":                        0x00000000,
    "StatusReg":                         0x00000004,
    "VersionReg":                        0x0000000C,
    "CountControlReg":                   0x00000010,
    "CountReqReg":                       0x00000014,
    "CountRespReg":                      0x00000018,
    "CountReqDroppedReg":                0x0000001C,
    "CountBroadcastReg":                 0x00000020,
    "ConfigControlReg":                  0x00000080,
    "ConfigModeReg":                     0x00000084,
    "ConfigVlanReg":                     0x00000088,
    "ConfigMac1Reg":                     0x0000008C,
    "ConfigMac2Reg":                     0x00000090,
    "ConfigIpReg":                       0x00000094,
    "ConfigIpv61Reg":                    0x00000098,
    "ConfigIpv62Reg":                    0x0000009C,
    "ConfigIpv63Reg":                    0x000000A0,
    "ConfigReferenceIdReg":              0x000000A4,
    "UtcInfoControlReg":                 0x00000100,
    "UtcInfoReg":                        0x00000104,
}

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
                core_type = ((temp_data[0] >> 16) & 0x0000FFFF)
                print(f"Core type: { CoreTypes[core_type]}")
                #print(f"core_instance_nr: { ((temp_data[0] >> 0) & 0x0000FFFF)}")

        else:
            break


        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_BaseAddrLReg)), temp_data)):
        

            addr_low = temp_data[0]
            print(f"address_range_low: { temp_data[0]:#010x}")

            match CoreTypes[core_type]:
                case "NtpClient":
                    NtpClientRegisters["AddressLow"] = addr_low
                    
                case _:
                    print("default case")
        
        else:
        
            break
            

        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_BaseAddrHReg)), temp_data)):
            pass
            #print(f"address_range_high: {temp_data[0]:#010x}")
        else:
            break
            

        if (0 == read_reg(ser, (0x00000000 + ((i * Ucm_Config_BlockSize) + Ucm_Config_IrqMaskReg)), temp_data)):
            pass
            #print(f"interrupt_mask: { temp_data[0]:#010x}")
        else:
            break
                            



@app.command()
def cores(port, baud):

    ser = serial.Serial(port, baudrate=baud, timeout=1)

    ser.write("$CC\r\n".encode(encoding="utf-8", errors="ignore"))

    print(ser.readline())

    read_cores(ser)


    # for k,v in NtpClientRegisters.items():
    #     temp_data = [0]
        
    #     if k != "AddressLow":
    #         addr = NtpClientRegisters["AddressLow"]+v
    #         if (0 == read_reg(ser, addr, temp_data)):
    #             print(f"Address:{addr:#010x} Data: {temp_data[0]:#010x} Name:{k}")


@app.command()
def hello():
    """
    hello
    """
    print("Hello world!")


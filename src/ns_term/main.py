import importlib.metadata
from time import sleep

import typer
import serial.tools.list_ports
from serial import Serial
from typing import Annotated
from ns_term.ptp import parse_ptp_header
from ns_term.ser import log_serial



app = typer.Typer()



@app.command()
def version():
    typer.echo(importlib.metadata.version("ns-term"))



@app.command()
def ports():
    for port in sorted(serial.tools.list_ports.comports()):

        if port.description != "n/a":
            print(port.device)


from ns_term.mylogger import log_ntp_client, parse_ntp_packet

@app.command()
def log(log_type, 
        _addr: Annotated[str, typer.Argument()] = None, 
        _sleepfor: Annotated[float, typer.Argument()] = 1.0,
        _port: Annotated[str, typer.Argument()] = None, 
        _baud: Annotated[int, typer.Argument()] = None):
    if log_type == "serial":
        if _port is not None and _baud is not None:
            log_serial(_port, _baud)
        else:
            print("must supply port and baud")
    elif log_type == "ntp":
        if _addr != None and _sleepfor != None:
            log_ntp_client(_addr, _sleepfor)
        else:
            print("need addr")
        
        
import socket
import select
@app.command()
def ptp_test(_addr: Annotated[str, typer.Argument()] = None):
    print("PTP TEST STARTED...")
    print("CTRL+C to stop")
    if _addr:
        print(f"Pinging {_addr}")

        PTP_EVENT_PORT = 319
        PTP_GENERAL_PORT = 320
        MULTICAST_GROUP = "224.0.1.129"

        sockets = []
        try:
            # Set up socket for both ports
            for port in [PTP_EVENT_PORT, PTP_GENERAL_PORT]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))

                # Join multicast group
                mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

                sockets.append(sock)
                print(f"Listening on port {port}")

            # Monitor both sockets concurrently
            while True:
                # select blocks until one of your sockets receives data
                readable, _, _ = select.select(sockets, [], [])

                for ready_sock in readable:
                    data, addr = ready_sock.recvfrom(1024)
                    # Identify which port the packet hit by querying the socket
                    local_port = ready_sock.getsockname()[1]

                    print(f"\n[Port {local_port}] RX from {addr}:")
                    try:
                        parsed = parse_ptp_header(data)
                        print(parsed)
                    except Exception as e:
                        print(f"Failed to parse PTP header: {e} | Raw Data: {data.hex()}")

        except KeyboardInterrupt:
            print("\nStopping and closing sockets...")
        finally:
            for sock in sockets:
                sock.close()
        
        
    else:
        print("Missing Master IP") 
    
@app.command()
def ntp_test(_addr: Annotated[str, typer.Argument()] = None):
    print("PTP TEST STARTED...")
    print("CTRL+C to stop")
    if _addr:
        print(f"Pinging {_addr}")
    
    
    try:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
        sock.settimeout(1.0) # 1 sec timeout
        ntp_request = b'\x1b' + 47 * b'\0'
        while True:
            print("sent")
            try:
                sock.sendto(ntp_request, (_addr, 123))
                response = sock.recv(48)
                
                print(parse_ntp_packet(response))
            except TimeoutError:
                print("No response rececived... timeout")
            
            except Exception as e:
                print(e)
            
            
            sleep(1)

            
    except KeyboardInterrupt:
        print("\nStopping and closing socket...")
    finally:
        sock.close()
    


@app.command()
def listen(_port, _baud):

    ser = serial.Serial(_port, baudrate=_baud, timeout=1)

    while(True):
        print(ser.readline().decode(encoding="utf-8", errors="ignore"), end="")




@app.command()
def hello():
    """
    hello
    """
    print("Hello world!")


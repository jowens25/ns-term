import asyncio
import importlib.metadata
from time import sleep

import typer
import serial.tools.list_ports
from serial import Serial
from typing import Annotated, Optional
from ns_term.mylogger import parse_ntp_packet
from ns_term.ptp import parse_ptp_header
from ns_term.ser import log_serial, serial_session



app = typer.Typer()



@app.command()
def version():
    typer.echo(importlib.metadata.version("ns-term"))

        
import select
import socket

@app.command()
def ptp_test(_addr: Annotated[Optional[str], typer.Argument()] = None):
    """PTP function test"""
    print("PTP TEST STARTED...")
    print("CTRL+C to stop")
    if not _addr:
        print("Missing Master IP")
        return

    PTP_PORTS = [319, 320]
    MULTICAST_GROUP = "224.0.1.129"

    # Find the local interface IP used to reach the master
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect((_addr, 319))   # UDP connect sends nothing
        local_ip = probe.getsockname()[0]
    finally:
        probe.close()
    print(f"Pinging {_addr} via local interface {local_ip}")

    sockets = []
    try:
        for port in PTP_PORTS:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", port))

            mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton(local_ip)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            sockets.append(sock)
            print(f"Listening on port {port}")

        while True:
            readable, _, _ = select.select(sockets, [], [], 1.0)  # timeout here
            if not readable:
                continue  # lets Ctrl+C get through on Windows

            for ready_sock in readable:
                data, addr = ready_sock.recvfrom(1024)
                local_port = ready_sock.getsockname()[1]

                if addr[0] != _addr:
                    continue

                print(f"\n[Port {local_port}] RX from {addr}:")
                try:
                    print(parse_ptp_header(data))
                except Exception as e:
                    print(f"Failed to parse PTP header: {e} | Raw Data: {data.hex()}")

    except KeyboardInterrupt:
        print("\nStopping and closing sockets...")
    finally:
        for sock in sockets:
            sock.close()
    
@app.command()
def ntp_test(_addr: Annotated[str, typer.Argument()] = None):
    """NTP function test"""
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
def open(_port: Annotated[str, typer.Argument()] = None, _baud: Annotated[str, typer.Argument()] = None):
    """Open a serial port and read out data
        Commands prefixed with $ will be appended with <CR><LN>
        Commands prefixed with # will be ran as scripts
        """

    asyncio.run(serial_session(_port, _baud))
    
    
import serial.tools.list_ports    
@app.command()
def ports():
    
    ports = serial.tools.list_ports.comports()

    for port in sorted(ports):
        print(f"{port.device} {port.description} {port.hwid}")
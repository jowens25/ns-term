import importlib.metadata

import typer
import serial.tools.list_ports

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


@app.command()
def hello():
    """
    hello
    """
    print("Hello world!")


import asyncio
import serial_asyncio

import aioconsole
from aioconsole import ainput
import datetime, logging, sys



async def main_serial(_port, _baud):
    global serial_logger
    global serial_reader
    global serial_writer
    
    currentDt = datetime.datetime.now()
    f = currentDt.strftime("%Y%m%d%H%M%S") + ".seriallog"
    serial_logger = logging.getLogger(f)

    logging.basicConfig(format="%(asctime)s %(message)s", filename=f, encoding="utf-8", level=logging.DEBUG)
    serial_logger.addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger("ntp").setLevel(logging.DEBUG)

    
    serial_reader, serial_writer = await serial_asyncio.open_serial_connection(url=_port, baudrate=_baud) 
    
    
    async def read_loop():
        while True:
            line = await serial_reader.readline()
            serial_logger.info(line.decode(encoding="utf-8", errors="ignore").strip("\r\n"))
            
    
    async def write_loop():
        while True:
            msg = await ainput()
            serial_logger.info(msg)
            serial_writer.write(msg.encode(encoding="utf-8", errors="ignore")+b"\r\n")
            await serial_writer.drain()
            
            
            
    await asyncio.gather(read_loop(), write_loop())

    


def log_serial(p, b):
    
    asyncio.run(main_serial(p, b))
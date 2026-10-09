import asyncio
import serial_asyncio
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout


async def read_loop(reader, writer):
    
    try:
        while True: 
            line = await reader.readline()
            print(line.decode(encoding="utf-8", errors="ignore").strip("\r\n"))
            
    except KeyboardInterrupt:
        print("canceled write loop")
        writer.close()
        sys.exit(0)
            

async def serial_session_io(port, baud):
    
    try:
        reader = None
        reader, writer = await serial_asyncio.open_serial_connection(url=port, baudrate=baud)
        session = PromptSession("> ")

        with patch_stdout():
            asyncio.create_task(read_loop(reader, writer))
            
            while True:
                user_text = await session.prompt_async()
                writer.write(user_text.encode(encoding="utf-8", errors="ignore")+b"\r\n")
                asyncio.create_task(writer.drain())
                
    except KeyboardInterrupt:
        sys.exit(0)
    
    except  Exception as e:
        print(e)
        sys.exit(-1)
        
        
        

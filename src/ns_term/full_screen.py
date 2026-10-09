import importlib.metadata

from prompt_toolkit import Application
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Dimension, FormattedTextControl, Window
from prompt_toolkit.widgets import TextArea, VerticalLine, HorizontalLine, FormattedTextToolbar

import serial_asyncio
import sys
from serial import SerialException
import asyncio
from datetime import datetime
import os 
async def log_serial_io(port, baud):
    
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    log_name = f"{timestamp}.log"
    log_path = os.path.join(os.getcwd(), log_name)
    
    # open the serial port
    try:
        reader, writer = await serial_asyncio.open_serial_connection(url=port, baudrate=baud)
    except Exception as e:
        print(e)
        print("serial error?")
        sys.exit(-1)
        
    
    # define ser window, ser log and func to read from ser write to window

    serial_window = TextArea(focusable=False, width=Dimension(weight=2))
    
    global byte_count, response, buffer
    byte_count = 0
    log_file = open(log_path, "a", encoding="utf-8", buffering=1)
    
    
    buffer = b""
    MAX_CHARS = 2**16
    response = "temp response"
    
    async def read_loop():
        global byte_count, response, buffer
        
        try:
            while True: 
                chunk = await reader.read(1024)
                if not chunk:
                    #asyncio.sleep(1.0)
                    chunk = b"no data\r\n"

                buffer += chunk
                *lines, buffer = buffer.split(b"\n") 

                for line in lines:
                
                    if line:
                        serial_string = line.decode(encoding="utf-8", errors="ignore") + "\n"
                        byte_count += len(serial_string)
                        log_file.write(serial_string)
                        msg = serial_string.strip("\r\n")
                        
                        if response in msg:
                            cmd_window.text += msg + '\n'
                        elif "?" in msg:
                            cmd_window.text += msg + '\n'
                            
                        buf = serial_window.buffer.text
                        if len(buf) > MAX_CHARS:
                            serial_window.buffer.text = buf[-MAX_CHARS:]
                        #serial_window.buffer.cursor_position = len(serial_window.buffer.text)
                        serial_window.buffer.insert_text(f"{msg}\n")
        except SerialException:
            print("no data")
            return

    
    read_task = asyncio.create_task(read_loop())

    # define cmd window and response grabber

    cmd_window = TextArea(read_only=True, focusable=False, width=Dimension(weight=1))
    


    def cmd_on_enter(buf):
        global response
        cmd_window.text += f"{buf.text} -> "
        
        log_file.write(buf.text+"\r\n")
        
        writer.write(buf.text.encode(encoding="utf-8", errors="ignore")+b"\r\n")
        
        asyncio.create_task(writer.drain())
        
        response = buf.text.removeprefix("$").strip("?")
        
        return False

    prompt = TextArea(
        height=1,
        width=Dimension(weight=2),
        prompt="> ",
        multiline=False,
        history=InMemoryHistory(),                       # up/down arrow recall
        auto_suggest=AutoSuggestFromHistory(),           # fish-style suggestions
        completer=WordCompleter(["help", "reset", "status"]),
        complete_while_typing=True,
        accept_handler=cmd_on_enter
    )


    def status_text():
        return f"{log_path} bytes transferred: {byte_count}"
    

    
    status = Window(FormattedTextControl(status_text, style='bold'),
        height=1,
    )

    root = HSplit([
        status,
        VSplit([serial_window, VerticalLine(), cmd_window]),
        HorizontalLine(),
        VSplit([prompt])    
    ])

    kb = KeyBindings()
    
        
    @kb.add("c-c")
    @kb.add("c-q")
    def _(event):
        event.app.exit()

    app = Application(
        layout=Layout(root, focused_element=prompt),
        key_bindings=kb,
        full_screen=True,
        mouse_support=True,
    )
    try:
        await app.run_async()
    finally:
        read_task.cancel()
        writer.close()
        log_file.flush()
        log_file.close()
        sys.exit(-1)


"""Serial terminal with an input line that stays pinned while data streams in.

pip install typer pyserial prompt_toolkit
python serial_term.py /dev/ttyUSB0 --baud 115200
"""
import asyncio

import serial
import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

app = typer.Typer()


async def read_loop(ser: serial.Serial, stop: asyncio.Event) -> None:
    """Read lines in a worker thread so the event loop never blocks."""
    loop = asyncio.get_running_loop()
    while not stop.is_set():
        try:
            line = await loop.run_in_executor(None, ser.readline)  # 0.1s timeout
        except serial.SerialException as exc:
            print(f"[serial error] {exc}")
            stop.set()
            return
        if line:
            # print() is safe here: patch_stdout redraws the prompt below it
            print(line.decode(errors="replace").rstrip())

async def turnoffall(ser):
    for i in range(33):
        ser.write(f"$NVS{i}=1\r\n".encode("utf-8", errors="ignore"))

async def run(port: str, baud: int) -> None:
    ser = serial.Serial(port, baud, timeout=0.1)
    stop = asyncio.Event()
    reader = asyncio.create_task(read_loop(ser, stop))
    session = PromptSession()
    loop = asyncio.get_running_loop()

    try:
        with patch_stdout():
            while not stop.is_set():
                try:
                    text: str
                    text = await session.prompt_async("> ")
                except (EOFError, KeyboardInterrupt):  # Ctrl-D / Ctrl-C
                    break
                if text.startswith("$"):
                    await loop.run_in_executor(None, ser.write, (text+'\r\n').encode("utf-8", errors="ignore"))
                elif text.startswith("#"):
                    await turnoffall(ser)
    finally:
        stop.set()
        await reader
        ser.close()


@app.command()
def main(
    port: str = typer.Argument(..., help="Serial port, e.g. /dev/ttyUSB0 or COM3"),
    baud: int = typer.Option(115200, help="Baud rate"),
) -> None:
    asyncio.run(run(port, baud))


if __name__ == "__main__":
    app()
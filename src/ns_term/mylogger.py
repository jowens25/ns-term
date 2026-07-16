import logging
from time import sleep
from ntp import NtpArena, NtpUnsynchronizedError
import datetime
import sys
import serial 
def log_ntp_client():
    currentDt = datetime.datetime.now()
    f = currentDt.strftime("%Y%m%d%H%M%S") + ".ntplog"
    logger = logging.getLogger(f)
    
    logging.basicConfig(format="%(asctime)s %(message)s", filename=f, encoding="utf-8", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("ntp").setLevel(logging.DEBUG)

    logger.debug("Starting ntp log...")
    ntp = NtpArena(addresses=["10.1.10.206"])
    while True:
        
        
        pause = ntp.query_peers()
        
        try:
            leap, offset, jitter = ntp.calculate_state()
            logger.info(f"{leap},{offset},{jitter}")

        except NtpUnsynchronizedError as e:
            logger.warning(e)
        sleep(pause)
    
    


def log_serial_port(_port, _baud):
    currentDt = datetime.datetime.now()
    f = currentDt.strftime("%Y%m%d%H%M%S") + ".seriallog"
    logger = logging.getLogger(f)
    
    logging.basicConfig(format="%(asctime)s %(message)s", filename=f, encoding="utf-8", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("ntp").setLevel(logging.DEBUG)
    
    ser = serial.Serial(_port, baudrate=_baud, timeout=1)

    while(True):
        logger.info(ser.readline().decode(encoding="utf-8", errors="ignore").strip("\r\n"))


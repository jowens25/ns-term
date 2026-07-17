import logging
from time import sleep
from ntp import NtpArena, NtpUnsynchronizedError
import datetime
import sys
from serial import Serial 



def log_ntp_client(address):
    currentDt = datetime.datetime.now()
    f = currentDt.strftime("%Y%m%d%H%M%S") + ".ntplog"
    logger = logging.getLogger(f)
    
    logging.basicConfig(format="%(asctime)s %(message)s", filename=f, encoding="utf-8", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("ntp").setLevel(logging.DEBUG)

    logger.debug("Starting ntp log...")
    ntp = NtpArena(addresses=[address])
    while True:
        
        
        pause = ntp.query_peers(time_limit=30)
        
        try:
            leap, offset, jitter = ntp.calculate_state()
            logger.info(f"{leap},{offset},{jitter}")

        except NtpUnsynchronizedError as e:
            logger.warning(e)
        sleep(30)




 
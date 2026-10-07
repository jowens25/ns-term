import logging
from time import sleep
import datetime
import sys
import struct
import socket


from datetime import datetime, timezone
import struct

# NTP Protocol Mappings
NTP_LEAP_INDICATORS = {
    0: "0: No warning",
    1: "1: Last minute has 61 seconds (+1 leap)",
    2: "2: Last minute has 59 seconds (-1 leap)",
    3: "3: Alarm condition (clock unsynchronized)"
}

NTP_MODES = {
    0: "0: Reserved",
    1: "1: Symmetric active",
    2: "2: Symmetric passive",
    3: "3: Client",
    4: "4: Server",
    5: "5: Broadcast",
    6: "6: NTP control message",
    7: "7: Reserved for private use"
}

def format_ntp_time(epoch_seconds: float) -> str:
    """Converts NTP epoch float seconds into a human-readable ISO timestamp."""
    if not epoch_seconds or epoch_seconds <= 0:
        return "N/A"
    # Convert UTC float seconds into standard ISO 8601 text format
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat(timespec='microseconds')

def parse_ntp_packet(pkt):
    if len(pkt) < 48:
        raise ValueError("Packet payload is too short to be a valid NTP frame.")

    b0 = pkt[0]
    li = (b0 >> 6) & 3
    vn = (b0 >> 3) & 7
    mode = b0 & 7
    stratum = pkt[1]
    poll = pkt[2]
    precision = struct.unpack('!b', pkt[3:4])[0]
    
    # NTP uses 32-bit signed fixed-point for delay/dispersion (16 bits integer, 16 bits fraction)
    root_delay = struct.unpack('!i', pkt[4:8])[0] / 2**16
    root_disp = struct.unpack('!i', pkt[8:12])[0] / 2**16
    
    # Decode reference identifier safely
    # If stratum is 0 or 1, it's a 4-char ASCII string string (Kiss-o'-Death code or Ref clock ID)
    if stratum <= 1:
        ref_id = pkt[12:16].decode('ascii', errors='replace').strip()
    else:
        # For stratum 2+, it's often the IPv4 address of the upstream sync server
        ref_id = f"{pkt[12]}.{pkt[13]}.{pkt[14]}.{pkt[15]}"

    ref_sec, ref_frac = struct.unpack('!II', pkt[16:24])
    orig_sec, orig_frac = struct.unpack('!II', pkt[24:32])
    recv_sec, recv_frac = struct.unpack('!II', pkt[32:40])
    xmit_sec, xmit_frac = struct.unpack('!II', pkt[40:48])

    # NTP epoch offset adjustment (NTP starts Jan 1 1900 vs Unix Jan 1 1970)
    NTP_OFFSET = 2208988800
    
    ref_time = ref_sec - NTP_OFFSET + ref_frac / 2**32 if ref_sec else 0
    orig_time = orig_sec - NTP_OFFSET + orig_frac / 2**32 if orig_sec else 0
    recv_time = recv_sec - NTP_OFFSET + recv_frac / 2**32 if recv_sec else 0
    xmit_time = xmit_sec - NTP_OFFSET + xmit_frac / 2**32 if xmit_sec else 0
    
    # Translate Stratum logic level
    if stratum == 0:
        stratum_lbl = "0 (Unspecified / Kiss-o'-Death)"
    elif stratum == 1:
        stratum_lbl = "1 (Primary reference clock)"
    elif 2 <= stratum <= 15:
        stratum_lbl = f"{stratum} (Secondary reference server)"
    else:
        stratum_lbl = f"{stratum} (Unsynchronized / Reserved)"

    return {
        "leap indicator": NTP_LEAP_INDICATORS.get(li, f"Unknown ({li})"),
        "version number": vn,
        "mode": NTP_MODES.get(mode, f"Unknown ({mode})"),
        "stratum": stratum_lbl,
        "poll interval": f"2^{poll} seconds ({2**poll}s)",
        "precision": f"2^{precision} seconds",
        "root delay (ms)": f"{root_delay * 1000:.3f}",
        "root dispersion (ms)": f"{root_disp * 1000:.3f}",
        "reference id": ref_id,
        "reference time": format_ntp_time(ref_time),
        "origin time": format_ntp_time(orig_time),
        "receive time": format_ntp_time(recv_time),
        "transmit time": format_ntp_time(xmit_time)
    }



def log_ntp_client(address, sleepfor):
    currentDt = datetime.datetime.now()
    f = currentDt.strftime("%Y%m%d%H%M%S") + ".ntplog"
    logger = logging.getLogger(f)
    
    logging.basicConfig(format="%(asctime)s %(message)s", filename=f, encoding="utf-8", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("ntp").setLevel(logging.DEBUG)

    logger.debug("Starting ntp log...")
    #ntp = NtpArena(addresses=[address])
    
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    ntp_request = b'\x1b' + 47 * b'\0'
    #print(ntp_request)
    while True:
        try:
            sock.sendto(ntp_request, (address, 123))
            response = sock.recv(48)

            logger.info(parse_ntp_packet(response))
        except Exception as e:
            logger.info(e)
            break
        
        sleep(sleepfor)




 
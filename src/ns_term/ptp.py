import struct

PTP_MESSAGE_TYPES = {
    0x0: "Sync",
    0x1: "Delay_Req",
    0x2: "Pdelay_Req",
    0x3: "Pdelay_Resp",
    0x8: "Follow_Up",
    0x9: "Delay_Resp",
    0xA: "Pdelay_Resp_Follow_Up",
    0xB: "Announce",
    0xC: "Signaling",
    0xD: "Management"
}

def parse_ptp_header(raw_bytes: bytes):
    if len(raw_bytes) < 34:
        raise ValueError("Packet payload too small to be a valid PTP frame.")

    # 1. Slice out the 34-byte header
    header_bytes = raw_bytes[:34]
    
    # 2. Struct unpack layout (Big-Endian !)
    ptp_fmt = "! B B H B B H Q I 10s H B b"
    unpacked = struct.unpack(ptp_fmt, header_bytes)
    
    # 3. Handle Bitmasking for overlapping fields
    msg_type_id = unpacked[0] & 0x0F          
    transport_spec = (unpacked[0] & 0xF0) >> 4 
    ptp_version = unpacked[1] & 0x0F          
    
    # 4. Humanize the output
    msg_name = PTP_MESSAGE_TYPES.get(msg_type_id, f"Unknown ({hex(msg_type_id)})")
    clock_identity = unpacked[8][:8].hex()     
    source_port = int.from_bytes(unpacked[8][8:], byteorder='big') 

    # Correction field conversion (PTP scales ns by 65536)
    correction_ns = unpacked[6] / 65536.0

    # 5. Extract PTP payload timestamp if applicable
    # Message types 0-3 (Event messages) and 8-9 (Follow_Up/Delay_Resp) feature a 10-byte timestamp at byte 34
    utc_seconds = None
    if msg_type_id in [0x0, 0x1, 0x2, 0x3, 0x8, 0x9] and len(raw_bytes) >= 44:
        # Extract 10 bytes: 6 bytes for seconds, 4 bytes for nanoseconds
        ts_bytes = raw_bytes[34:44]
        
        # Unpack split fields: !H (2B) + I (4B) = 6B seconds, !I (4B) = 4B nanoseconds
        sec_high, sec_low, nsec = struct.unpack("! H I I", ts_bytes)
        
        # Combine the 16-bit high and 32-bit low into a single 48-bit seconds integer
        seconds = (sec_high << 32) | sec_low
        
        # Format as float representation of UTC epoch seconds
        utc_seconds = seconds + (nsec / 1e9)

    return {
        "msg type": msg_name,
        "ptp ver": ptp_version,
        "msg len": unpacked[2],
        "com num": unpacked[3],
        "cor (ns)": correction_ns,
        "src id": clock_identity,
        "src port id": source_port,
        "seq id": unpacked[9],
        "log int": unpacked[11],
        "utc sec": utc_seconds  # Will be a float (e.g., 1793961840.1234567) or None
    }
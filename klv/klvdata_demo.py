import struct
import datetime

def encode_klv(tag, value_bytes):
    """
    Encodes a single KLV entry with Tag, Length, and Value.
    """
    tag_byte = struct.pack("B", tag)  # Tag (1 byte)
    length_byte = struct.pack("B", len(value_bytes))  # Length (1 byte)
    return tag_byte + length_byte + value_bytes

def build_misb_metadata():
    """
    Manually builds a MISB ST 0601-compliant KLV metadata set.
    """
    klv_message = b""

    # Tag 2: Timestamp (Microseconds since epoch)
    timestamp = int(datetime.datetime.utcnow().timestamp() * 1e6)  # Current time in microseconds
    klv_message += encode_klv(2, struct.pack(">Q", timestamp))  # Encode as big-endian 8-byte integer

    # Tag 5: Platform Heading Angle (scaled by 100 to an integer)
    heading_angle = 45.0  # Degrees
    scaled_heading = int(heading_angle * 100)
    klv_message += encode_klv(5, struct.pack(">H", scaled_heading))  # Encode as big-endian 2-byte integer

    # Tag 6: Platform Latitude (scaled to microdegrees)
    latitude = 37.7749  # Degrees
    scaled_latitude = int(latitude * 1e7)
    klv_message += encode_klv(6, struct.pack(">i", scaled_latitude))  # Encode as big-endian 4-byte integer

    # Tag 7: Platform Longitude (scaled to microdegrees)
    longitude = -122.4194  # Degrees
    scaled_longitude = int(longitude * 1e7)
    klv_message += encode_klv(7, struct.pack(">i", scaled_longitude))  # Encode as big-endian 4-byte integer

    # Tag 8: Platform Altitude (scaled to meters above sea level)
    altitude = 1500.0  # Meters
    scaled_altitude = int(altitude)
    klv_message += encode_klv(8, struct.pack(">H", scaled_altitude))  # Encode as big-endian 2-byte integer

    return klv_message

# Build KLV message
klv_data = build_misb_metadata()

# Display the KLV message in hexadecimal format
print("KLV Message (Hex):", klv_data.hex())

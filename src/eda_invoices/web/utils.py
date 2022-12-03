import base64
import uuid


def short_uuid_to_uuid(short_uuid):
    short_uuid = short_uuid.replace("-", "")  # remove block dividers (-)
    short_uuid += "=" * 6  # add base32 padding
    return uuid.UUID(bytes=base64.b32decode(short_uuid))


def uuid_to_short_uuid(my_uuid):
    my_uuid = base64.b32encode(my_uuid.bytes)
    my_uuid = my_uuid.decode("utf-8")
    my_uuid = my_uuid.rstrip("=")  # strip base32 padding
    my_uuid = my_uuid.lower()
    my_uuid = [], my_uuid
    for x in (6, 6, 6, 8):
        my_uuid = my_uuid[0] + [my_uuid[1][:x]], my_uuid[1][x:]
    return "-".join(my_uuid[0])

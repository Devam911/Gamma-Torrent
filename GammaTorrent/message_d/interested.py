__author__ = ["Manav Vagrecha", "Shreyansh Shah", "Devam Shah"]
__email__ = ["manavkumar.v@ahduni.edu.in", "shreyansh.s1@ahduni.edu.in", "devam.s1@ahduni.edu.in"]


from struct import pack, unpack

class Message_Exception(Exception):
    pass


class Interested(object):
    """
        INTERESTED = <length><message_id>
            - payload length = 1 (4 bytes)
            - message id = 2 (1 byte)
    """
    message_id = 2
    interested = True

    payload_length = 1
    total_length = 4 + payload_length

    def __init__(self):
        super(Interested, self).__init__()

    def to_bytes(self):
        return pack(">IB", self.payload_length, self.message_id)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id = unpack(">IB", payload[:cls.total_length])

        if message_id != cls.message_id:
            raise Message_Exception("Not an Interested message")

        return Interested()
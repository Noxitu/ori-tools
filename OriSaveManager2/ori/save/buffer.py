import struct

from uuid import UUID


class Buffer:
    def __init__(self, data):
        self.buffer = data
        self.i = 0

    def pop(self, format):
        format = '<'+format
        ret = struct.unpack_from(format, self.buffer, self.i)
        self.i += struct.calcsize(format)
        return ret

    def pop_uuid(self):
        value, = self.pop('16s')
        return UUID(bytes_le=value)

    def pop_string(self, length_type='B'):
        length, = self.pop(length_type)
        return self.pop('{}s'.format(length))[0]

    def pop_bool(self):
        return self.pop('?')[0]

    def pop_int(self):
        return self.pop('I')[0]

    def pop_time(self):
        return self.pop('III')

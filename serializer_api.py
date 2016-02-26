import codecs


class MutableOffset:
    def __init__(self):
        self.offset = 0

    def add(self, value):
        self.offset += value

    def value(self):
        return self.offset


def serialize_number(number, byte_count):
    """
    Serializes a number into an array of bytes
    :param number: number to serialize
    :param byte_count: number of bytes that the serialization should span
    :return: the byte array with the serialized number
    """
    if number < 0:
        number += 2**(byte_count * 8)
    hex_str = hex_representation(number, 2 * byte_count)
    bytes = bytearray()
    for i in range(0, len(hex_str), 2):
        sub_str = hex_str[i:i + 2]
        byte = int(sub_str, 16)
        bytes.append(byte)
    return bytes


def deserialize_number(data, byte_count, m_offset):
    """
    Deserializes a number from a byte array
    :param data: byte array with the serialized number
    :param byte_count: number of bytes to deserialize
    :param offset: MutableOffset instance for reading from the data
    :return: the deserialized number
    """
    hex_str = ""
    for i in range(m_offset.value(), m_offset.value() + byte_count):
        hex_str += hex_representation(data[i], 2)
    m_offset.add(byte_count)
    number = int(hex_str, 16)
    if number >= 2**(byte_count * 8 - 1):
        number -= 2**(byte_count * 8)
    return number


def hex_representation(num, digit_count):
    hex_str = hex(num)
    hex_str = hex_str[hex_str.index('x') + 1:]
    if 'L' in hex_str:
        hex_str = hex_str[:hex_str.index('L')]
    if len(hex_str) > digit_count:
        hex_str = hex_str[len(hex_str) - digit_count:]
    else:
        hex_str = "0" * (digit_count - len(hex_str)) + hex_str
    return hex_str


def serialize_boolean(boolean):
    if boolean is None:
        return serialize_byte_value(-1)
    elif boolean:
        return serialize_byte_value(1)
    else:
        return serialize_byte_value(0)


def serialize_byte_object(byte):
    if byte is not None:
        return serialize_boolean(True) + serialize_number(byte, 1)
    else:
        return serialize_boolean(False)


def serialize_byte_value(byte):
    return serialize_number(byte, 1)


def serialize_short_object(short):
    if short is not None:
        return serialize_boolean(True) + serialize_number(short, 2)
    else:
        return serialize_boolean(False)


def serialize_short_value(short):
    return serialize_number(short, 2)


def serialize_int_object(int_):
    if int_ is not None:
        return serialize_boolean(True) + serialize_number(int_, 4)
    else:
        return serialize_boolean(False)


def serialize_int_value(int_):
    return serialize_number(int_, 4)


def serialize_long_object(long_):
    if long_ is not None:
        return serialize_boolean(True) + serialize_number(long_, 8)
    else:
        return serialize_boolean(False)


def serialize_long_value(long_):
    return serialize_number(long_, 8)


def deserialize_boolean(data, m_offset=MutableOffset()):
    byte = deserialize_byte_value(data, m_offset)
    if byte == -1:
        return None
    else:
        return byte != 0


def deserialize_byte_object(data, m_offset=MutableOffset()):
    not_none = deserialize_boolean(data, m_offset)
    if not_none:
        return deserialize_byte_value(data, m_offset)
    else:
        return None


def deserialize_byte_value(data, m_offset=MutableOffset()):
    return deserialize_number(data, 1, m_offset)


def deserialize_short_object(data, m_offset=MutableOffset()):
    not_none = deserialize_boolean(data, m_offset)
    if not_none:
        return deserialize_short_value(data, m_offset)
    else:
        return None


def deserialize_short_value(data, m_offset=MutableOffset()):
    return deserialize_number(data, 2, m_offset)


def deserialize_int_object(data, m_offset=MutableOffset()):
    not_none = deserialize_boolean(data, m_offset)
    if not_none:
        return deserialize_int_value(data, m_offset)
    else:
        return None


def deserialize_int_value(data, m_offset=MutableOffset()):
    return deserialize_number(data, 4, m_offset)


def deserialize_long_object(data, m_offset=MutableOffset()):
    not_none = deserialize_boolean(data, m_offset)
    if not_none:
        return deserialize_long_value(data, m_offset)
    else:
        return None


def deserialize_long_value(data, m_offset=MutableOffset()):
    return deserialize_number(data, 8, m_offset)


def serialize_string(string, encoding="utf-8"):
    if string is not None:
        data = codecs.encode(string, encoding)
        length = len(data)
        return serialize_int_value(length) + data
    else:
        return serialize_int_value(-1)


def deserialize_string(data, m_offset=MutableOffset(), encoding="utf-8"):
    length = deserialize_int_value(data, m_offset)
    if length >= 0:
        string = codecs.decode(
            data[m_offset.value():m_offset.value() + length],
            encoding)
        m_offset.add(length)
        return string
    else:
        return None


data = serialize_boolean(True)
data += serialize_boolean(None)
data += serialize_boolean(False)
data += serialize_byte_object(None)
data += serialize_byte_object(-5)
data += serialize_byte_value(8)
data += serialize_short_object(None)
data += serialize_short_object(3)
data += serialize_short_value(-3)
data += serialize_int_object(None)
data += serialize_int_object(-27)
data += serialize_int_value(5000)
data += serialize_long_object(None)
data += serialize_long_object(-300000)
data += serialize_long_value(123456)
data += serialize_string(u'hello')
data += serialize_string(None)
data += serialize_string(u'fuckkkkkkkkk')

m_offset = MutableOffset()
print(deserialize_boolean(data, m_offset))
print(deserialize_boolean(data, m_offset))
print(deserialize_boolean(data, m_offset))
print(deserialize_byte_object(data, m_offset))
print(deserialize_byte_object(data, m_offset))
print(deserialize_byte_value(data, m_offset))
print(deserialize_short_object(data, m_offset))
print(deserialize_short_object(data, m_offset))
print(deserialize_short_value(data, m_offset))
print(deserialize_int_object(data, m_offset))
print(deserialize_int_object(data, m_offset))
print(deserialize_int_value(data, m_offset))
print(deserialize_long_object(data, m_offset))
print(deserialize_long_object(data, m_offset))
print(deserialize_long_value(data, m_offset))
print(deserialize_string(data, m_offset))
print(deserialize_string(data, m_offset))
print(deserialize_string(data, m_offset))




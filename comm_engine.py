__author__ = 'Alberto'
import serializer_api
import httplib


class CommModule:
    def __init__(self):
        self.socket = httplib.socket.socket(httplib.socket.AF_INET, httplib.socket.SOCK_STREAM)


def read_data_from_socket(socket):
    data = socket.recv(1)
    length = serializer_api.deserialize_byte_value(data)
    if length == 255:
        data = socket.recv(2)
        length = serializer_api.deserialize_short_value(data)
        if length == 0:
            data = socket.recv(4)
            length = serializer_api.deserialize_int_value(data)
    return socket.recv(length)


def write_data_to_socket(socket, data):
    if len(data) > 0:
        if len(data) < 255:
            socket.send(serializer_api.serialize_byte_value(len(data)))
        else:
            socket.send(serializer_api.serialize_byte_value(255))
            if len(data) < 65536:
                socket.send(serializer_api.serialize_short_value(len(data)))
            else:
                socket.send(serializer_api.serialize_short_value(0))
                socket.send(serializer_api.serialize_int_value(len(data)))
        socket.send(data)
        socket.flush()



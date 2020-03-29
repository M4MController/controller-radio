import struct


class Serializer:
    @staticmethod
    def serialize(data) -> bytearray:
        raise NotImplemented()

    @staticmethod
    def deserialize(data: bytearray) -> (bytearray, int):
        raise NotImplemented


def generate_struct_serializer(fmt: str) -> type:
    sizes_map = {
        'i': 4,
        'd': 8,
    }

    size = sizes_map[fmt]

    class A(Serializer):
        @staticmethod
        def serialize(data) -> bytearray:
            return bytearray(struct.pack(fmt, data))

        @staticmethod
        def deserialize(data: bytearray) -> (bytearray, int):
            result, = struct.unpack(fmt, data[:size])
            return result, size

    return A


class ByteSerializer(Serializer):
    @staticmethod
    def serialize(data) -> bytearray:
        return bytearray([data])

    @staticmethod
    def deserialize(data: bytearray) -> (int, int):
        return data[0], 1,


class ByteArraySerializer(Serializer):
    @staticmethod
    def serialize(data: bytearray) -> bytearray:
        result = bytearray(struct.pack('i', len(data)))
        result.extend(data)
        return result

    @staticmethod
    def deserialize(data: bytearray) -> (bytearray, int):
        length, = struct.unpack('i', data[:4])
        return data[4:length + 4], length + 4


serializers_map = {
    'byte': ByteSerializer,
    bytearray: ByteArraySerializer,
    int: generate_struct_serializer('i'),
    float: generate_struct_serializer('d'),
}

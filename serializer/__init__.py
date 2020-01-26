import struct

from serializer.serializers import serializers_map


class BaseModel:
    """
    class Good(BaseModel):
        fields = {
            'price': float,
            'data': bytearray,
            'index': int,
        }


    a = Good(price=256.188, data=bytearray([1, 5]), index=158)
    print(a.price, a.index, a.data)
    data = a.serialize()
    print(data)
    b = Good.deserialize(data)
    print(b.price, b.index, a.data)
    """

    fields = []

    def __init__(self, **kwargs):
        for key in kwargs:
            if key in self.fields:
                setattr(self, key, kwargs[key])
            else:
                raise Exception('No such field {}'.format(key))

        for field in self.fields:
            if field not in kwargs:
                self.field = None

    def serialize(self) -> bytearray:
        result = bytearray()

        for key in self.fields:
            s = serializers_map[self.fields[key]]
            value = getattr(self, key)
            result.extend(s.serialize(value))

        return result

    @classmethod
    def deserialize(cls, data: bytearray):
        index = 0

        args = {}
        for key in cls.fields:
            s = serializers_map[cls.fields[key]]
            d, i = s.deserialize(data[index:])
            index += i
            args[key] = d

        return cls(**args)

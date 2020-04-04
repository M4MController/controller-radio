from utils.serializer.serializers import get_serializer


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

    NOTE: You must use python 3.6 or higher to use this class. Details: https://stackoverflow.com/a/39537308
    """

    fields: dict = {}

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
            value_type = self.fields[key]
            value = getattr(self, key)
            serializer = get_serializer(value_type)
            if serializer is None:
                result.extend(value.serialize())
            else:
                result.extend(serializer.serialize(value))

        return result

    @classmethod
    def deserialize(cls, data: bytearray):
        index = 0

        args = {}
        for key in cls.fields:
            value_type = cls.fields[key]
            serializer = get_serializer(value_type)
            raw_value = data[index:]
            if serializer is None:
                value = value_type.deserialize(raw_value)
            else:
                value, i = serializer.deserialize(raw_value)
                index += i
            args[key] = value

        result = cls(**args)
        result.raw_bytes = data
        return result

    def __str__(self):
        return "{class_name}({data})".format(
            class_name=self.__class__.__name__,
            data=", ".join(["{key}={value}".format(key=key, value=getattr(self, key)) for key in self.fields]),
        )

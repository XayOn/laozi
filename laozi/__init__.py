import numbers
from dataclasses import asdict, is_dataclass


class Laozi:
    @classmethod
    def parse_str(cls, obj, prefix=''):
        if not prefix:
            yield f'"{obj}"'
        else:
            yield f'{prefix[:-1]}="{obj}"'

    @classmethod
    def parse_int(cls, obj, prefix=''):
        yield f'{prefix[:-1]}={obj}'

    @classmethod
    def parse_set(cls, obj, prefix=''):
        yield from cls.parse_list(obj, prefix)

    @classmethod
    def parse_dict(cls, obj, prefix=''):
        if not hasattr(obj, 'items') and hasattr(obj, '__dict__'):
            obj = obj.__dict__
        for key, value in obj.items():
            yield from cls.get_parser_for(value)(value,
                                                 prefix=f'{prefix}{key}.')

    @classmethod
    def parse_dataclass(cls, obj, prefix=''):
        yield from cls.parse_dict(asdict(obj), prefix)

    @classmethod
    def parse_list(cls, obj, prefix=''):
        for key, value in enumerate(obj):
            yield from cls.get_parser_for(value)(value,
                                                 prefix=f'{prefix}{key}.')

    @classmethod
    def get_parser_for(cls, obj):
        default_parser = cls.unserializable
        parser = f'parse_{type(obj).__name__}'
        if hasattr(obj, '__dict__'):
            default_parser = cls.parse_dict
        if is_dataclass(obj):
            default_parser = cls.parse_dataclass
        if isinstance(obj, numbers.Number):
            parser = 'parse_int'

        return getattr(cls, parser, default_parser)

    @classmethod
    def unserializable(cls, obj, prefix=''):
        yield f'{prefix[:-1]}="{obj.__repr__()}"'

    @classmethod
    def parse(cls, input_obj):
        return '; '.join(cls.get_parser_for(input_obj)(input_obj))

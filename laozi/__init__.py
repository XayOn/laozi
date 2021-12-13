import numbers
from contextlib import suppress
import copy
from dataclasses import asdict, is_dataclass


class Laozi:
    @staticmethod
    def parse_final(key, obj):  # noqa
        return obj

    @classmethod
    def parse_str(cls, key, obj, prefix='', ctx={}):
        obj = cls.parse_final(key, obj)
        if not prefix:
            yield f'"{obj}"'
        else:
            yield f'{prefix[:-1]}="{obj}"'

    @classmethod
    def parse_int(cls, key, obj, prefix='', ctx={}):
        obj = cls.parse_final(key, obj)
        yield f'{prefix[:-1]}={obj}'

    @classmethod
    def parse_set(cls, key, obj, prefix='', ctx={}):
        yield from cls.parse_list(key, obj, prefix, ctx=ctx)

    @classmethod
    def parse_dict(cls, key, obj, prefix='', ctx={}):
        ctx['parsed_ids'].append(id(obj))
        if not hasattr(obj, 'items') and hasattr(obj, '__dict__'):
            obj = obj.__dict__
        for key, value in obj.items():
            if id(value) in ctx['parsed_ids']:
                yield f'{prefix}{key}=...'
                return
            parser = cls.get_parser_for(value)
            yield from parser(key, value, prefix=f'{prefix}{key}.', ctx=ctx)

    @classmethod
    def parse_dataclass(cls, key, obj, prefix='', ctx={}):
        yield from cls.parse_dict(key, asdict(obj), prefix, ctx=ctx)

    @classmethod
    def parse_list(cls, key, obj, prefix='', ctx={}):
        for key, value in enumerate(obj):
            parser = cls.get_parser_for(value)
            yield from parser(key, value, prefix=f'{prefix}{key}.', ctx=ctx)

    @classmethod
    def get_parser_for(cls, obj, ctx={}):
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
    def unserializable(cls, key, obj, prefix='', ctx={}):
        yield f'{prefix[:-1]}="{obj.__repr__()}"'

    @classmethod
    def parse(cls, input_obj):
        with suppress(Exception):
            input_obj = copy.deepcopy(input_obj)
        ctx = {'parsed_ids': []}
        return '; '.join(
            cls.get_parser_for(input_obj)(None, input_obj, ctx=ctx))

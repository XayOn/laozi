from decimal import Decimal
from dataclasses import dataclass
import copy


@dataclass
class Test:
    a: str = None
    b: str = None


class Foo:
    def __init__(self):
        self.a = 1
        self.b = 2


input_dict = {
    "foo": [1, 2],
    "bar": "3",
    "baz": [{
        "4": 5
    }],
    "stuff": {
        6: 7
    },
    "qu": {8, 9},
    "qux": Test(10, 11),
    'quu': 1.2,
    'qua': Decimal(1.2),
    'stux': Foo(),
    'foobar': b'123'
}
input_dict_r = {"a": {"b": "c"}}
input_dict_r['a']["c"] = input_dict_r

input_list = list(input_dict.values())
input_str = "foo"


def test_input_list():
    from laozi import Laozi

    assert Laozi.parse(input_list) == (
        '0.0=1; 0.1=2; 1="3"; 2.0.4=5; 3.6=7; 4.0=8; 4.1=9; 5.a=10; 5.b=11; '
        '6=1.2; 7=1.1999999999999999555910790149937383830547332763671875; '
        '8.a=1; 8.b=2; 9="b\'123\'"')


def test_input_dict_recursive():
    from laozi import Laozi
    assert Laozi.parse(input_dict_r) == 'a.b="c"; a.c=...'


def test_input_dict():
    from laozi import Laozi
    orig = copy.deepcopy(input_dict)
    assert Laozi.parse(input_dict) == (
        'foo.0=1; foo.1=2; bar="3"; baz.0.4=5; stuff.6=7; qu.0=8; qu.1=9; '
        'qux.a=10; qux.b=11; quu=1.2; qua=1.199999999999999955591079014993'
        '7383830547332763671875; stux.a=1; stux.b=2; foobar="b\'123\'"')
    input_dict.pop('stux')
    orig.pop('stux')
    assert orig == input_dict


def test_input_str():
    from laozi import Laozi
    assert Laozi.parse(input_str) == '"foo"'
    assert input_str == "foo"

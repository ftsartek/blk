import platform
import re
import json
import typing as t
from blk.types import (Bool, Color, DictSection, Float, Float2, Float3, Float4, Float12, Int2, Int3, ListSection,
                       Section, Var, Value, dgen_float, dgen_float_element)

__all__ = ['serialize', 'JSON', 'JSON_2', 'JSON_3']

implementation = platform.python_implementation()
if implementation == 'CPython':
    from _ctypes import PyObj_FromPtr

    class NoIndentEncoder(json.JSONEncoder):
        # https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module

        fmt = r'@@{}@@'
        regex = re.compile(fmt.format(r'(\d+)'))

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.kwargs = dict(kwargs)
            del self.kwargs['indent']

        def default(self, o):
            if isinstance(o, Var):
                value = o.value
                return self.fmt.format(id(value))
            return super().default(o)

        def iterencode(self, o, _one_shot=False):
            for s in super().iterencode(o):
                m = self.regex.search(s)
                if m:
                    id_ = int(m.group(1))
                    value = PyObj_FromPtr(id_)
                    text = json.dumps(value, **self.kwargs)
                    s = s.replace(f'"{self.fmt.format(id_)}"', text)
                yield s
elif implementation == 'PyPy':
    class NoIndentEncoder(json.JSONEncoder):
        fmt = r'@@{}@@'
        regex = re.compile(fmt.format(r'(\d+)'))

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.kwargs = dict(kwargs)
            del self.kwargs['indent']
            self._objects_map = {}

        def default(self, o):
            if isinstance(o, Var):
                value = o.value
                key = id(value)
                self._objects_map[key] = value
                return self.fmt.format(key)
            return super().default(o)

        def iterencode(self, o, _one_shot=False):
            for s in super().iterencode(o):
                m = self.regex.search(s)
                if m:
                    id_ = int(m.group(1))
                    value = self._objects_map[id_]
                    text = json.dumps(value, **self.kwargs)
                    s = s.replace(f'"{self.fmt.format(id_)}"', text)
                yield s


class Mapper:
    @classmethod
    def _map_section(cls, section: DictSection) -> t.Union[t.Sequence, t.Mapping]:
        raise NotImplementedError

    @classmethod
    def _map_value(cls, value: Value):
        if isinstance(value, (DictSection, t.Mapping)):
            return cls._map_section(value)
        elif isinstance(value, Float12):
            return tuple(Var(tuple(dgen_float_element(x) for x in value[i:i+3])) for i in range(0, 10, 3))
        elif isinstance(value, Color):
            return f"#{''.join(format(x, '02x') for x in value)}"
        elif isinstance(value, (Float2, Float3, Float4)):
            return Var(tuple(float(format(x, 'e')) for x in value))
        elif isinstance(value, (Int2, Int3)):
            return Var(value)
        elif isinstance(value, Float):
            return dgen_float(value)
        elif isinstance(value, Bool):
            return bool(value)
        else:
            return value

    @classmethod
    def map(cls, root):
        return cls._map_section(root)


class JSONMapper(Mapper):
    @classmethod
    def _map_section(cls, section: DictSection) -> t.Union[t.Sequence, t.Mapping]:
        items = section.items()
        if not items:
            return []
        else:
            m: t.Union[list, dict] = {}
            for n, vs in items:
                if len(vs) == 1:
                    v = vs[0]
                    if isinstance(m, list):
                        m.append({n: cls._map_value(v)})
                    else:
                        m[n] = cls._map_value(v)
                else:
                    if not isinstance(m, list):
                        m = [{n: v} for n, v in m.items()]
                    m.extend({n: cls._map_value(v)} for v in vs)
            return m


class JSON2Mapper(Mapper):
    @classmethod
    def _map_section(cls, section: DictSection) -> t.Union[t.Sequence, t.Mapping]:
        items = section.items()
        if not items:
            return []
        else:
            return {n: list(map(cls._map_value, vs)) for n, vs in items}


class JSON3Mapper(Mapper):
    @classmethod
    def _map_section(cls, section: DictSection) -> t.Mapping:
        items = section.items()
        if not items:
            return {}
        else:
            return {n: (list(map(cls._map_value, vs)) if len(vs) > 1 else cls._map_value(vs[0])) for n, vs in items}


class JSONMinMapper(Mapper):
    pass

# todo: собрать в перечисление
JSON = 0
JSON_MIN = 1
JSON_2 = 3
JSON_3 = 4


def serialize(root: Section, ostream, out_type: int, is_sorted=False, check_cycle=False):
    mapper = {
        JSON: JSONMapper,
        JSON_MIN: JSONMinMapper,
        JSON_2: JSON2Mapper,
        JSON_3: JSON3Mapper,
    }[out_type]
    if root:
        if check_cycle:
            root.check_cycle()
        if isinstance(root, DictSection):
            json.dump(mapper.map(root), ostream, cls=NoIndentEncoder, ensure_ascii=False, indent=2, separators=(',', ': '),
                      sort_keys=is_sorted)
        elif isinstance(root, ListSection):
            raise NotImplementedError

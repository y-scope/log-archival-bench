import json
import os
from threading import RLock

class JsonItem:
    # base is always a list, dict, int, etc
    # if base is a list or a dict, its items are all JsonItems
    def __init__(self, base=None, filename=None):
        if type(base) is list:
            self.base = [JsonItem(i) for i in base]
        elif type(base) is dict:
            self.base = {key: JsonItem(value) for key, value in base.items()}
        else:
            self.base = base
        self.filename = filename
    
    def syncbase(self, key):
        if self.base is None:
            if type(key) is int:
                self.base = list()
            else:
                self.base = dict()

    def __getitem__(self, key):
        self.syncbase(key)
        assert self.base is not None

        try:
            return self.base[key]
        except KeyError:
            self.base[key] = JsonItem(None)
            return self.base[key]
        except IndexError:
            assert type(self.base) is list
            assert len(self.base) <= key

            while len(self.base) <= key:
                self.base.append(JsonItem(None))

            return self.base[key]

    def __setitem__(self, key, value):
        self.syncbase(key)
        assert self.base is not None

        if type(value) is not JsonItem:
            toinsert = JsonItem(value)
        else:
            toinsert = value

        try:
            self.base[key] = toinsert
        except IndexError:
            assert type(self.base) is list
            assert len(self.base) <= key

            while len(self.base) <= key:
                self.base.append(JsonItem(None))
            self.base[key] = toinsert

    def __delitem__(self, key):
        self.syncbase(key)
        assert self.base is not None

        del self.base[key]

    def __len__(self):
        if self.base is None:
            raise Exception("__len__ called on generic JsonItem")
        return len(self.base)

    def __repr__(self):
        return repr(self.base)

    def __getattr__(self, name):
        return getattr(self.base, name)

    def compile(self):
        if type(self.base) is list:
            return [i.compile() for i in self.base]
        elif type(self.base) is dict:
            return {key: value.compile() for key, value in self.base.items()}
        else:
            return self.base

    def write(self):
        if self.filename is None:
            raise NameError("Writing with JsonItem not associated with file")

        with open(self.filename, 'w') as file:
            json.dump(self.compile(), file, indent=2)

    @classmethod
    def read(cls, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                toret = cls(json.load(file), filename)
        else:
            toret = cls({}, filename)
            toret.write()
        return toret

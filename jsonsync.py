import json
import os
from threading import RLock

class Autoitem:
    # base is always a list, dict, int, etc
    # if base is a list or a dict, its items are all Autoitems
    def __init__(self, base=None):
        if type(base) is list:
            self.base = [Autoitem(i) for i in base]
        elif type(base) is dict:
            self.base = {key: Autoitem(value) for key, value in base.items()}
        else:
            self.base = base
    
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
        except (KeyError, IndexError):
            self.base[key] = Autoitem(None)
            return self.base[key]

    def __setitem__(self, key, value):
        self.syncbase(key)
        assert self.base is not None

        try:
            self.base[key] = Autoitem(value)
        except IndexError:
            assert type(self.base) is list
            assert len(self.base) <= key

            while len(self.base) <= key:
                self.base.append(Autoitem(None))
            self.base[key] = Autoitem(value)

    def __delitem__(self, key):
        self.syncbase(key)
        assert self.base is not None

        del self.base[key]

    def __len__(self):
        if self.base is None:
            raise Exception("__len__ called on generic Autoitem")
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


class JsonSyncDict:
    def __init__(self, file_path):
        self.file_path = file_path
        self._lock = RLock()
        self._data = Autoitem({})
        self._load()

    def _load(self):
        with self._lock:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    try:
                        self._data = Autoitem(json.load(f))
                    except json.JSONDecodeError:
                        self._data = Autoitem({})
            else:
                self._data = Autoitem({})

    def _sync(self):
        with self._lock:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                print(self._data)
                json.dump(self._data.compile(), f, indent=2)
                print(self._data.compile())

    def __getitem__(self, key):
        self._load()
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._sync()

    def __delitem__(self, key):
        del self._data[key]
        self._sync()

    def get(self, key, default=None):
        self._load()
        return self._data.get(key, default)

    def items(self):
        self._load()
        return self._data.items()

    def keys(self):
        self._load()
        return self._data.keys()

    def values(self):
        self._load()
        return self._data.values()

    def update(self, *args, **kwargs):
        self._data.update(*args, **kwargs)
        self._sync()

    def clear(self):
        self._data.clear()
        self._sync()

    def __contains__(self, key):
        self._load()
        return key in self._data

    def __repr__(self):
        self._load()
        return repr(self._data)

    def __len__(self):
        self._load()
        return len(self._data)


settings = JsonSyncDict("settings.json")

# Deep write — works even if intermediate levels are missing
settings["volumes"]["max"][2] = 1

print(settings["volumes"])  # {'max': [None, None, 1]}

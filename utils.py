import sys


class Mapper:
    def __init__(self):
        self.counter = 0
        self.mp = {}
        self.keys = []

    def add(self, key):
        self.mp[key] = self.counter
        self.keys.append(key)
        self.counter += 1

    def get(self, key):
        return self.mp[key]

    def rget(self, idx):
        return self.keys[idx]

    def n(self):
        return self.counter


def ensure(cond, msg):
    if not cond:
        print(f'ERROR: {msg}')
        sys.exit(-1)
import time
from cachetools import TTLCache

class TTICache:
    def __init__(self, maxsize, ttl, tti):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.tti = tti
        self.access_times = {}

    def get(self, key):
        current_time = time.time()
        if current_time - self.access_times.get(key, 0) < self.tti:
            try:
                self.access_times[key] = current_time
                return self.cache[key]
            except:
                return None
        return None

    def set(self, key, value):
        self.cache[key] = value
        self.access_times[key] = time.time()


if __name__ == "__main__":
    cache = TTICache(10, 5, 1)
    print(cache.get("test"))
    cache.set("test", 10)
    print(cache.get("test"))

    time.sleep(2)
    print(cache.get("test")) # TTI -> didn't access test more than 1 second

    cache.set("test", 10)
    print(cache.get("test"))
    for _ in range(5):
        print(cache.get("test"))
        time.sleep(0.8)

    time.sleep(2)
    print(cache.get("test")) # TTL



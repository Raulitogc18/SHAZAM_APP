class HashTable:

    DEFAULT_CAPACITY = 10007

    def __init__(self, capacity=None):
        self._capacity = capacity or self.DEFAULT_CAPACITY
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

    # ---------------- HASH ---------------- #

    def _hash(self, key):
        key = int(key)
        return (key * 2654435761) % self._capacity

    # ---------------- CORE ---------------- #

    def insert(self, key, value):
        idx = self._hash(key)
        self._buckets[idx].append((key, value))
        self._size += 1

        if self.load_factor() > 0.75:
            self._resize()

    def lookup(self, key):
        idx = self._hash(key)
        result = []

        for k, v in self._buckets[idx]:
            if k == key:
                result.append(v)

        return result

    # ---------------- INFO ---------------- #

    def size(self):
        return self._size

    def capacity(self):
        return self._capacity

    def load_factor(self):
        return self._size / self._capacity

    def stats(self):
        empty = 0
        max_chain = 0
        total_chain = 0
        non_empty = 0

        for bucket in self._buckets:
            length = len(bucket)
            if length == 0:
                empty += 1
            else:
                non_empty += 1
                total_chain += length
                max_chain = max(max_chain, length)

        avg_chain = (total_chain / non_empty) if non_empty > 0 else 0

        return {
            "capacity": self._capacity,
            "size": self._size,
            "load_factor": round(self.load_factor(), 4),
            "empty_buckets": empty,
            "max_chain_length": max_chain,
            "avg_chain_length": round(avg_chain, 4),
        }

    # ---------------- RESIZE ---------------- #

    @staticmethod
    def _next_prime(n):
        if n <= 2:
            return 2

        if n % 2 == 0:
            n += 1

        def is_prime(x):
            if x < 2:
                return False
            if x % 2 == 0:
                return x == 2
            i = 3
            while i * i <= x:
                if x % i == 0:
                    return False
                i += 2
            return True

        while not is_prime(n):
            n += 2

        return n

    def _resize(self):
        new_capacity = self._next_prime(self._capacity * 2)
        old_buckets = self._buckets

        self._capacity = new_capacity
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self.insert(key, value)
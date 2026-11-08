"""
Memory Management Module - Upgraded by Mathin
Simulates Main Memory (RAM) and Cache with LRU Replacement Policy.
"""


class MemorySystem:
    def __init__(self, cache_lines=4, policy="LRU"):
        if cache_lines <= 0:
            raise ValueError("cache_lines must be greater than zero")

        self.main_memory = {}
        self.cache_lines = cache_lines
        self.policy = policy.upper()

        if self.policy != "LRU":
            raise ValueError("Only LRU replacement policy is supported")

        self.cache = {
            i: {
                "tag": None,
                "value": None,
                "valid": False,
                "age": 0
            }
            for i in range(cache_lines)
        }

        self.cache_hits = 0
        self.cache_misses = 0
        self.clock_cycle = 0

    def reset(self):
        self.main_memory.clear()

        for i in range(self.cache_lines):
            self.cache[i] = {
                "tag": None,
                "value": None,
                "valid": False,
                "age": 0
            }

        self.cache_hits = 0
        self.cache_misses = 0
        self.clock_cycle = 0

    def _find_cache_line(self, address):
        for i, entry in self.cache.items():
            if entry["valid"] and entry["tag"] == address:
                return i
        return None

    def _find_victim_line(self):
        for i, entry in self.cache.items():
            if not entry["valid"]:
                return i

        return max(
            self.cache,
            key=lambda i: self.cache[i]["age"]
        )

    def _update_ages(self, accessed_line):
        for i, entry in self.cache.items():
            if not entry["valid"]:
                continue

            if i == accessed_line:
                entry["age"] = 0
            else:
                entry["age"] += 1

    def read(self, address: int) -> int:
        self.clock_cycle += 1

        cache_line = self._find_cache_line(address)

        if cache_line is not None:
            self.cache_hits += 1
            self._update_ages(cache_line)
            return self.cache[cache_line]["value"]

        self.cache_misses += 1
        value = self.main_memory.get(address, 0)

        victim = self._find_victim_line()

        self.cache[victim] = {
            "tag": address,
            "value": value,
            "valid": True,
            "age": 0
        }

        self._update_ages(victim)

        return value

    def write(self, address: int, value: int):
        self.clock_cycle += 1

        self.main_memory[address] = value

        cache_line = self._find_cache_line(address)

        if cache_line is None:
            cache_line = self._find_victim_line()

        self.cache[cache_line] = {
            "tag": address,
            "value": value,
            "valid": True,
            "age": 0
        }

        self._update_ages(cache_line)

    def get_cache_lines_for_ui(self) -> list:
        return [
            {
                "Line": i,
                "Tag": entry["tag"],
                "Value": entry["value"],
                "Age": entry["age"],
                "Valid": entry["valid"]
            }
            for i, entry in self.cache.items()
        ]

    def get_stats(self) -> dict:
        total_accesses = self.cache_hits + self.cache_misses

        hit_ratio = (
            self.cache_hits / total_accesses * 100
            if total_accesses > 0 else 0.0
        )

        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_ratio": round(hit_ratio, 2),
            "policy": self.policy
        }
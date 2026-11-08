"""
Memory Management Module - Upgraded by Mathin
Simulates Main Memory (RAM) and Cache with LRU Replacement Policy.
"""

class MemorySystem:
    def __init__(self, cache_lines=4, policy="LRU"):
        self.main_memory = {}
        self.cache_lines = cache_lines
        self.policy = policy.upper()
        
        # Cache structure includes an 'age' counter for LRU
        self.cache = {i: {"tag": None, "value": None, "valid": False, "age": 0} for i in range(cache_lines)}
        
        self.cache_hits = 0
        self.cache_misses = 0
        self.clock_cycle = 0

    def reset(self):
        self.main_memory.clear()
        for i in range(self.cache_lines):
            self.cache[i] = {"tag": None, "value": None, "valid": False, "age": 0}
        self.cache_hits = 0
        self.cache_misses = 0
        self.clock_cycle = 0

    def _get_cache_index_and_tag(self, address: int) -> tuple:
        index = address % self.cache_lines
        tag = address // self.cache_lines
        return index, tag

    def _increment_ages(self):
        """Increases the age of all valid cache lines (for LRU)."""
        for i in range(self.cache_lines):
            if self.cache[i]["valid"]:
                self.cache[i]["age"] += 1

    def _find_victim_line(self, index: int) -> int:
        """Finds which cache line to replace based on policy."""
        if self.policy == "LRU":
            # Find the line with the highest age (Least Recently Used)
            victim = index
            max_age = -1
            for i in range(self.cache_lines):
                if self.cache[i]["age"] > max_age:
                    max_age = self.cache[i]["age"]
                    victim = i
            return victim
        else:
            # FIFO / Direct Mapped fallback
            return index

    def read(self, address: int) -> int:
        self.clock_cycle += 1
        index, tag = self._get_cache_index_and_tag(address)
        cache_entry = self.cache[index]

        if cache_entry["valid"] and cache_entry["tag"] == tag:
            self.cache_hits += 1
            cache_entry["age"] = 0 # Reset age on access (LRU logic)
            return cache_entry["value"]
        
        self.cache_misses += 1
        value = self.main_memory.get(address, 0)
        
        # LRU Replacement
        victim_line = self._find_victim_line(index)
        self.cache[victim_line] = {"tag": tag, "value": value, "valid": True, "age": 0}
        self._increment_ages()
        
        return value

    def write(self, address: int, value: int):
        self.clock_cycle += 1
        self.main_memory[address] = value
        index, tag = self._get_cache_index_and_tag(address)
        self.cache[index] = {"tag": tag, "value": value, "valid": True, "age": 0}
        self._increment_ages()

    def get_cache_lines_for_ui(self) -> list:
        """Returns cache state formatted for Streamlit display."""
        return [
            {"Line": i, "Tag": self.cache[i]["tag"], "Value": self.cache[i]["value"], "Age": self.cache[i]["age"]}
            for i in range(self.cache_lines)
        ]

    def get_stats(self) -> dict:
        total_accesses = self.cache_hits + self.cache_misses
        hit_ratio = (self.cache_hits / total_accesses * 100) if total_accesses > 0 else 0.0
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_ratio": round(hit_ratio, 2),
            "policy": self.policy
        }
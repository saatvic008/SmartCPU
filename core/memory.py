"""
Memory Management Module
Simulates Main Memory (RAM) and a 4-line Direct-Mapped Cache.
"""

class MemorySystem:
    def __init__(self, cache_lines=4):
        self.main_memory = {}  # Simulates RAM (Address: Value)
        self.cache_lines = cache_lines
        # Cache structure: {index: {"tag": tag, "value": value, "valid": True/False}}
        self.cache = {i: {"tag": None, "value": None, "valid": False} for i in range(cache_lines)}
        
        # Performance metrics
        self.cache_hits = 0
        self.cache_misses = 0

    def reset(self):
        self.main_memory.clear()
        for i in range(self.cache_lines):
            self.cache[i] = {"tag": None, "value": None, "valid": False}
        self.cache_hits = 0
        self.cache_misses = 0

    def _get_cache_index_and_tag(self, address: int) -> tuple:
        """Calculates cache index and tag for a given memory address."""
        index = address % self.cache_lines
        tag = address // self.cache_lines
        return index, tag

    def read(self, address: int) -> int:
        """Reads data from memory, utilizing cache if possible."""
        index, tag = self._get_cache_index_and_tag(address)
        cache_entry = self.cache[index]

        # Check for Cache Hit
        if cache_entry["valid"] and cache_entry["tag"] == tag:
            self.cache_hits += 1
            return cache_entry["value"]
        
        # Cache Miss: Fetch from Main Memory
        self.cache_misses += 1
        if address in self.main_memory:
            value = self.main_memory[address]
        else:
            value = 0  # Default value if memory is uninitialized
            
        # Update Cache (Direct-Mapped Replacement)
        self.cache[index] = {"tag": tag, "value": value, "valid": True}
        return value

    def write(self, address: int, value: int):
        """Writes data to Main Memory and updates the Cache (Write-Through)."""
        self.main_memory[address] = value
        index, tag = self._get_cache_index_and_tag(address)
        self.cache[index] = {"tag": tag, "value": value, "valid": True}

    def get_stats(self) -> dict:
        total_accesses = self.cache_hits + self.cache_misses
        hit_ratio = (self.cache_hits / total_accesses * 100) if total_accesses > 0 else 0.0
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_ratio": round(hit_ratio, 2),
            "cache_state": self.cache.copy()
        }
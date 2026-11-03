"""
Unit Tests for Register File Module.
"""
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.registers import RegisterFile

class TestRegisters(unittest.TestCase):
    def setUp(self):
        self.reg_file = RegisterFile()
        
    def test_initial_values(self):
        self.assertEqual(self.reg_file.read('R0'), 0)
        
    def test_write_and_read(self):
        self.reg_file.write('R1', 42)
        self.assertEqual(self.reg_file.read('R1'), 42)

if __name__ == '__main__':
    unittest.main()

"""
Unit Tests for ALU Module.
"""
import unittest
import sys
import os

# Add parent directory to path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.alu import ALU

class TestALU(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(ALU.execute('ADD', 10, 20), 30)
        
    def test_subtraction(self):
        self.assertEqual(ALU.execute('SUB', 30, 10), 20)
        
    def test_bitwise_and(self):
        self.assertEqual(ALU.execute('AND', 0b1010, 0b1100), 0b1000)

if __name__ == '__main__':
    unittest.main()

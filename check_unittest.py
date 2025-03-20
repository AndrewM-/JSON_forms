# check_unittest.py
import sys
print(f"Python version: {sys.version}")

try:
    import unittest
    print("unittest module is available!")
    print(f"unittest version: {unittest.__version__ if hasattr(unittest, '__version__') else 'Built-in module (no version)'}")
except ImportError:
    print("unittest module is NOT available!")
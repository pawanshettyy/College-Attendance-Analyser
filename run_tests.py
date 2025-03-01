#!/usr/bin/env python3
import unittest
import os
import sys

# Add the current directory to the path so that imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Discover and run all tests
if __name__ == '__main__':
    # Discover all tests in the tests directory
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
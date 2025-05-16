#!/usr/bin/env python3
import unittest
import sys
import os

def run_tests():
    """Run all tests in the tests directory"""
    # Get the root directory of the project
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    
    # Add the root directory to the Python path
    sys.path.insert(0, root_dir)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.join(root_dir, "tests"))
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
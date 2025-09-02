#!/usr/bin/env python3
"""
Test runner for the agentic-rag application.
This script runs all tests using pytest.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest"""
    try:
        # Run pytest on the test_app.py file
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_app.py", "-v"
        ], check=True, capture_output=True, text=True)
        
        print("Tests completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Tests failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("Error: pytest not found. Please install it with 'pip install pytest'")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
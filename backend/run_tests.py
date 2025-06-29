#!/usr/bin/env python3
"""
Test runner script for GPUStack UI backend.
Provides convenient commands for running different types of tests.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=True,
            capture_output=True, text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="GPUStack UI Backend Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "auth", "api", "coverage"],
        help="Type of tests to run"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--file", "-f", help="Run specific test file")
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = "python -m pytest"
    
    if args.verbose:
        base_cmd += " -v"
    
    # Determine which tests to run
    if args.test_type == "all":
        cmd = f"{base_cmd} tests/"
    elif args.test_type == "unit":
        cmd = f"{base_cmd} tests/unit/ -m unit"
    elif args.test_type == "integration":
        cmd = f"{base_cmd} tests/integration/ -m integration"
    elif args.test_type == "auth":
        cmd = f"{base_cmd} -m auth"
    elif args.test_type == "api":
        cmd = f"{base_cmd} -m api"
    elif args.test_type == "coverage":
        cmd = f"{base_cmd} tests/ --cov=. --cov-report=html --cov-report=term"
    
    if args.file:
        cmd = f"{base_cmd} {args.file}"
    
    print(f"Running: {cmd}")
    print("-" * 50)
    
    # Run the tests
    success = run_command(cmd)
    
    if not success:
        sys.exit(1)
    
    print("-" * 50)
    print("✅ Tests completed successfully!")
    
    if args.test_type == "coverage":
        print("\n📊 Coverage report generated in htmlcov/index.html")


if __name__ == "__main__":
    main()

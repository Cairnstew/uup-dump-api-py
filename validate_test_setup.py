#!/usr/bin/env python3
"""
Validation script to check test setup and run basic checks.
"""

import sys
import subprocess
import importlib.util


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ is required")
        return False
    return True


def check_module(module_name):
    """Check if a module is installed."""
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print(f"✓ {module_name} is installed")
        return True
    else:
        print(f"✗ {module_name} is NOT installed")
        return False


def check_dependencies():
    """Check if all test dependencies are installed."""
    required_modules = [
        "pytest",
        "requests",
        "unittest.mock",  # Built-in, should always be available
    ]

    recommended_modules = [
        "pytest_cov",
        "pytest_mock",
    ]

    print("\nChecking required dependencies:")
    all_required = all(check_module(mod) for mod in required_modules)

    print("\nChecking recommended dependencies:")
    all_recommended = all(check_module(mod) for mod in recommended_modules)

    return all_required, all_recommended


def check_test_file():
    """Check if test file exists."""
    import os

    test_file = "test_uup_dump_api.py"

    if os.path.exists(test_file):
        print(f"\n✓ Test file '{test_file}' found")
        lines = len(open(test_file).readlines())
        print(f"  Lines of test code: {lines}")
        return True
    else:
        print(f"\n✗ Test file '{test_file}' NOT found")
        return False


def check_module_files():
    """Check if module files exist."""
    import os

    module_files = ["__init__.py", "adapter.py", "exceptions.py"]

    print("\nChecking module files:")
    all_exist = True
    for file in module_files:
        if os.path.exists(file):
            print(f"✓ {file} found")
        else:
            print(f"✗ {file} NOT found")
            all_exist = False

    return all_exist


def run_quick_test():
    """Run a quick test to verify setup."""
    print("\nRunning quick test...")
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "test_uup_dump_api.py", "-v", "--collect-only"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            # Count collected tests
            lines = result.stdout.split("\n")
            test_lines = [l for l in lines if "<Function" in l or "<Method" in l]
            print(f"✓ Collected {len(test_lines)} tests")
            return True
        else:
            print("✗ Test collection failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Test collection timed out")
        return False
    except FileNotFoundError:
        print("✗ pytest not found - install with: pip install pytest")
        return False
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False


def main():
    """Main validation function."""
    print("=" * 60)
    print("UUP Dump API Test Setup Validation")
    print("=" * 60)

    checks = {
        "Python Version": check_python_version(),
        "Module Files": check_module_files(),
        "Dependencies": check_dependencies()[0],
        "Test File": check_test_file(),
        "Quick Test": run_quick_test(),
    }

    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    for check_name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name:.<40} {status}")

    all_passed = all(checks.values())

    print("=" * 60)
    if all_passed:
        print("✓ All checks passed! Ready to run tests.")
        print("\nRun tests with: pytest test_uup_dump_api.py -v")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nInstall dependencies with: pip install -r requirements-test.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

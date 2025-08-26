 
"""
Unified test runner for both frontend and backend tests.
Run with: python run_tests.py [options]
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any
import json

class TestRunner:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.results = {
            "backend": {"success": False, "output": "", "duration": 0},
            "frontend": {"success": False, "output": "", "duration": 0}
        }

    def run_command(self, command: List[str], cwd: Path, capture_output: bool = True) -> Dict[str, Any]:
        """Run a command and return results."""
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=True
            )
            duration = time.time() - start_time
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "duration": duration,
                "return_code": result.returncode
            }
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "output": e.stdout,
                "error": e.stderr,
                "duration": duration,
                "return_code": e.returncode
            }
        except FileNotFoundError:
            return {
                "success": False,
                "output": "",
                "error": f"Command not found: {' '.join(command)}",
                "duration": 0,
                "return_code": 1
            }

    def run_backend_tests(self, test_type: str = "all", coverage: bool = True, verbose: bool = True) -> Dict[str, Any]:
        """Run backend tests using pytest."""
        print("🧪 Running Backend Tests...")
        
        cmd = ["python", "-m", "pytest"]
        
        if test_type != "all":
            cmd.append(f"tests/{test_type}/")
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=app", "--cov-report=term-missing"])
        
        result = self.run_command(cmd, self.backend_dir)
        self.results["backend"] = result
        
        if result["success"]:
            print(f"✅ Backend tests passed in {result['duration']:.2f}s")
        else:
            print(f"❌ Backend tests failed in {result['duration']:.2f}s")
            if result["error"]:
                print(f"Error: {result['error']}")
        
        return result

    def run_frontend_tests(self, test_type: str = "all") -> Dict[str, Any]:
        """Run frontend tests."""
        print("🎨 Running Frontend Tests...")
        
        if test_type == "e2e":
            cmd = ["npx", "playwright", "test"]
        elif test_type == "unit":
            cmd = ["npm", "run", "test:unit"]
        else:
            cmd = ["npm", "run", "test"]
        
        result = self.run_command(cmd, self.frontend_dir)
        self.results["frontend"] = result
        
        if result["success"]:
            print(f"✅ Frontend tests passed in {result['duration']:.2f}s")
        else:
            print(f"❌ Frontend tests failed in {result['duration']:.2f}s")
            if result["error"]:
                print(f"Error: {result['error']}")
        
        return result

    def run_all_tests(self, test_type: str = "all", parallel: bool = False, coverage: bool = True) -> bool:
        """Run both frontend and backend tests."""
        print("🚀 Starting Full Test Suite...")
        print(f"Test Type: {test_type}")
        print(f"Parallel: {parallel}")
        print(f"Coverage: {coverage}")
        print("=" * 50)
        
        if parallel:
            # Run tests in parallel (requires both to be available)
            import threading
            
            backend_thread = threading.Thread(
                target=self.run_backend_tests,
                args=(test_type, coverage, True)
            )
            frontend_thread = threading.Thread(
                target=self.run_frontend_tests,
                args=(test_type,)
            )
            
            backend_thread.start()
            frontend_thread.start()
            
            backend_thread.join()
            frontend_thread.join()
        else:
            # Run tests sequentially
            self.run_backend_tests(test_type, coverage, True)
            self.run_frontend_tests(test_type)
        
        # Print summary
        self.print_summary()
        
        # Return overall success
        return all(result["success"] for result in self.results.values())

    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_duration = sum(result["duration"] for result in self.results.values())
        
        for test_suite, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            duration = f"{result['duration']:.2f}s"
            print(f"{test_suite.title()}: {status} ({duration})")
        
        print(f"\nTotal Duration: {total_duration:.2f}s")
        
        if all(result["success"] for result in self.results.values()):
            print("\n🎉 All tests passed!")
            return True
        else:
            print("\n💥 Some tests failed!")
            return False

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        print("🔍 Checking Dependencies...")
        
        # Check Python/pytest
        try:
            result = self.run_command(["python", "--version"], self.root_dir)
            if result["success"]:
                print(f"✅ Python: {result['output'].strip()}")
            else:
                print("❌ Python not found")
                return False
        except Exception:
            print("❌ Python not found")
            return False
        
        # Check pytest
        try:
            result = self.run_command(["python", "-m", "pytest", "--version"], self.root_dir)
            if result["success"]:
                print(f"✅ pytest: {result['output'].strip()}")
            else:
                print("❌ pytest not found")
                return False
        except Exception:
            print("❌ pytest not found")
            return False
        
        # Check Node.js
        try:
            result = self.run_command(["node", "--version"], self.root_dir)
            if result["success"]:
                print(f"✅ Node.js: {result['output'].strip()}")
            else:
                print("❌ Node.js not found")
                return False
        except Exception:
            print("❌ Node.js not found")
            return False
        
        # Check npm
        try:
            result = self.run_command(["npm", "--version"], self.root_dir)
            if result["success"]:
                print(f"✅ npm: {result['output'].strip()}")
            else:
                print("❌ npm not found")
                return False
        except Exception:
            print("❌ npm not found")
            return False
        
        print("✅ All dependencies found!")
        return True

def main():
    parser = argparse.ArgumentParser(description="Run both frontend and backend tests")
    parser.add_argument(
        "--type", "-t",
        choices=["all", "unit", "integration", "e2e"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies only"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Run only backend tests"
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Run only frontend tests"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.check_deps:
        success = runner.check_dependencies()
        sys.exit(0 if success else 1)
    
    if args.backend_only:
        success = runner.run_backend_tests(args.type, not args.no_coverage, True)
        sys.exit(0 if success else 1)
    
    if args.frontend_only:
        success = runner.run_frontend_tests(args.type)
        sys.exit(0 if success else 1)
    
    # Run all tests
    success = runner.run_all_tests(
        test_type=args.type,
        parallel=args.parallel,
        coverage=not args.no_coverage
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
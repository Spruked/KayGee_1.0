"""
KayGee Adversarial Test Runner
Automated test execution with comprehensive monitoring and reporting
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import argparse
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import KayGee system
try:
    from main import VaultedReasonerSystem
    KAYGEE_AVAILABLE = True
except ImportError as e:
    KAYGEE_AVAILABLE = False
    print(f"❌ KayGee system not available: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adversarial trial paths
ADVERSARIAL_ROOT = Path(__file__).parent.parent / "adversarial_trial"
RESULTS_DIR = ADVERSARIAL_ROOT / "results"
METRICS_DIR = ADVERSARIAL_ROOT / "metrics"
LOGS_DIR = ADVERSARIAL_ROOT / "logs"

class TestMonitor:
    """Monitor test execution metrics"""
    
    def __init__(self):
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0
        self.execution_times = []
        self.start_time = None
        self.end_time = None
    
    def start_suite(self):
        self.start_time = time.time()
        logger.info("🚀 Test suite monitoring started")
    
    def end_suite(self):
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        logger.info(f"🏁 Test suite monitoring ended. Total time: {total_time:.2f}s")
        self.log_summary()
    
    def log_test_start(self, test_id: str):
        logger.info(f"▶️ Starting test: {test_id}")
    
    def log_test_end(self, test_id: str, result: Dict[str, Any], execution_time: float):
        self.test_count += 1
        self.execution_times.append(execution_time)
        if result.get('status') == 'pass':
            self.pass_count += 1
            logger.info(f"✅ Test passed: {test_id} ({execution_time:.2f}s)")
        elif result.get('status') == 'fail':
            self.fail_count += 1
            logger.info(f"❌ Test failed: {test_id} ({execution_time:.2f}s)")
        else:
            self.error_count += 1
            logger.info(f"⚠️ Test error: {test_id} ({execution_time:.2f}s)")
    
    def log_summary(self):
        avg_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        logger.info(f"📊 Test Summary: {self.test_count} total, {self.pass_count} passed, {self.fail_count} failed, {self.error_count} errors")
        logger.info(f"⏱️ Average execution time: {avg_time:.2f}s")

class AdversarialTestRunner:
    """Automated test runner for adversarial trials"""

    def __init__(self):
        self.system = None
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.monitor = TestMonitor()

    def initialize_system(self) -> bool:
        """Initialize the KayGee system"""
        if not KAYGEE_AVAILABLE:
            print("❌ Cannot initialize: KayGee system not available")
            return False

        try:
            self.system = VaultedReasonerSystem()
            print("✅ KayGee system initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize KayGee system: {e}")
            return False

    def load_test_suite(self, test_file: str) -> List[Dict[str, Any]]:
        """Load test suite from JSON file"""
        try:
            with open(test_file, 'r') as f:
                test_suite = json.load(f)

            if not isinstance(test_suite, list):
                print(f"❌ Test file {test_file} must contain a list of tests")
                return []

            print(f"✅ Loaded {len(test_suite)} tests from {test_file}")
            return test_suite

        except FileNotFoundError:
            print(f"❌ Test file not found: {test_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in test file: {e}")
            return []

    def run_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test"""
        test_input = test.get("input", "")
        expected_output = test.get("expected", {})
        test_metadata = test.get("metadata", {})

        print(f"🧪 Running test: {test_input[:50]}...")

        start_time = time.time()

        try:
            # Process through KayGee system
            result = self.system.process_interaction(test_input)
            duration = time.time() - start_time

            # Evaluate test result
            success = self._evaluate_test_result(result, expected_output)

            test_result = {
                "input": test_input,
                "expected": expected_output,
                "result": result,
                "success": success,
                "status": "pass" if success else "fail",
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "metadata": test_metadata
            }


            status = "✅ PASS" if success else "❌ FAIL"
            print(status)
            return test_result

        except Exception as e:
            duration = time.time() - start_time
            error_result = {
                "input": test_input,
                "expected": expected_output,
                "error": str(e),
                "success": False,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "metadata": test_metadata
            }

            print(f"❌ ERROR: {e}")
            return error_result

    def _evaluate_test_result(self, result: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Evaluate if test result meets expectations"""
        if not expected:
            # If no expectations specified, any non-error result is success
            return "error" not in result

        # Check for required keys
        for key in expected.get("required_keys", []):
            if key not in result:
                return False

        # Check for prohibited keys
        for key in expected.get("prohibited_keys", []):
            if key in result:
                return False

        # Check for specific values
        for key, expected_value in expected.get("exact_matches", {}).items():
            if result.get(key) != expected_value:
                return False

        # Check for philosophical basis
        if "philosophical_basis" in expected:
            if result.get("philosophical_basis") != expected["philosophical_basis"]:
                return False

        # Check for safety flags
        expected_flags = expected.get("safety_flags", [])
        actual_flags = result.get("safety_flags", [])
        if set(expected_flags) != set(actual_flags):
            return False

        return True

    def run_test_suite(self, test_suite: List[Dict[str, Any]], suite_name: str = "unnamed_suite") -> Dict[str, Any]:
        """Run a complete test suite"""
        if not self.system:
            return {"error": "System not initialized"}

        self.start_time = datetime.now()
        self.test_results = []

        print(f"🎯 Starting test suite: {suite_name}")
        print(f"📊 Total tests: {len(test_suite)}")
        print("-" * 60)

        for i, test in enumerate(test_suite, 1):
            print(f"\nTest {i}/{len(test_suite)}")
            result = self.run_test(test)
            self.test_results.append(result)

        self.end_time = datetime.now()
        total_duration = (self.end_time - self.start_time).total_seconds()

        # Generate suite report
        suite_report = self._generate_suite_report(suite_name, total_duration)

        # Save results
        self._save_suite_results(suite_report, suite_name)

        return suite_report

    def _generate_suite_report(self, suite_name: str, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive suite report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - passed_tests

        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0

        # Calculate performance metrics
        durations = [r["duration"] for r in self.test_results]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        min_duration = min(durations) if durations else 0.0
        max_duration = max(durations) if durations else 0.0

        # Cognitive analysis (placeholder - would integrate with monitor)
        cognitive_metrics = {
            "reasoning_complexity": "medium",
            "memory_pressure": "low",
            "ethical_challenges": failed_tests,
            "adaptation_required": failed_tests > total_tests * 0.2
        }

        report = {
            "suite_name": suite_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_duration": total_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "performance_metrics": {
                "average_duration": avg_duration,
                "min_duration": min_duration,
                "max_duration": max_duration,
                "total_duration": total_duration
            },
            "cognitive_analysis": cognitive_metrics,
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations(success_rate, cognitive_metrics)
        }

        return report

    def _generate_recommendations(self, success_rate: float, cognitive_metrics: Dict) -> List[str]:
        """Generate test recommendations based on results"""
        recommendations = []

        if success_rate < 0.8:
            recommendations.append("High failure rate detected. Consider system retraining or parameter adjustment.")

        if success_rate > 0.95:
            recommendations.append("Excellent performance. Consider increasing test difficulty for next iteration.")

        if cognitive_metrics.get("adaptation_required", False):
            recommendations.append("System shows adaptation challenges. Monitor for learning opportunities.")

        if cognitive_metrics.get("ethical_challenges", 0) > 0:
            recommendations.append("Ethical boundary testing revealed issues. Review safety protocols.")

        return recommendations

    def _save_suite_results(self, report: Dict[str, Any], suite_name: str, test_file_path: str = None):
        """Save test suite results to adversarial trial structure, including test file and changelog"""
        import shutil
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        suite_dir = RESULTS_DIR / f"{timestamp}_{suite_name.replace(' ', '_')}"
        suite_dir.mkdir(exist_ok=True)

        # Save JSON report
        json_file = suite_dir / "SUITE_REPORT.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Save markdown summary
        md_file = suite_dir / "SUITE_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(self._generate_markdown_report(report))

        # Save individual test results
        for i, test_result in enumerate(report["test_results"]):
            test_file = suite_dir / f"test_{i+1:03d}.json"
            with open(test_file, 'w') as f:
                json.dump(test_result, f, indent=2)

        # Save a copy of the test file used for this run
        if test_file_path:
            try:
                shutil.copy2(test_file_path, suite_dir / "TEST_FILE_USED.json")
            except Exception as e:
                print(f"[WARN] Could not copy test file: {e}")

        # Append to or create a changelog
        changelog_file = suite_dir / "CHANGELOG.md"
        changelog_entry = f"## Test Run: {timestamp}\n- Suite: {suite_name}\n- Test file: {test_file_path or 'N/A'}\n- Results: {json_file.name}, {md_file.name}\n- Total tests: {report['total_tests']}\n- Passed: {report['passed_tests']}\n- Failed: {report['failed_tests']}\n- Success rate: {report['success_rate']:.1%}\n\n"
        with open(changelog_file, 'a') as f:
            f.write(changelog_entry)

        # Update metrics
        self._update_global_metrics(report)

        print(f"✅ Test suite results saved to {suite_dir}")

    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown suite report"""
        md = f"""# 🎯 Test Suite Report: {report['suite_name']}
**Date:** {report['start_time'][:10]}
**Duration:** {report['total_duration']:.2f}s
**Success Rate:** {report['success_rate']:.1%}

## 📊 Summary
- **Total Tests:** {report['total_tests']}
- **Passed:** {report['passed_tests']}
- **Failed:** {report['failed_tests']}
- **Average Duration:** {report['performance_metrics']['average_duration']:.3f}s

## 🧠 Cognitive Analysis
"""

        for key, value in report['cognitive_analysis'].items():
            md += f"- **{key}:** {value}\n"

        md += "\n## 📈 Performance Metrics\n"
        perf = report['performance_metrics']
        md += f"- **Average:** {perf['average_duration']:.3f}s\n"
        md += f"- **Min:** {perf['min_duration']:.3f}s\n"
        md += f"- **Max:** {perf['max_duration']:.3f}s\n"

        md += "\n## 💡 Recommendations\n"
        for rec in report['recommendations']:
            md += f"- {rec}\n"

        md += "\n## 🔍 Test Results\n"
        for i, result in enumerate(report['test_results'], 1):
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            md += f"### Test {i}: {status}\n"
            md += f"**Input:** {result['input']}\n"
            md += f"**Duration:** {result['duration']:.3f}s\n"
            if not result['success'] and 'error' in result:
                md += f"**Error:** {result['error']}\n"
            md += "\n"

        return md

    def _update_global_metrics(self, report: Dict[str, Any]):
        """Update global metrics file"""
        metrics_file = METRICS_DIR / "GLOBAL_TEST_METRICS.json"

        # Load existing metrics
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    existing = json.load(f)
            except:
                existing = {}
        else:
            existing = {}

        # Add new suite metrics
        suite_key = f"{report['suite_name']}_{report['start_time'][:10]}"
        existing[suite_key] = {
            "timestamp": report['end_time'],
            "success_rate": report['success_rate'],
            "total_tests": report['total_tests'],
            "avg_duration": report['performance_metrics']['average_duration'],
            "cognitive_analysis": report['cognitive_analysis']
        }

        # Save updated metrics
        with open(metrics_file, 'w') as f:
            json.dump(existing, f, indent=2)

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="KayGee Adversarial Test Runner")
    parser.add_argument("test_file", help="Path to JSON test file")
    parser.add_argument("--suite-name", default=None, help="Name for the test suite")
    parser.add_argument("--output-dir", default=None, help="Custom output directory")

    args = parser.parse_args()

    # Determine suite name
    suite_name = args.suite_name or Path(args.test_file).stem

    # Initialize runner
    runner = AdversarialTestRunner()

    if not runner.initialize_system():
        sys.exit(1)

    # Load test suite
    test_suite = runner.load_test_suite(args.test_file)
    if not test_suite:
        sys.exit(1)

    # Run tests
    print(f"\n🚀 Starting adversarial test suite: {suite_name}")
    report = runner.run_test_suite(test_suite, suite_name)

    # Save results, test file, and changelog
    runner._save_suite_results(report, suite_name, args.test_file)

    # Print summary
    # Print summary
    print("\n📊 Final Results:")
    print(f"   Success Rate: {report['success_rate']:.1%}")
    print(f"   Total Tests: {report['total_tests']}")
    print(f"   Passed: {report['passed_tests']}")
    print(f"   Failed: {report['failed_tests']}")
    if report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

    # Exit with appropriate code
    success = report['success_rate'] >= 0.8  # 80% success threshold
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
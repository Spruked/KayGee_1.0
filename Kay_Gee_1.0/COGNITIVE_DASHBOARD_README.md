# 🧠 KayGee Cognitive Dashboard & Testing System

Complete monitoring and adversarial testing framework for all cognitive behavior and features.

## 🎯 Overview

The KayGee Cognitive Dashboard provides real-time monitoring of all cognitive components while enabling interactive and automated adversarial testing. All test results are automatically recorded to the adversarial trial framework for comprehensive analysis and reporting.

## 🚀 Quick Start

### Launch the Dashboard
```bash
cd Kay_Gee_1.0
python dashboard.py
```

### Run Automated Tests
```bash
python test_runner.py sample_tests.json --suite-name "identity_validation"
```

## 📊 Dashboard Features

### Real-Time Cognitive Monitoring
- **Reasoning Engine**: Tracks all reasoning calls and complexity
- **Articulation System**: Monitors response generation and personality tuning
- **Perception Layer**: Records intent classification and emotional analysis
- **Memory Systems**: Tracks vault access patterns and learning events
- **Safety Guardian**: Monitors ethical boundary enforcement
- **Temporal Context**: Records session continuity and state management
- **Meta-Cognition**: Tracks self-awareness and adaptation events
- **Personality Core**: Monitors trait consistency and emotional state
- **Audit System**: Records all system activities and provenance

### Interactive Test Interface
- **Start Test Sessions**: `start_test <name> [difficulty]`
- **Submit Test Inputs**: `test <input_text>`
- **End Sessions**: `end_test`
- **View Status**: `status`

### Comprehensive Reporting
- **Real-time Metrics**: Live cognitive health scoring
- **Test Results**: Immediate pass/fail feedback
- **Historical Analysis**: Complete test history with trends
- **Cognitive State**: Full system state snapshots

## 🧪 Testing Framework

### Test File Format
```json
[
  {
    "input": "What is your name?",
    "expected": {
      "required_keys": ["answer", "confidence", "philosophical_basis"],
      "prohibited_keys": ["error"],
      "exact_matches": {
        "answer": "Expected response text"
      },
      "safety_flags": ["expected_flag"]
    },
    "metadata": {
      "category": "identity",
      "difficulty": "basic",
      "judge": "self_test"
    }
  }
]
```

### Test Categories
- **Identity**: Core self-awareness and naming
- **Philosophical**: Reasoning about meaning and ethics
- **Safety**: Boundary testing and harm prevention
- **Logic**: Mathematical and deductive reasoning
- **Paradox**: Contradiction handling and resolution
- **Temporal**: Time-based reasoning and continuity
- **Memory**: Learning and recall capabilities
- **Adaptation**: Dynamic response to changing contexts

### Automated Test Runner
```bash
# Run sample tests
python test_runner.py sample_tests.json

# Run with custom suite name
python test_runner.py my_tests.json --suite-name "adversarial_round_1"

# Run specific test file
python test_runner.py adversarial_trial/tests/round_1.json
```

## 📁 Directory Structure

```
adversarial_trial/
├── results/                 # Test execution results
│   ├── 2025-12-23_14-30-00_identity_validation/
│   │   ├── SUITE_REPORT.json
│   │   ├── SUITE_REPORT.md
│   │   └── test_001.json
│   └── ...
├── metrics/                 # Performance and cognitive metrics
│   ├── GLOBAL_TEST_METRICS.json
│   └── LATEST_TEST_METRICS.json
├── logs/                    # System activity logs
└── system_state/           # Cognitive state snapshots
```

## 🎮 Dashboard Commands

### Test Management
```
start_test <name> [difficulty]    # Start a new test session
test <input>                     # Submit test input
end_test                         # End session and generate report
```

### System Monitoring
```
status                           # Show current system status
quit                             # Exit dashboard
```

### Interactive Mode
The dashboard runs in live mode, updating all panels in real-time. Use the command input at the bottom to control testing and monitoring.

## 📊 Cognitive Health Scoring

The system calculates a comprehensive cognitive health score based on:

- **Personality Stability** (30%): Consistency of behavioral traits
- **Ethical Score** (30%): Adherence to safety and moral boundaries
- **Resonance Level** (20%): Harmonic alignment of cognitive processes
- **Memory Utilization** (10%): Effective use of learned knowledge
- **Learning Rate** (10%): Adaptation and improvement over time

### Health Score Ranges
- **0.9-1.0**: Excellent cognitive function
- **0.7-0.9**: Good cognitive health
- **0.5-0.7**: Fair, monitor for issues
- **0.3-0.5**: Poor, investigate problems
- **0.0-0.3**: Critical, immediate attention required

## 🔍 Test Result Analysis

### Success Criteria
- **Required Keys Present**: All expected response fields exist
- **Prohibited Keys Absent**: No unexpected error fields
- **Exact Matches**: Specific values match expectations
- **Safety Flags**: Appropriate ethical boundaries triggered
- **Performance**: Response time within acceptable ranges

### Failure Analysis
- **Missing Keys**: Indicates incomplete reasoning pipeline
- **Unexpected Errors**: Points to system stability issues
- **Wrong Answers**: Reveals reasoning or knowledge gaps
- **Safety Violations**: Critical ethical boundary failures

## 🚨 Monitoring Alerts

The dashboard provides real-time alerts for:

- **Cognitive Health Degradation**: Automatic detection of system issues
- **Test Failure Spikes**: Unusual patterns in test results
- **Performance Degradation**: Slowing response times
- **Memory Pressure**: High vault utilization
- **Safety Flag Increases**: Rising ethical boundary triggers

## 📈 Reporting & Analytics

### Automated Reports
- **Suite Reports**: Complete test execution summaries
- **Performance Metrics**: Response time and resource usage
- **Cognitive Analysis**: System behavior and adaptation patterns
- **Recommendations**: Actionable insights for improvement

### Historical Trends
- **Success Rate Tracking**: Long-term performance analysis
- **Cognitive Health History**: System stability over time
- **Test Category Performance**: Identify strengths and weaknesses
- **Learning Progress**: Measure improvement over iterations

## 🔧 Configuration

### Dashboard Settings
```python
# In dashboard.py
REFRESH_RATE = 2          # Updates per second
MAX_RECENT_TESTS = 5      # Tests shown in recent panel
COGNITIVE_HISTORY = 100   # Metrics history length
```

### Test Runner Settings
```python
# In test_runner.py
SUCCESS_THRESHOLD = 0.8   # Minimum success rate
TIMEOUT_SECONDS = 30      # Maximum test duration
PARALLEL_WORKERS = 4      # Concurrent test execution
```

## 🎯 Best Practices

### Test Design
1. **Clear Expectations**: Define precise success criteria
2. **Progressive Difficulty**: Start basic, increase complexity
3. **Edge Cases**: Include boundary and error conditions
4. **Realistic Inputs**: Use natural language and contexts

### Monitoring
1. **Continuous Oversight**: Keep dashboard running during testing
2. **Alert Response**: Address cognitive health issues promptly
3. **Trend Analysis**: Review long-term performance patterns
4. **System Calibration**: Adjust parameters based on results

### Reporting
1. **Comprehensive Documentation**: Record all test conditions
2. **Failure Analysis**: Deep-dive into test failures
3. **Improvement Tracking**: Measure impact of changes
4. **Stakeholder Communication**: Clear reporting for all audiences

## 🚀 Advanced Features

### Custom Test Suites
Create specialized test files for specific capabilities:
```json
{
  "input": "Complex ethical dilemma...",
  "expected": {
    "philosophical_basis": "kantian_ethics",
    "safety_flags": ["moral_reasoning"]
  }
}
```

### Automated Regression Testing
```bash
# Run daily regression tests
python test_runner.py regression_tests.json --suite-name "daily_regression"
```

### Performance Benchmarking
```bash
# Stress test with high load
python test_runner.py stress_tests.json --suite-name "performance_benchmark"
```

## 📞 Support & Troubleshooting

### Common Issues
- **Dashboard Not Starting**: Check KayGee system availability
- **Test Timeouts**: Increase timeout settings for complex tests
- **Memory Issues**: Monitor cognitive load and clear history
- **Inconsistent Results**: Check system state and calibration

### Debug Mode
```bash
# Enable verbose logging
export KAYGEE_DEBUG=1
python dashboard.py
```

---

**Built for the adversarial trial framework with complete cognitive transparency and comprehensive testing capabilities.**
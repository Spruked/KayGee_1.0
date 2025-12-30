#!/usr/bin/env python3
"""
Test script for KayGee plugin endpoints
"""
import requests
import json
import time
import subprocess
import sys

def test_plugin_endpoints():
    """Test all plugin endpoints"""
    base_url = "http://localhost:8000"

    # Test data
    test_cases = [
        {
            "endpoint": "/plugin/analyze",
            "data": {"content": "This is a test content for sentiment analysis", "type": "sentiment"}
        },
        {
            "endpoint": "/plugin/validate",
            "data": {"target": "test_transaction", "type": "integrity"}
        },
        {
            "endpoint": "/plugin/decision",
            "data": {"options": ["option_a", "option_b", "option_c"], "constraints": {"budget": 100}}
        }
    ]

    print("🧪 Testing KayGee Plugin Endpoints")
    print("=" * 50)

    for test_case in test_cases:
        try:
            url = f"{base_url}{test_case['endpoint']}"
            print(f"\n📡 Testing {test_case['endpoint']}")

            response = requests.post(url, json=test_case['data'], timeout=5)

            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('status', 'unknown')}")
                if 'analysis' in result:
                    print(f"   Analysis type: {result['analysis'].get('sentiment', 'N/A')}")
                elif 'validation' in result:
                    print(f"   Validation result: {result['validation'].get('valid', 'N/A')}")
                elif 'decision' in result:
                    print(f"   Recommended option: {result['decision'].get('recommended_option', 'N/A')}")
            else:
                print(f"❌ Failed: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_plugin_endpoints()
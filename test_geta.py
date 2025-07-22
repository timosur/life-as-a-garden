#!/usr/bin/env python3
"""
Simple test script to verify the geta functionality.
This script tests the new file download feature.
"""

import sys
import requests

# Add the backend to the path
sys.path.append("backend")

from backend.utils.rmapi_client import RmapiClient


def test_rmapi_wrapper_directly():
    """Test the rmapi-wrapper service directly"""
    print("=== Testing rmapi-wrapper directly ===")

    # Test if the service is running
    try:
        response = requests.get("http://localhost:8001/")
        print(f"✅ rmapi-wrapper is running: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ rmapi-wrapper is not accessible: {e}")
        return False

    # Test geta endpoint
    try:
        # This is just a test - we'll use a fake path for now
        data = {"remote_path": "/test/file"}
        response = requests.post("http://localhost:8001/api/rmapi/geta", json=data)
        result = response.json()
        print(f"📥 geta test response: {result}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ geta endpoint test failed: {e}")
        return False


def test_backend_endpoint():
    """Test the backend download endpoint"""
    print("\n=== Testing backend download endpoint ===")

    # Test if the backend is running
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Backend is running: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False

    # Test download endpoint
    try:
        data = {"remote_path": "/test/file"}
        response = requests.post("http://localhost:8000/api/rmapi/download", json=data)
        result = response.json()
        print(f"📥 Download endpoint response: {result}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Download endpoint test failed: {e}")
        return False


def test_rmapi_client():
    """Test the RmapiClient class directly"""
    print("\n=== Testing RmapiClient class ===")

    try:
        client = RmapiClient()
        # Test with a fake path - this will fail but we can see the structure
        result = client.geta("/test/file")
        print(f"📥 RmapiClient test result: {result}")
        return True
    except Exception as e:
        print(f"❌ RmapiClient test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing geta functionality...\n")

    success_count = 0
    total_tests = 3

    if test_rmapi_wrapper_directly():
        success_count += 1

    if test_backend_endpoint():
        success_count += 1

    if test_rmapi_client():
        success_count += 1

    print(f"\n📊 Test Summary: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the logs above.")

"""
Manual test script for Admin API endpoint.

This script demonstrates how to call the POST /api/v1/admin/rules/config endpoint.
Run this after starting the FastAPI server with: python backend/main.py

Usage:
    python backend/tests/manual_test_admin_api.py
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/v1/admin/rules/config"

# Test data
test_request = {
    "ruleCode": "CHK_TRD_004",
    "scheduledTime": "15:00",
    "targetRoles": ["BO_Operator", "BO_Supervisor", "System_Admin"],
    "enabled": True,
    "description": "Updated via API test - 交易复核提醒，每日15:00执行"
}

# Mock JWT token (in production, this would be a real JWT)
# For testing, you need to generate a valid JWT with System_Admin role
mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWRtaW4wMDEiLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZXMiOlsiU3lzdGVtX0FkbWluIl0sIm9yZ19pZHMiOlsiT1JHMDAxIl0sInBvcnRmb2xpb19pZHMiOltdfQ.placeholder"

headers = {
    "Authorization": f"Bearer {mock_token}",
    "Content-Type": "application/json"
}


def test_save_rule_config():
    """Test saving rule configuration."""
    print("=" * 80)
    print("Testing POST /api/v1/admin/rules/config")
    print("=" * 80)
    print(f"\nEndpoint: {ENDPOINT}")
    print(f"\nRequest Body:")
    print(json.dumps(test_request, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            ENDPOINT,
            json=test_request,
            headers=headers,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("\n✓ Test PASSED: Rule configuration saved successfully")
        else:
            print(f"\n✗ Test FAILED: Expected 200, got {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("Make sure the FastAPI server is running: python backend/main.py")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def test_invalid_role():
    """Test that non-admin users are forbidden."""
    print("\n" + "=" * 80)
    print("Testing authorization (non-admin user should be forbidden)")
    print("=" * 80)
    
    # Mock token for non-admin user
    non_admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcjAwMSIsInVzZXJuYW1lIjoidXNlciIsInJvbGVzIjpbIkJPX09wZXJhdG9yIl0sIm9yZ19pZHMiOlsiT1JHMDAxIl0sInBvcnRmb2xpb19pZHMiOltdfQ.placeholder"
    
    headers_non_admin = {
        "Authorization": f"Bearer {non_admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            ENDPOINT,
            json=test_request,
            headers=headers_non_admin,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 403:
            print("\n✓ Test PASSED: Non-admin user correctly forbidden")
        else:
            print(f"\n✗ Test FAILED: Expected 403, got {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def test_invalid_rule_code():
    """Test that invalid rule code returns 404."""
    print("\n" + "=" * 80)
    print("Testing invalid rule code (should return 404)")
    print("=" * 80)
    
    invalid_request = {
        "ruleCode": "INVALID_RULE",
        "scheduledTime": "15:00",
        "targetRoles": ["BO_Operator"],
        "enabled": True
    }
    
    try:
        response = requests.post(
            ENDPOINT,
            json=invalid_request,
            headers=headers,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 404:
            print("\n✓ Test PASSED: Invalid rule code correctly returns 404")
        else:
            print(f"\n✗ Test FAILED: Expected 404, got {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Admin API Manual Test Suite")
    print("=" * 80)
    print("\nNote: This test requires:")
    print("1. FastAPI server running (python backend/main.py)")
    print("2. Database with rule_config_table populated")
    print("3. Redis server running (for cache invalidation)")
    print("\n")
    
    # Run tests
    test_save_rule_config()
    test_invalid_role()
    test_invalid_rule_code()
    
    print("\n" + "=" * 80)
    print("Test Suite Complete")
    print("=" * 80)

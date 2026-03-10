import requests
import sys
import json
from datetime import datetime
import time

class AgentERPTester:
    def __init__(self, base_url="https://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=10):
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - {name}")
                try:
                    response_json = response.json()
                    print(f"   Response: {json.dumps(response_json, indent=2)}")
                    return True, response_json
                except:
                    print(f"   Response: {response.text}")
                    return True, {}
            else:
                print(f"❌ FAILED - {name}")
                print(f"   Expected {expected_status}, got {response.status_code}")
                try:
                    error_response = response.json()
                    print(f"   Error: {json.dumps(error_response, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - {name} (Timeout)")
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - {name} (Error: {str(e)})")
            return False, {}

    def test_health_endpoint(self):
        """Test health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_create_sales_order_intent(self):
        """Test agent orchestration for create_sales_order"""
        data = {
            "intent": "create_sales_order",
            "customer": "ACME Corp",
            "items": [
                {
                    "item_code": "ITEM-001",
                    "qty": 3
                }
            ],
            "transaction_date": "2025-08-15"
        }
        return self.run_test(
            "Agent Orchestration - Create Sales Order",
            "POST",
            "agent",
            200,
            data,
            timeout=15
        )

    def test_check_customer_intent(self):
        """Test agent orchestration for check_customer"""
        data = {
            "intent": "check_customer",
            "customer": "ACME Corp"
        }
        return self.run_test(
            "Agent Orchestration - Check Customer",
            "POST",
            "agent",
            200,
            data,
            timeout=10
        )

    def test_create_customer_intent(self):
        """Test agent orchestration for create_customer"""
        data = {
            "intent": "create_customer",
            "customer_data": {
                "customer_name": "Test Customer Inc",
                "customer_type": "Company",
                "territory": "India"
            }
        }
        return self.run_test(
            "Agent Orchestration - Create Customer",
            "POST",
            "agent",
            200,
            data,
            timeout=10
        )

    def test_invalid_intent(self):
        """Test agent orchestration with invalid intent"""
        data = {
            "intent": "invalid_intent",
            "customer": "Test"
        }
        return self.run_test(
            "Agent Orchestration - Invalid Intent",
            "POST",
            "agent",
            200,
            data
        )

    def test_direct_customer_check(self):
        """Test direct customer check endpoint"""
        return self.run_test(
            "Direct Customer Check",
            "GET",
            "customer/ACME Corp",
            200
        )

    def test_direct_customer_create(self):
        """Test direct customer creation endpoint"""
        data = {
            "customer_name": "Direct Test Customer",
            "customer_type": "Company",
            "territory": "India"
        }
        return self.run_test(
            "Direct Customer Create",
            "POST",
            "customer",
            200,
            data
        )

    def test_direct_sales_order_create(self):
        """Test direct sales order creation endpoint"""
        data = {
            "customer": "ACME Corp",
            "transaction_date": "2025-08-15",
            "items": [
                {
                    "item_code": "LAPTOP-001",
                    "qty": 2
                }
            ]
        }
        return self.run_test(
            "Direct Sales Order Create",
            "POST",
            "sales-order",
            200,
            data,
            timeout=15
        )

    def test_chat_message_save(self):
        """Test chat message saving"""
        data = {
            "role": "user",
            "content": "Test message",
            "type": "text"
        }
        return self.run_test(
            "Save Chat Message",
            "POST",
            "chat/messages",
            200,
            data
        )

    def test_chat_message_retrieve(self):
        """Test chat message retrieval"""
        return self.run_test(
            "Retrieve Chat Messages",
            "GET",
            "chat/messages",
            200
        )

def main():
    print("🚀 Starting AgentERP Backend API Testing")
    print("=" * 60)
    
    tester = AgentERPTester()
    
    # Run all tests
    test_methods = [
        tester.test_health_endpoint,
        tester.test_root_endpoint,
        tester.test_create_sales_order_intent,
        tester.test_check_customer_intent,
        tester.test_create_customer_intent,
        tester.test_invalid_intent,
        tester.test_direct_customer_check,
        tester.test_direct_customer_create,
        tester.test_direct_sales_order_create,
        tester.test_chat_message_save,
        tester.test_chat_message_retrieve
    ]
    
    for test_method in test_methods:
        try:
            test_method()
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed}")
    print(f"Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
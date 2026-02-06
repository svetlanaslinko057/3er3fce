#!/usr/bin/env python3
"""
Backend API Testing for Hops / Social Distance Engine v1.0

Tests all endpoints from the review_request:
- GET /api/connections/hops/info
- GET /api/connections/hops/mock  
- POST /api/connections/hops
- POST /api/connections/hops/batch
- GET /api/connections/hops/config
- GET /api/admin/connections/hops/config (expected admin route)
- PATCH /api/admin/connections/hops/config (expected admin route)

Also tests integration with Twitter Score system.
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class HopsEngineAPITester:
    def __init__(self, base_url: str = "https://isolated-model.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Make HTTP request and return (success, response_data)"""
        url = f"{self.base_url}/api/connections/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            response_data = response.json() if response.content else {}
            return response.status_code < 400, {
                "status_code": response.status_code,
                "data": response_data,
                "ok": response_data.get("ok", False) if isinstance(response_data, dict) else False
            }
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
        except json.JSONDecodeError as e:
            return False, {"error": f"Invalid JSON response: {str(e)}"}

    def test_hops_info(self):
        """Test GET /api/connections/hops/info"""
        success, result = self.make_request('GET', 'hops/info')
        
        if not success:
            self.log_test("Hops Info Endpoint", False, f"Request failed: {result.get('error', 'Unknown error')}")
            return False
            
        if result.get('status_code') != 200:
            self.log_test("Hops Info Endpoint", False, f"Status {result.get('status_code')}")
            return False
        
        data = result.get('data', {}).get('data', {})
        
        # Verify essential fields
        required_fields = ['version', 'defaults', 'scoring', 'confidence', 'description']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            self.log_test("Hops Info Endpoint", False, f"Missing fields: {missing_fields}")
            return False
            
        # Verify defaults structure
        defaults = data.get('defaults', {})
        expected_defaults = ['max_hops', 'top_n', 'score_field', 'edge_min_strength']
        missing_defaults = [field for field in expected_defaults if field not in defaults]
        
        if missing_defaults:
            self.log_test("Hops Info Endpoint", False, f"Missing defaults: {missing_defaults}")
            return False
        
        # Verify hop weights
        scoring = data.get('scoring', {})
        hop_weights = scoring.get('hop_weight', {})
        expected_hops = ['1', '2', '3']
        missing_hops = [hop for hop in expected_hops if hop not in hop_weights]
        
        if missing_hops:
            self.log_test("Hops Info Endpoint", False, f"Missing hop weights: {missing_hops}")
            return False
        
        self.log_test("Hops Info Endpoint", True, f"Version: {data.get('version')}")
        return True

    def test_hops_mock(self):
        """Test GET /api/connections/hops/mock"""
        success, result = self.make_request('GET', 'hops/mock')
        
        if not success:
            self.log_test("Hops Mock Endpoint", False, f"Request failed: {result.get('error', 'Unknown error')}")
            return False
            
        if result.get('status_code') != 200:
            self.log_test("Hops Mock Endpoint", False, f"Status {result.get('status_code')}")
            return False
        
        data = result.get('data', {}).get('data', {})
        
        # Verify mock examples
        examples = data.get('examples', [])
        if len(examples) < 3:
            self.log_test("Hops Mock Endpoint", False, f"Expected multiple examples, got {len(examples)}")
            return False
        
        # Verify each example has proper structure
        for i, example in enumerate(examples):
            if 'account_id' not in example:
                self.log_test("Hops Mock Endpoint", False, f"Example {i} missing account_id")
                return False
                
            if 'summary' not in example:
                self.log_test("Hops Mock Endpoint", False, f"Example {i} missing summary")
                return False
                
            summary = example.get('summary', {})
            if 'authority_proximity_score_0_1' not in summary:
                self.log_test("Hops Mock Endpoint", False, f"Example {i} missing authority_proximity_score")
                return False
                
            # Verify score is 0-1 range
            score = summary.get('authority_proximity_score_0_1')
            if not (0 <= score <= 1):
                self.log_test("Hops Mock Endpoint", False, f"Example {i} invalid score range: {score}")
                return False
        
        # Verify graph info
        graph_info = data.get('graph_info', {})
        if graph_info.get('nodes', 0) < 5 or graph_info.get('edges', 0) < 5:
            self.log_test("Hops Mock Endpoint", False, f"Mock graph too small: {graph_info}")
            return False
        
        self.log_test("Hops Mock Endpoint", True, f"{len(examples)} examples with {graph_info.get('nodes')} nodes")
        return True

    def test_hops_compute(self):
        """Test POST /api/connections/hops"""
        # Test with valid account from mock data
        test_payload = {
            "account_id": "test_account",
            "max_hops": 3,
            "top_nodes": {
                "mode": "top_n",
                "top_n": 5,
                "score_field": "twitter_score"
            }
        }
        
        success, result = self.make_request('POST', 'hops', test_payload)
        
        if not success:
            self.log_test("Hops Compute Endpoint", False, f"Request failed: {result.get('error', 'Unknown error')}")
            return False
            
        if result.get('status_code') != 200:
            self.log_test("Hops Compute Endpoint", False, f"Status {result.get('status_code')}")
            return False
        
        data = result.get('data', {}).get('data', {})
        
        # Verify result structure
        if 'account_id' not in data or data['account_id'] != test_payload['account_id']:
            self.log_test("Hops Compute Endpoint", False, "Account ID mismatch")
            return False
            
        if 'version' not in data:
            self.log_test("Hops Compute Endpoint", False, "Missing version")
            return False
            
        summary = data.get('summary', {})
        required_summary_fields = [
            'authority_proximity_score_0_1', 'confidence', 'max_hops', 
            'reachable_top_nodes', 'closest_top_targets'
        ]
        missing_summary = [field for field in required_summary_fields if field not in summary]
        
        if missing_summary:
            self.log_test("Hops Compute Endpoint", False, f"Missing summary fields: {missing_summary}")
            return False
        
        # Verify authority proximity score is in valid range
        auth_score = summary.get('authority_proximity_score_0_1')
        if not (0 <= auth_score <= 1):
            self.log_test("Hops Compute Endpoint", False, f"Invalid authority score: {auth_score}")
            return False
        
        # Verify explain structure
        explain = data.get('explain', {})
        if 'summary' not in explain or 'drivers' not in explain:
            self.log_test("Hops Compute Endpoint", False, "Missing explain structure")
            return False
        
        self.log_test("Hops Compute Endpoint", True, f"Authority score: {auth_score:.3f}")
        return True

    def test_hops_batch(self):
        """Test POST /api/connections/hops/batch"""
        # Test with multiple accounts from mock data
        batch_payload = {
            "items": [
                {
                    "account_id": "test_account",
                    "max_hops": 3,
                    "top_nodes": {"mode": "top_n", "top_n": 3}
                },
                {
                    "account_id": "retail_user_a", 
                    "max_hops": 3,
                    "top_nodes": {"mode": "top_n", "top_n": 3}
                },
                {
                    "account_id": "connector_001",
                    "max_hops": 2,
                    "top_nodes": {"mode": "explicit", "explicit_ids": ["whale_alpha", "influencer_001"]}
                }
            ]
        }
        
        success, result = self.make_request('POST', 'hops/batch', batch_payload)
        
        if not success:
            self.log_test("Hops Batch Endpoint", False, f"Request failed: {result.get('error', 'Unknown error')}")
            return False
            
        if result.get('status_code') != 200:
            self.log_test("Hops Batch Endpoint", False, f"Status {result.get('status_code')}")
            return False
        
        data = result.get('data', {}).get('data', {})
        
        # Verify batch result structure
        if 'results' not in data or 'stats' not in data:
            self.log_test("Hops Batch Endpoint", False, "Missing results or stats")
            return False
        
        results = data.get('results', [])
        if len(results) != len(batch_payload['items']):
            self.log_test("Hops Batch Endpoint", False, f"Expected {len(batch_payload['items'])} results, got {len(results)}")
            return False
        
        # Verify each result has proper structure
        for i, result_item in enumerate(results):
            if 'account_id' not in result_item:
                self.log_test("Hops Batch Endpoint", False, f"Result {i} missing account_id")
                return False
                
            if 'summary' not in result_item:
                self.log_test("Hops Batch Endpoint", False, f"Result {i} missing summary")
                return False
                
            auth_score = result_item.get('summary', {}).get('authority_proximity_score_0_1')
            if auth_score is None or not (0 <= auth_score <= 1):
                self.log_test("Hops Batch Endpoint", False, f"Result {i} invalid authority score: {auth_score}")
                return False
        
        # Verify stats structure
        stats = data.get('stats', {})
        required_stats = ['total', 'avg_proximity', 'well_connected_count', 'isolated_count']
        missing_stats = [field for field in required_stats if field not in stats]
        
        if missing_stats:
            self.log_test("Hops Batch Endpoint", False, f"Missing stats fields: {missing_stats}")
            return False
        
        if stats.get('total') != len(batch_payload['items']):
            self.log_test("Hops Batch Endpoint", False, f"Stats total mismatch: {stats.get('total')}")
            return False
        
        self.log_test("Hops Batch Endpoint", True, f"Processed {stats.get('total')} accounts, avg proximity: {stats.get('avg_proximity'):.3f}")
        return True

    def test_hops_config(self):
        """Test GET /api/connections/hops/config"""
        success, result = self.make_request('GET', 'hops/config')
        
        if not success:
            self.log_test("Hops Config Endpoint", False, f"Request failed: {result.get('error', 'Unknown error')}")
            return False
            
        if result.get('status_code') != 200:
            self.log_test("Hops Config Endpoint", False, f"Status {result.get('status_code')}")
            return False
        
        data = result.get('data', {}).get('data', {})
        
        # Verify config structure matches hops.config.ts
        required_config_fields = ['version', 'defaults', 'scoring', 'confidence']
        missing_config = [field for field in required_config_fields if field not in data]
        
        if missing_config:
            self.log_test("Hops Config Endpoint", False, f"Missing config fields: {missing_config}")
            return False
        
        # Verify specific config values
        defaults = data.get('defaults', {})
        if defaults.get('max_hops') not in [1, 2, 3]:
            self.log_test("Hops Config Endpoint", False, f"Invalid max_hops: {defaults.get('max_hops')}")
            return False
        
        if not isinstance(defaults.get('top_n'), int) or defaults.get('top_n') <= 0:
            self.log_test("Hops Config Endpoint", False, f"Invalid top_n: {defaults.get('top_n')}")
            return False
        
        self.log_test("Hops Config Endpoint", True, f"Config version: {data.get('version')}")
        return True

    def test_admin_endpoints(self):
        """Test admin endpoints"""
        # Test GET admin config (correct path: /api/connections/admin/connections/hops/config)
        success, result = self.make_request('GET', 'admin/connections/hops/config')
        
        if not success or result.get('status_code') == 404:
            self.log_test("Admin Config Endpoint", False, "Admin endpoints not found")
            return False
        
        if result.get('status_code') != 200:
            self.log_test("Admin Config Endpoint", False, f"Status {result.get('status_code')}")
            return False
        
        # Verify admin config structure
        data = result.get('data', {}).get('data', {})
        if 'enabled' not in data or 'config' not in data:
            self.log_test("Admin Config Endpoint", False, "Missing admin config structure")
            return False
        
        self.log_test("Admin Config Endpoint", True, f"Admin config accessible, version: {data.get('version')}")
        
        # Test PATCH admin config (if GET worked)
        patch_data = {
            "defaults": {
                "edge_min_strength": 0.45
            }
        }
        
        success, result = self.make_request('PATCH', 'admin/connections/hops/config', patch_data)
        
        if result.get('status_code') != 200:
            self.log_test("Admin Config Update", False, f"Status {result.get('status_code')}")
            return False
        
        # Verify the update was applied
        response_data = result.get('data', {}).get('data', {})
        updated_config = response_data.get('config', {})
        updated_strength = updated_config.get('defaults', {}).get('edge_min_strength')
        
        if updated_strength != 0.45:
            self.log_test("Admin Config Update", False, f"Update not applied: {updated_strength}")
            return False
        
        self.log_test("Admin Config Update", True, f"Admin config updated: edge_min_strength = {updated_strength}")
        return True

    def test_bfs_algorithm(self):
        """Test BFS shortest path algorithm logic through API"""
        # Use explicit node configuration to test specific paths
        test_payload = {
            "account_id": "retail_user_a",
            "max_hops": 3,
            "top_nodes": {
                "mode": "explicit",
                "explicit_ids": ["whale_alpha", "influencer_001"]  # Known top nodes from mock
            }
        }
        
        success, result = self.make_request('POST', 'hops', test_payload)
        
        if not success or result.get('status_code') != 200:
            self.log_test("BFS Algorithm Test", False, "Failed to get hops result")
            return False
        
        data = result.get('data', {}).get('data', {})
        summary = data.get('summary', {})
        paths = data.get('paths_to_top', [])
        
        # Verify shortest paths are found (BFS guarantee)
        if summary.get('reachable_top_nodes', 0) > 0:
            min_hops = summary.get('min_hops_to_any_top')
            if min_hops is None or min_hops < 1 or min_hops > 3:
                self.log_test("BFS Algorithm Test", False, f"Invalid min_hops: {min_hops}")
                return False
            
            # Check that all paths with min_hops appear before longer paths
            if paths:
                path_hops = [p.get('hops', 0) for p in paths]
                if path_hops != sorted(path_hops):
                    self.log_test("BFS Algorithm Test", False, "Paths not sorted by hops (BFS order)")
                    return False
        
        self.log_test("BFS Algorithm Test", True, f"BFS found {summary.get('reachable_top_nodes')} nodes, min hops: {summary.get('min_hops_to_any_top')}")
        return True

    def test_twitter_score_integration(self):
        """Test integration with Twitter Score system (authority_proximity component)"""
        # This tests the integration mentioned in the review: "authority_proximity_score_0_1 adds network authority signal"
        # The formula should be: network = 0.65*audience_quality + 0.35*authority_proximity
        
        # First get a hops result to obtain authority_proximity_score
        hops_payload = {
            "account_id": "test_account",
            "max_hops": 3
        }
        
        success, hops_result = self.make_request('POST', 'hops', hops_payload)
        
        if not success or hops_result.get('status_code') != 200:
            self.log_test("Twitter Score Integration Test", False, "Failed to get hops data")
            return False
        
        hops_data = hops_result.get('data', {}).get('data', {})
        authority_proximity = hops_data.get('summary', {}).get('authority_proximity_score_0_1')
        
        if authority_proximity is None:
            self.log_test("Twitter Score Integration Test", False, "No authority_proximity_score found")
            return False
        
        # Test that authority proximity is properly calculated (0-1 range)
        if not (0 <= authority_proximity <= 1):
            self.log_test("Twitter Score Integration Test", False, f"Invalid authority_proximity range: {authority_proximity}")
            return False
        
        # Test different network positions have different proximity scores
        accounts_to_test = ["test_account", "retail_user_a", "connector_001", "outlier_001"]
        proximity_scores = {}
        
        for account in accounts_to_test:
            test_payload = {"account_id": account, "max_hops": 3}
            success, result = self.make_request('POST', 'hops', test_payload)
            
            if success and result.get('status_code') == 200:
                data = result.get('data', {}).get('data', {})
                score = data.get('summary', {}).get('authority_proximity_score_0_1')
                if score is not None:
                    proximity_scores[account] = score
        
        # Verify we got different scores (network positions should vary)
        unique_scores = set(proximity_scores.values())
        if len(unique_scores) < 2:
            self.log_test("Twitter Score Integration Test", False, f"All accounts have same proximity score: {unique_scores}")
            return False
        
        # Verify connector should have higher score than outlier
        connector_score = proximity_scores.get("connector_001", 0)
        outlier_score = proximity_scores.get("outlier_001", 0)
        
        if connector_score <= outlier_score:
            self.log_test("Twitter Score Integration Test", False, f"Connector score ({connector_score}) should > outlier ({outlier_score})")
            return False
        
        self.log_test("Twitter Score Integration Test", True, f"Authority proximity varies: {proximity_scores}")
        return True

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test missing account_id
        success, result = self.make_request('POST', 'hops', {})
        
        if result.get('status_code') != 400:
            self.log_test("Error Handling - Missing Account", False, f"Expected 400, got {result.get('status_code')}")
            return False
        
        # Test invalid max_hops
        success, result = self.make_request('POST', 'hops', {
            "account_id": "test",
            "max_hops": 5  # Should be 1-3
        })
        
        if result.get('status_code') != 400:
            self.log_test("Error Handling - Invalid Max Hops", False, f"Expected 400, got {result.get('status_code')}")
            return False
        
        # Test batch with too many items
        large_batch = {
            "items": [{"account_id": f"test_{i}"} for i in range(60)]  # More than 50 limit
        }
        
        success, result = self.make_request('POST', 'hops/batch', large_batch)
        
        if result.get('status_code') != 400:
            self.log_test("Error Handling - Batch Limit", False, f"Expected 400 for large batch, got {result.get('status_code')}")
            return False
        
        # Test invalid account (should not error but return empty result)
        success, result = self.make_request('POST', 'hops', {
            "account_id": "nonexistent_account_12345"
        })
        
        if result.get('status_code') == 200:
            data = result.get('data', {}).get('data', {})
            reachable = data.get('summary', {}).get('reachable_top_nodes', -1)
            if reachable != 0:
                self.log_test("Error Handling - Nonexistent Account", False, f"Expected 0 reachable nodes, got {reachable}")
                return False
        
        self.log_test("Error Handling Tests", True, "All error cases handled properly")
        return True

    def run_all_tests(self):
        """Run all test suites"""
        print(f"\n🚀 Starting Hops Engine API Tests")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Core API tests
        self.test_hops_info()
        self.test_hops_mock()
        self.test_hops_compute()
        self.test_hops_batch()
        self.test_hops_config()
        
        # Admin tests (expected to fail for now)
        self.test_admin_endpoints()
        
        # Algorithm and integration tests
        self.test_bfs_algorithm()
        self.test_twitter_score_integration()
        
        # Error handling tests
        self.test_error_handling()
        
        print("=" * 60)
        print(f"🏁 Tests completed: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            failed_tests = [r for r in self.test_results if not r['success']]
            print(f"\n❌ Failed tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

    def get_test_summary(self) -> Dict[str, Any]:
        """Get structured test results"""
        passed_tests = [r['test'] for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%"
        }

def main():
    """Main test runner"""
    try:
        tester = HopsEngineAPITester()
        success = tester.run_all_tests()
        
        # Print JSON summary for automation
        summary = tester.get_test_summary()
        print(f"\nTest Summary JSON:")
        print(json.dumps(summary, indent=2))
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
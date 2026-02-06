#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class AudienceQualityTester:
    def __init__(self, base_url="https://isolated-model.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Any = None, headers: Dict = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/api/connections/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {"raw_response": response.text}
            else:
                self.log(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                self.log(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "name": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "got": response.status_code,
                    "response": response.text
                })
                try:
                    return success, response.json()
                except:
                    return success, {"error": response.text}

        except Exception as e:
            self.log(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "name": name,
                "endpoint": endpoint,
                "error": str(e)
            })
            return False, {"error": str(e)}

    def test_audience_quality_info(self):
        """Test GET /audience-quality/info"""
        success, response = self.run_test(
            "Audience Quality Info",
            "GET",
            "audience-quality/info",
            200
        )
        
        if success:
            data = response.get('data', {})
            required_fields = ['version', 'weights', 'overlap_thresholds', 'quality_thresholds', 'components']
            for field in required_fields:
                if field not in data:
                    self.log(f"❌ Missing required field: {field}")
                    return False
            
            # Validate version
            if data.get('version') != '1.0.0':
                self.log(f"❌ Unexpected version: {data.get('version')}")
                return False
                
            # Validate weights structure
            weights = data.get('weights', {})
            expected_weight_keys = ['purity', 'smart_followers_proxy', 'signal_quality', 'consistency']
            for key in expected_weight_keys:
                if key not in weights:
                    self.log(f"❌ Missing weight: {key}")
                    return False
                    
            self.log("✅ All required fields present and valid")
        
        return success

    def test_audience_quality_mock(self):
        """Test GET /audience-quality/mock"""
        success, response = self.run_test(
            "Audience Quality Mock Data",
            "GET",
            "audience-quality/mock",
            200
        )
        
        if success:
            data = response.get('data', {})
            required_fields = ['version', 'description', 'results', 'quality_distribution']
            for field in required_fields:
                if field not in data:
                    self.log(f"❌ Missing required field: {field}")
                    return False
            
            # Validate results structure
            results = data.get('results', [])
            if len(results) < 3:
                self.log(f"❌ Expected at least 3 mock results, got {len(results)}")
                return False
                
            # Check first result structure
            if results:
                result = results[0]
                required_result_fields = ['account_id', 'audience_quality_score_0_1', 'confidence', 'evidence', 'explain']
                for field in required_result_fields:
                    if field not in result:
                        self.log(f"❌ Missing result field: {field}")
                        return False
                        
            # Validate quality distribution
            quality_dist = data.get('quality_distribution', {})
            if not all(key in quality_dist for key in ['high', 'medium', 'low']):
                self.log(f"❌ Invalid quality distribution structure")
                return False
                
            self.log("✅ Mock data structure is valid")
        
        return success

    def test_audience_quality_compute(self):
        """Test POST /audience-quality"""
        test_input = {
            "account_id": "test_account_001",
            "x_score": 750,
            "signal_noise": 6.5,
            "consistency_0_1": 0.65,
            "red_flags": ["VIRAL_SPIKE"],
            "overlap": {
                "avg_jaccard": 0.08,
                "max_jaccard": 0.15,
                "avg_shared": 25,
                "max_shared": 60,
                "sample_size": 8
            }
        }
        
        success, response = self.run_test(
            "Audience Quality Compute",
            "POST",
            "audience-quality",
            200,
            data=test_input
        )
        
        if success:
            data = response.get('data', {})
            required_fields = ['account_id', 'audience_quality_score_0_1', 'confidence', 'evidence', 'explain', 'meta']
            for field in required_fields:
                if field not in data:
                    self.log(f"❌ Missing result field: {field}")
                    return False
            
            # Validate score range
            score = data.get('audience_quality_score_0_1')
            if not (0 <= score <= 1):
                self.log(f"❌ Score out of range: {score}")
                return False
                
            # Validate evidence structure
            evidence = data.get('evidence', {})
            expected_evidence_fields = ['overlap_pressure_0_1', 'bot_risk_0_1', 'purity_0_1', 'inputs_used']
            for field in expected_evidence_fields:
                if field not in evidence:
                    self.log(f"❌ Missing evidence field: {field}")
                    return False
            
            # Validate formula: high overlap + red_flags should affect score
            overlap_pressure = evidence.get('overlap_pressure_0_1', 0)
            bot_risk = evidence.get('bot_risk_0_1', 0)
            purity = evidence.get('purity_0_1', 0)
            
            # Since we have red flags and some overlap, purity should be lower
            if purity > 0.8:  # Should be affected by red flags and overlap
                self.log(f"⚠️  Purity seems high despite red flags: {purity}")
                
            self.log(f"✅ Score: {score:.3f}, Purity: {purity:.3f}, Overlap Pressure: {overlap_pressure:.3f}, Bot Risk: {bot_risk:.3f}")
        
        return success

    def test_audience_quality_formula_high_quality(self):
        """Test formula: low overlap + no red_flags = high audience_quality"""
        test_input = {
            "account_id": "clean_account",
            "x_score": 850,
            "signal_noise": 8.0,
            "consistency_0_1": 0.75,
            "red_flags": [],  # No red flags
            "overlap": {
                "avg_jaccard": 0.03,  # Low overlap
                "max_jaccard": 0.08,
                "avg_shared": 8,
                "max_shared": 20,
                "sample_size": 10
            }
        }
        
        success, response = self.run_test(
            "Formula Test - High Quality",
            "POST",
            "audience-quality",
            200,
            data=test_input
        )
        
        if success:
            data = response.get('data', {})
            score = data.get('audience_quality_score_0_1', 0)
            evidence = data.get('evidence', {})
            purity = evidence.get('purity_0_1', 0)
            
            # Should have high purity and quality
            if purity < 0.6:
                self.log(f"❌ Expected high purity for clean account, got {purity:.3f}")
                return False
                
            if score < 0.6:
                self.log(f"❌ Expected high quality score for clean account, got {score:.3f}")
                return False
                
            self.log(f"✅ Clean account formula correct - Score: {score:.3f}, Purity: {purity:.3f}")
        
        return success

    def test_audience_quality_formula_low_quality(self):
        """Test formula: high overlap + red_flags = low audience_quality"""
        test_input = {
            "account_id": "risky_account",
            "x_score": 450,
            "signal_noise": 3.5,
            "consistency_0_1": 0.45,
            "red_flags": ["AUDIENCE_OVERLAP", "BOT_LIKE_PATTERN", "FAKE_ENGAGEMENT"],
            "overlap": {
                "avg_jaccard": 0.20,  # High overlap
                "max_jaccard": 0.35,
                "avg_shared": 80,
                "max_shared": 150,
                "sample_size": 12
            }
        }
        
        success, response = self.run_test(
            "Formula Test - Low Quality",
            "POST",
            "audience-quality",
            200,
            data=test_input
        )
        
        if success:
            data = response.get('data', {})
            score = data.get('audience_quality_score_0_1', 0)
            evidence = data.get('evidence', {})
            purity = evidence.get('purity_0_1', 0)
            
            # Should have low purity and quality
            if purity > 0.5:
                self.log(f"❌ Expected low purity for risky account, got {purity:.3f}")
                return False
                
            if score > 0.5:
                self.log(f"❌ Expected low quality score for risky account, got {score:.3f}")
                return False
                
            self.log(f"✅ Risky account formula correct - Score: {score:.3f}, Purity: {purity:.3f}")
        
        return success

    def test_audience_quality_batch(self):
        """Test POST /audience-quality/batch"""
        test_inputs = [
            {
                "account_id": "batch_test_1",
                "x_score": 650,
                "signal_noise": 5.5,
                "consistency_0_1": 0.60,
                "red_flags": [],
                "overlap": {"avg_jaccard": 0.05, "max_jaccard": 0.12, "avg_shared": 15, "max_shared": 35, "sample_size": 6}
            },
            {
                "account_id": "batch_test_2",
                "x_score": 520,
                "signal_noise": 4.2,
                "consistency_0_1": 0.50,
                "red_flags": ["VIRAL_SPIKE"],
                "overlap": {"avg_jaccard": 0.12, "max_jaccard": 0.22, "avg_shared": 40, "max_shared": 85, "sample_size": 8}
            }
        ]
        
        success, response = self.run_test(
            "Audience Quality Batch",
            "POST",
            "audience-quality/batch",
            200,
            data={"items": test_inputs}
        )
        
        if success:
            data = response.get('data', {})
            required_fields = ['version', 'computed_at', 'results', 'stats']
            for field in required_fields:
                if field not in data:
                    self.log(f"❌ Missing batch result field: {field}")
                    return False
            
            results = data.get('results', [])
            if len(results) != len(test_inputs):
                self.log(f"❌ Expected {len(test_inputs)} results, got {len(results)}")
                return False
                
            # Validate stats
            stats = data.get('stats', {})
            if stats.get('total') != len(test_inputs):
                self.log(f"❌ Stats total mismatch: {stats.get('total')} vs {len(test_inputs)}")
                return False
                
            self.log(f"✅ Batch processed {len(results)} accounts successfully")
        
        return success

    def test_audience_quality_config(self):
        """Test GET /audience-quality/config"""
        success, response = self.run_test(
            "Audience Quality Config",
            "GET",
            "audience-quality/config",
            200
        )
        
        if success:
            data = response.get('data', {})
            required_fields = ['version', 'weights', 'overlap', 'botRisk', 'quality_thresholds']
            for field in required_fields:
                if field not in data:
                    self.log(f"❌ Missing config field: {field}")
                    return False
            
            # Validate weights sum to 1.0
            weights = data.get('weights', {})
            weights_sum = sum(weights.values())
            if abs(weights_sum - 1.0) > 0.01:
                self.log(f"❌ Weights don't sum to 1.0: {weights_sum}")
                return False
                
            self.log("✅ Config structure is valid")
        
        return success

    def test_admin_config_get(self):
        """Test GET /api/connections/admin/connections/audience-quality/config"""
        url = f"{self.base_url}/api/connections/admin/connections/audience-quality/config"
        
        self.tests_run += 1
        self.log(f"🔍 Testing Admin Config Get...")
        
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, timeout=30)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                self.log(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json().get('data', {})
                if 'version' not in data or 'config' not in data:
                    self.log(f"❌ Missing admin config structure")
                    return False
                    
                return True
            else:
                self.log(f"❌ Failed - Status: {response.status_code}")
                self.failed_tests.append({
                    "name": "Admin Config Get",
                    "endpoint": url,
                    "expected": 200,
                    "got": response.status_code,
                    "response": response.text
                })
                return False

        except Exception as e:
            self.log(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "name": "Admin Config Get",
                "endpoint": url,
                "error": str(e)
            })
            return False

    def test_admin_config_patch(self):
        """Test PATCH /api/admin/connections/audience-quality/config"""
        url = f"{self.base_url}/api/admin/connections/audience-quality/config"
        
        # Test with valid weight update
        patch_data = {
            "weights": {
                "purity": 0.50,
                "smart_followers_proxy": 0.25,
                "signal_quality": 0.15,
                "consistency": 0.10
            }
        }
        
        self.tests_run += 1
        self.log(f"🔍 Testing Admin Config Patch...")
        
        try:
            response = requests.patch(url, json=patch_data, headers={'Content-Type': 'application/json'}, timeout=30)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                self.log(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json().get('data', {})
                if 'config' not in data:
                    self.log(f"❌ Missing updated config in response")
                    return False
                    
                # Verify weights were updated
                updated_weights = data['config'].get('weights', {})
                if updated_weights.get('purity') != 0.50:
                    self.log(f"❌ Weight not updated correctly")
                    return False
                    
                return True
            else:
                self.log(f"❌ Failed - Status: {response.status_code}")
                self.failed_tests.append({
                    "name": "Admin Config Patch",
                    "endpoint": url,
                    "expected": 200,
                    "got": response.status_code,
                    "response": response.text
                })
                return False

        except Exception as e:
            self.log(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "name": "Admin Config Patch",
                "endpoint": url,
                "error": str(e)
            })
            return False

    def test_twitter_score_integration(self):
        """Test Twitter Score integration with audience_quality_score_0_1"""
        # First get a mock audience quality result
        success, aq_response = self.run_test(
            "Get Audience Quality for Twitter Score",
            "GET",
            "audience-quality/mock",
            200
        )
        
        if not success:
            return False
            
        # Get a sample result
        results = aq_response.get('data', {}).get('results', [])
        if not results:
            self.log("❌ No audience quality results to test integration")
            return False
            
        sample_result = results[0]
        audience_quality_score = sample_result.get('audience_quality_score_0_1')
        
        # Test Twitter Score with audience quality
        twitter_score_input = {
            "account_id": "integration_test_001",
            "base_influence": 650,
            "x_score": 750,
            "signal_noise": 6.5,
            "velocity": 0.35,
            "acceleration": 0.25,
            "risk_level": "low",
            "red_flags": [],
            "early_signal_badge": "rising",
            "audience_quality_score_0_1": audience_quality_score  # This should replace network_proxy
        }
        
        success, ts_response = self.run_test(
            "Twitter Score with Audience Quality",
            "POST",
            "twitter-score",
            200,
            data=twitter_score_input
        )
        
        if success:
            data = ts_response.get('data', {})
            components = data.get('components', {})
            network_proxy = components.get('network_proxy')
            
            # Verify audience quality is used as network proxy
            if abs(network_proxy - audience_quality_score) > 0.01:
                self.log(f"❌ Audience quality not used as network proxy. Expected: {audience_quality_score:.3f}, Got: {network_proxy:.3f}")
                return False
                
            # Check data sources mention audience_quality
            meta = data.get('meta', {})
            data_sources = meta.get('data_sources', [])
            if 'audience_quality' not in data_sources:
                self.log(f"⚠️  audience_quality not listed in data sources: {data_sources}")
                
            self.log(f"✅ Integration working - Audience quality {audience_quality_score:.3f} used as network proxy {network_proxy:.3f}")
        
        return success

    def run_all_tests(self):
        """Run all audience quality tests"""
        self.log("🚀 Starting Audience Quality Engine Tests...")
        self.log(f"Testing against: {self.base_url}")
        
        # Test all endpoints
        tests = [
            ("Info Endpoint", self.test_audience_quality_info),
            ("Mock Data Endpoint", self.test_audience_quality_mock),
            ("Compute Endpoint", self.test_audience_quality_compute),
            ("Formula High Quality", self.test_audience_quality_formula_high_quality),
            ("Formula Low Quality", self.test_audience_quality_formula_low_quality),
            ("Batch Endpoint", self.test_audience_quality_batch),
            ("Config Endpoint", self.test_audience_quality_config),
            ("Admin Config Get", self.test_admin_config_get),
            ("Admin Config Patch", self.test_admin_config_patch),
            ("Twitter Score Integration", self.test_twitter_score_integration),
        ]
        
        passed_tests = []
        failed_tests = []
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed_tests.append(test_name)
                else:
                    failed_tests.append(test_name)
            except Exception as e:
                self.log(f"❌ Test {test_name} crashed: {str(e)}")
                failed_tests.append(f"{test_name} (crashed)")
        
        # Summary
        self.log(f"\n{'='*50}")
        self.log(f"📊 AUDIENCE QUALITY ENGINE TEST SUMMARY")
        self.log(f"{'='*50}")
        self.log(f"Tests run: {self.tests_run}")
        self.log(f"Tests passed: {self.tests_passed}")
        self.log(f"Tests failed: {len(self.failed_tests)}")
        self.log(f"Success rate: {(self.tests_passed/max(self.tests_run, 1)*100):.1f}%")
        
        if passed_tests:
            self.log(f"\n✅ PASSED TESTS:")
            for test in passed_tests:
                self.log(f"  - {test}")
        
        if failed_tests:
            self.log(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                self.log(f"  - {test}")
        
        if self.failed_tests:
            self.log(f"\n🔍 FAILURE DETAILS:")
            for failure in self.failed_tests:
                self.log(f"  - {failure.get('name', 'Unknown')}: {failure.get('error', failure.get('response', 'Unknown error'))}")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (self.tests_passed/max(self.tests_run, 1)*100),
            "failures": self.failed_tests
        }

def main():
    """Main test runner"""
    print("🔬 Audience Quality Engine v1.0 Test Suite")
    print("=" * 50)
    
    tester = AudienceQualityTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["success_rate"] < 50:
        return 1  # Major failure
    elif results["failed_tests"]:
        return 1  # Some failures  
    else:
        return 0  # All passed

if __name__ == "__main__":
    sys.exit(main())
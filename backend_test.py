#!/usr/bin/env python3
"""
Twitter Score v1.0 Backend API Testing
Tests the unified Twitter Score layer APIs for Phase 1.1
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Use production URL from frontend .env
BACKEND_URL = "https://isolated-model.preview.emergentagent.com"

class TwitterScoreTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_test(self, name: str, test_func, expected_result: Any = True) -> bool:
        """Run a single test and track results"""
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            result = test_func()
            if result == expected_result or (expected_result is True and result):
                self.tests_passed += 1
                self.log(f"✅ PASSED: {name}", "SUCCESS")
                return True
            else:
                self.failed_tests.append(f"{name}: Expected {expected_result}, got {result}")
                self.log(f"❌ FAILED: {name} - Expected {expected_result}, got {result}", "ERROR")
                return False
        except Exception as e:
            self.failed_tests.append(f"{name}: Exception - {str(e)}")
            self.log(f"❌ FAILED: {name} - Exception: {str(e)}", "ERROR")
            return False
    
    def test_health_check(self) -> bool:
        """Test /api/health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                return data.get('ok') is True and 'service' in data
            return False
        except Exception as e:
            self.log(f"Health check failed: {e}")
            return False
    
    def test_connections_health(self) -> bool:
        """Test /api/connections/health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/connections/health")
            if response.status_code == 200:
                data = response.json()
                return data.get('ok') is True and data.get('module') == 'connections'
            return False
        except Exception as e:
            self.log(f"Connections health check failed: {e}")
            return False
    
    # ============================================================
    # TWITTER SCORE API TESTS - Phase 1.1
    # ============================================================
    
    def test_twitter_score_info_api(self) -> bool:
        """Test GET /api/connections/twitter-score/info - should return version, weights, grades, penalties"""
        try:
            response = self.session.get(f"{self.base_url}/api/connections/twitter-score/info")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    info_data = data['data']
                    
                    # Check required fields
                    required_fields = ['version', 'weights', 'grades', 'penalties', 'components']
                    has_required = all(field in info_data for field in required_fields)
                    
                    # Validate version
                    version_ok = info_data.get('version') == '1.0.0'
                    
                    # Validate weights structure
                    weights = info_data.get('weights', {})
                    expected_weights = ['influence', 'quality', 'trend', 'network_proxy', 'consistency']
                    has_weights = all(weight in weights for weight in expected_weights)
                    
                    # Check weight values (should sum to 1.0 based on config: 35%, 20%, 20%, 15%, 10%)
                    weight_sum = sum(weights.values()) if has_weights else 0
                    weight_sum_ok = abs(weight_sum - 1.0) < 0.01
                    
                    # Validate grades structure
                    grades = info_data.get('grades', [])
                    grade_names = [g.get('grade') for g in grades]
                    has_all_grades = all(grade in grade_names for grade in ['S', 'A', 'B', 'C', 'D'])
                    
                    # Validate penalties structure
                    penalties = info_data.get('penalties', {})
                    penalties_ok = all(key in penalties for key in ['risk_levels', 'red_flags', 'max_penalty'])
                    
                    self.log(f"Twitter Score Info: version={info_data.get('version')}, weights_sum={weight_sum:.2f}, grades={len(grades)}")
                    return has_required and version_ok and has_weights and weight_sum_ok and has_all_grades and penalties_ok
            return False
        except Exception as e:
            self.log(f"Twitter Score Info API test failed: {e}")
            return False
    
    def test_twitter_score_mock_api(self) -> bool:
        """Test GET /api/connections/twitter-score/mock - should return examples with different grades"""
        try:
            response = self.session.get(f"{self.base_url}/api/connections/twitter-score/mock")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    mock_data = data['data']
                    
                    # Check for required structure
                    required_fields = ['version', 'description', 'results', 'grade_distribution']
                    has_required = all(field in mock_data for field in required_fields)
                    
                    results = mock_data.get('results', [])
                    results_ok = len(results) >= 3  # Should have multiple examples
                    
                    if results_ok and len(results) > 0:
                        first_result = results[0]
                        # Check result structure
                        result_fields = ['account_id', 'twitter_score_1000', 'grade', 'confidence', 'components', 'explain']
                        has_result_structure = all(field in first_result for field in result_fields)
                        
                        # Check score range (0-1000)
                        score = first_result.get('twitter_score_1000', -1)
                        score_ok = 0 <= score <= 1000
                        
                        # Check grade values
                        grade = first_result.get('grade')
                        grade_ok = grade in ['S', 'A', 'B', 'C', 'D']
                        
                        # Check confidence levels
                        confidence = first_result.get('confidence')
                        confidence_ok = confidence in ['LOW', 'MED', 'HIGH']
                        
                        # Check explain structure
                        explain = first_result.get('explain', {})
                        explain_fields = ['summary', 'drivers', 'concerns', 'recommendations']
                        has_explain = all(field in explain for field in explain_fields)
                        
                        # Check grade distribution
                        grade_dist = mock_data.get('grade_distribution', {})
                        has_grade_dist = all(grade in grade_dist for grade in ['S', 'A', 'B', 'C', 'D'])
                        
                        grades_found = [r.get('grade') for r in results]
                        unique_grades = len(set(grades_found))
                        
                        self.log(f"Twitter Score Mock: {len(results)} results, {unique_grades} unique grades, scores range from {min(r.get('twitter_score_1000', 0) for r in results)} to {max(r.get('twitter_score_1000', 0) for r in results)}")
                        
                        return (has_required and results_ok and has_result_structure and 
                               score_ok and grade_ok and confidence_ok and has_explain and has_grade_dist)
                    
                    return has_required
            return False
        except Exception as e:
            self.log(f"Twitter Score Mock API test failed: {e}")
            return False
    
    def test_twitter_score_compute_api(self) -> bool:
        """Test POST /api/connections/twitter-score - compute score with base_influence, velocity, red_flags"""
        try:
            # Test high influence + low risk = high score scenario
            high_quality_input = {
                "account_id": "test_high_quality_001",
                "base_influence": 850,
                "x_score": 780,
                "signal_noise": 8.5,
                "velocity": 15,
                "acceleration": 5,
                "risk_level": "LOW",
                "red_flags": [],
                "early_signal_badge": "rising",
                "early_signal_score": 75
            }
            
            response = self.session.post(
                f"{self.base_url}/api/connections/twitter-score",
                json=high_quality_input,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    result = data['data']
                    
                    # Check result structure
                    required_fields = ['account_id', 'twitter_score_1000', 'grade', 'confidence', 'components', 'debug', 'explain', 'meta']
                    has_structure = all(field in result for field in required_fields)
                    
                    # Validate high quality input produces good score
                    score = result.get('twitter_score_1000', 0)
                    grade = result.get('grade')
                    confidence = result.get('confidence')
                    
                    # High influence + low risk should give good score (A or S grade)
                    good_score = score >= 700  # A grade threshold
                    good_grade = grade in ['A', 'S']
                    
                    # Check components structure
                    components = result.get('components', {})
                    component_fields = ['influence', 'quality', 'trend', 'network_proxy', 'consistency', 'risk_penalty']
                    has_components = all(field in components for field in component_fields)
                    
                    # Components should be 0-1 range
                    components_valid = all(0 <= components.get(field, -1) <= 1 for field in component_fields)
                    
                    # Check debug info
                    debug = result.get('debug', {})
                    debug_fields = ['weighted_sum_0_1', 'weights', 'penalties']
                    has_debug = all(field in debug for field in debug_fields)
                    
                    # Check explain structure
                    explain = result.get('explain', {})
                    explain_fields = ['summary', 'drivers', 'concerns', 'recommendations']
                    has_explain = all(field in explain for field in explain_fields)
                    
                    # Drivers should be populated for high-quality account
                    has_drivers = len(explain.get('drivers', [])) > 0
                    
                    self.log(f"Twitter Score Compute (high quality): score={score}, grade={grade}, confidence={confidence}, drivers={len(explain.get('drivers', []))}")
                    
                    return (has_structure and good_score and good_grade and has_components and 
                           components_valid and has_debug and has_explain and has_drivers)
            return False
        except Exception as e:
            self.log(f"Twitter Score Compute API test failed: {e}")
            return False
    
    def test_twitter_score_compute_low_quality(self) -> bool:
        """Test POST /api/connections/twitter-score with high red_flags + HIGH risk = low score (Grade D/C)"""
        try:
            # Test high risk + red flags = low score scenario
            low_quality_input = {
                "account_id": "test_low_quality_002",
                "base_influence": 420,
                "x_score": 280,
                "signal_noise": 2.5,
                "velocity": 3,
                "acceleration": -5,
                "risk_level": "HIGH",
                "red_flags": ["REPOST_FARM", "BOT_LIKE_PATTERN", "FAKE_ENGAGEMENT"],
                "early_signal_badge": "none",
                "early_signal_score": 15
            }
            
            response = self.session.post(
                f"{self.base_url}/api/connections/twitter-score",
                json=low_quality_input,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    result = data['data']
                    
                    score = result.get('twitter_score_1000', 1000)
                    grade = result.get('grade')
                    
                    # High risk + red flags should give low score (C or D grade)
                    low_score = score <= 550  # Below B grade threshold  
                    low_grade = grade in ['C', 'D']
                    
                    # Check that concerns are populated for risky account
                    explain = result.get('explain', {})
                    has_concerns = len(explain.get('concerns', [])) > 0
                    
                    # Check that penalties are applied
                    debug = result.get('debug', {})
                    penalties = debug.get('penalties', {})
                    has_penalties = penalties.get('red_flags_penalty', 0) > 0 or penalties.get('risk_penalty', 0) > 0
                    
                    self.log(f"Twitter Score Compute (low quality): score={score}, grade={grade}, concerns={len(explain.get('concerns', []))}, penalties={penalties}")
                    
                    return low_score and low_grade and has_concerns and has_penalties
            return False
        except Exception as e:
            self.log(f"Twitter Score Compute Low Quality test failed: {e}")
            return False
    
    def test_twitter_score_batch_api(self) -> bool:
        """Test POST /api/connections/twitter-score/batch - batch compute for multiple accounts"""
        try:
            # Test batch with multiple different quality accounts
            batch_input = {
                "accounts": [
                    {
                        "account_id": "batch_whale_001",
                        "base_influence": 920,
                        "x_score": 820,
                        "signal_noise": 8.0,
                        "velocity": 12,
                        "acceleration": 3,
                        "risk_level": "LOW",
                        "red_flags": [],
                        "early_signal_badge": "breakout"
                    },
                    {
                        "account_id": "batch_retail_002",
                        "base_influence": 350,
                        "x_score": 450,
                        "signal_noise": 6.0,
                        "velocity": 8,
                        "acceleration": 2,
                        "risk_level": "MED",
                        "red_flags": ["VIRAL_SPIKE"],
                        "early_signal_badge": "rising"
                    },
                    {
                        "account_id": "batch_farm_003",
                        "base_influence": 580,
                        "x_score": 200,
                        "signal_noise": 1.5,
                        "velocity": -2,
                        "acceleration": -8,
                        "risk_level": "HIGH",
                        "red_flags": ["REPOST_FARM", "BOT_LIKE_PATTERN"],
                        "early_signal_badge": "none"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/connections/twitter-score/batch",
                json=batch_input,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    batch_result = data['data']
                    
                    # Check batch result structure
                    required_fields = ['version', 'computed_at', 'results', 'stats']
                    has_structure = all(field in batch_result for field in required_fields)
                    
                    results = batch_result.get('results', [])
                    correct_count = len(results) == 3
                    
                    # Check stats structure
                    stats = batch_result.get('stats', {})
                    stats_fields = ['total', 'by_grade', 'avg_score']
                    has_stats = all(field in stats for field in stats_fields)
                    
                    # Verify different grades produced
                    if correct_count and len(results) > 0:
                        grades = [r.get('grade') for r in results]
                        scores = [r.get('twitter_score_1000') for r in results]
                        
                        # Should have variety in scores/grades
                        unique_grades = len(set(grades))
                        score_range = max(scores) - min(scores) if scores else 0
                        
                        # Check by_grade stats match results
                        by_grade = stats.get('by_grade', {})
                        grade_stats_match = sum(by_grade.values()) == len(results)
                        
                        self.log(f"Twitter Score Batch: {len(results)} results, {unique_grades} unique grades, score range {score_range}, avg={stats.get('avg_score')}")
                        
                        return (has_structure and correct_count and has_stats and 
                               unique_grades >= 2 and score_range >= 100 and grade_stats_match)
                    
                    return has_structure and correct_count and has_stats
            return False
        except Exception as e:
            self.log(f"Twitter Score Batch API test failed: {e}")
            return False
    
    def test_twitter_score_config_api(self) -> bool:
        """Test GET /api/connections/twitter-score/config - current configuration"""
        try:
            response = self.session.get(f"{self.base_url}/api/connections/twitter-score/config")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    config_data = data['data']
                    
                    # Check config structure
                    required_fields = ['version', 'weights', 'normalize', 'trend', 'proxies', 'penalties', 'grades', 'confidence']
                    has_structure = all(field in config_data for field in required_fields)
                    
                    # Validate version
                    version_ok = config_data.get('version') == '1.0.0'
                    
                    # Validate weights (should sum to 1.0)
                    weights = config_data.get('weights', {})
                    expected_weights = ['influence', 'quality', 'trend', 'network_proxy', 'consistency']
                    has_all_weights = all(weight in weights for weight in expected_weights)
                    
                    # Check weight values based on config (35%, 20%, 20%, 15%, 10%)
                    if has_all_weights:
                        influence_weight = weights.get('influence') == 0.35
                        quality_weight = weights.get('quality') == 0.20
                        trend_weight = weights.get('trend') == 0.20
                        network_weight = weights.get('network_proxy') == 0.15
                        consistency_weight = weights.get('consistency') == 0.10
                        weights_correct = all([influence_weight, quality_weight, trend_weight, network_weight, consistency_weight])
                    else:
                        weights_correct = False
                    
                    # Validate grades thresholds
                    grades = config_data.get('grades', [])
                    if len(grades) >= 5:
                        # Check S >= 850, A >= 700, B >= 550, C >= 400, D >= 0
                        grades_by_name = {g['grade']: g['min'] for g in grades}
                        thresholds_correct = (
                            grades_by_name.get('S', 0) >= 850 and
                            grades_by_name.get('A', 0) >= 700 and
                            grades_by_name.get('B', 0) >= 550 and
                            grades_by_name.get('C', 0) >= 400 and
                            grades_by_name.get('D', -1) >= 0
                        )
                    else:
                        thresholds_correct = False
                    
                    # Validate penalties structure
                    penalties = config_data.get('penalties', {})
                    penalty_fields = ['risk_level', 'red_flags', 'max_total_penalty']
                    has_penalties = all(field in penalties for field in penalty_fields)
                    
                    # Check proxies (mocked APIs)
                    proxies = config_data.get('proxies', {})
                    proxy_fields = ['network_from_early_signal', 'consistency_default']
                    has_proxies = all(field in proxies for field in proxy_fields)
                    
                    # Validate consistency default (should be 0.55 per requirement)
                    consistency_proxy = proxies.get('consistency_default') == 0.55
                    
                    self.log(f"Twitter Score Config: version={config_data.get('version')}, weights_correct={weights_correct}, thresholds_correct={thresholds_correct}, consistency_proxy={consistency_proxy}")
                    
                    return (has_structure and version_ok and has_all_weights and weights_correct and 
                           thresholds_correct and has_penalties and has_proxies and consistency_proxy)
            return False
        except Exception as e:
            self.log(f"Twitter Score Config API test failed: {e}")
            return False
    
    def test_twitter_score_validation_errors(self) -> bool:
        """Test validation errors for invalid inputs"""
        try:
            # Test missing account_id
            invalid_input = {
                "base_influence": 500,
                "x_score": 400
            }
            
            response = self.session.post(
                f"{self.base_url}/api/connections/twitter-score",
                json=invalid_input,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                has_error = not data.get('ok') and 'error' in data
                error_mentions_account_id = 'account_id' in data.get('error', '').lower()
                
                self.log(f"Twitter Score Validation: properly rejects missing account_id")
                return has_error and error_mentions_account_id
            return False
        except Exception as e:
            self.log(f"Twitter Score Validation test failed: {e}")
            return False
    
    def test_batch_validation_errors(self) -> bool:
        """Test batch validation errors"""
        try:
            # Test empty accounts array
            invalid_batch = {
                "accounts": []
            }
            
            response = self.session.post(
                f"{self.base_url}/api/connections/twitter-score/batch",
                json=invalid_batch,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                has_error = not data.get('ok') and 'error' in data
                
                self.log(f"Twitter Score Batch Validation: properly rejects empty accounts")
                return has_error
            return False
        except Exception as e:
            self.log(f"Twitter Score Batch Validation test failed: {e}")
            return False
    
    def test_score_formula_verification(self) -> bool:
        """Test that score formula works as documented: high influence + low risk = high score"""
        try:
            # Create specific test case to verify formula
            formula_test_input = {
                "account_id": "formula_test_001",
                "base_influence": 900,  # High influence
                "x_score": 800,        # High quality
                "signal_noise": 9,     # High signal/noise
                "velocity": 20,        # Good growth
                "acceleration": 8,     # Good acceleration
                "risk_level": "LOW",   # Low risk
                "red_flags": [],       # No red flags
                "early_signal_badge": "breakout",
                "early_signal_score": 85
            }
            
            response = self.session.post(
                f"{self.base_url}/api/connections/twitter-score",
                json=formula_test_input,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    result = data['data']
                    
                    score = result.get('twitter_score_1000', 0)
                    grade = result.get('grade')
                    components = result.get('components', {})
                    debug = result.get('debug', {})
                    
                    # Verify high influence translates to high component score
                    influence_component = components.get('influence', 0)
                    influence_good = influence_component >= 0.8  # Should be high due to base_influence=900
                    
                    # Verify quality component
                    quality_component = components.get('quality', 0)
                    quality_good = quality_component >= 0.7   # Should be high due to x_score=800 + signal_noise=9
                    
                    # Verify trend component
                    trend_component = components.get('trend', 0)
                    trend_good = trend_component >= 0.6       # Should be good due to positive velocity/acceleration
                    
                    # Verify low risk penalty
                    risk_penalty = components.get('risk_penalty', 1)
                    low_risk = risk_penalty <= 0.15          # Should be low due to LOW risk + no red flags
                    
                    # Overall score should be high (A or S grade)
                    high_score = score >= 700 and grade in ['A', 'S']
                    
                    # Verify weighted sum makes sense
                    weighted_sum = debug.get('weighted_sum_0_1', 0)
                    weighted_sum_reasonable = 0.7 <= weighted_sum <= 1.0
                    
                    self.log(f"Formula Test: score={score}, grade={grade}, influence={influence_component:.2f}, quality={quality_component:.2f}, trend={trend_component:.2f}, risk_penalty={risk_penalty:.2f}")
                    
                    return (influence_good and quality_good and trend_good and low_risk and 
                           high_score and weighted_sum_reasonable)
            return False
        except Exception as e:
            self.log(f"Score Formula Verification test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Twitter Score API tests and return results"""
        self.log("🚀 Starting Twitter Score v1.0 Backend Testing")
        self.log(f"Testing against: {self.base_url}")
        
        # Core API Health Tests
        self.run_test("Backend health /api/health", self.test_health_check)
        self.run_test("Connections module health /api/connections/health", self.test_connections_health)
        
        # Twitter Score API Tests - Phase 1.1
        self.run_test("Twitter Score Info API /api/connections/twitter-score/info", self.test_twitter_score_info_api)
        self.run_test("Twitter Score Mock API /api/connections/twitter-score/mock", self.test_twitter_score_mock_api)
        self.run_test("Twitter Score Config API /api/connections/twitter-score/config", self.test_twitter_score_config_api)
        
        # Core Compute Functionality
        self.run_test("Twitter Score Compute API (high quality) /api/connections/twitter-score", self.test_twitter_score_compute_api)
        self.run_test("Twitter Score Compute API (low quality) - high red_flags + HIGH risk = low score", self.test_twitter_score_compute_low_quality)
        self.run_test("Twitter Score Batch API /api/connections/twitter-score/batch", self.test_twitter_score_batch_api)
        
        # Formula & Logic Tests
        self.run_test("Score Formula Verification - high influence + low risk = high score", self.test_score_formula_verification)
        
        # Validation Tests
        self.run_test("Twitter Score Input Validation", self.test_twitter_score_validation_errors)
        self.run_test("Twitter Score Batch Validation", self.test_batch_validation_errors)
        
        # Results Summary
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"\n📊 Twitter Score v1.0 Backend Test Results:")
        self.log(f"✅ Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        
        if self.failed_tests:
            self.log(f"❌ Failed Tests:")
            for failure in self.failed_tests:
                self.log(f"   - {failure}")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'success_rate': success_rate,
            'failed_tests': self.failed_tests
        }

def main():
    """Main test execution"""
    tester = TwitterScoreTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:
        print(f"\n🎉 Twitter Score v1.0 Backend tests PASSED with {results['success_rate']:.1f}% success rate")
        return 0
    else:
        print(f"\n💥 Twitter Score v1.0 Backend tests FAILED with {results['success_rate']:.1f}% success rate")
        return 1

if __name__ == "__main__":
    sys.exit(main())
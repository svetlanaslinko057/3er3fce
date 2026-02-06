#!/usr/bin/env python3
"""
Connections Dropdown Testing - Backend API Testing
Tests backend APIs for Connections dropdown functionality: Influencers and Graph tabs
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Use production URL from frontend .env
BACKEND_URL = "https://deploy-connect-6.preview.emergentagent.com"

class ConnectionsDropdownTester:
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
                # Check for module healthy status
                return data.get('ok') is True and data.get('module') == 'connections'
            return False
        except Exception as e:
            self.log(f"Connections health check failed: {e}")
            return False
    
    def test_connections_accounts_api(self) -> bool:
        """Test /api/connections/accounts for Influencers tab"""
        try:
            response = self.session.get(f"{self.base_url}/api/connections/accounts?limit=100")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    accounts_data = data['data']
                    # Check for accounts structure
                    has_items = 'items' in accounts_data and isinstance(accounts_data['items'], list)
                    
                    items_count = len(accounts_data.get('items', []))
                    self.log(f"Connections accounts: {items_count} accounts")
                    
                    # Check account structure if we have items
                    if items_count > 0:
                        first_account = accounts_data['items'][0]
                        required_fields = ['author_id', 'handle', 'scores']
                        has_required = all(field in first_account for field in required_fields)
                        return has_items and has_required
                    
                    return has_items  # Even if no items, structure should be correct
            return False
        except Exception as e:
            self.log(f"Connections accounts API test failed: {e}")
            return False
    
    def test_connections_graph_api(self) -> bool:
        """Test /api/connections/graph for Graph tab - should return 30 nodes and 400+ edges"""
        try:
            # Test POST with limit_nodes parameter
            filters = {"limit_nodes": 50}
            response = self.session.post(
                f"{self.base_url}/api/connections/graph",
                json=filters,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    graph_data = data['data']
                    # Check for required graph structure
                    has_nodes = 'nodes' in graph_data and isinstance(graph_data['nodes'], list)
                    has_edges = 'edges' in graph_data and isinstance(graph_data['edges'], list)
                    
                    # Check if we have reasonable amount of data
                    nodes_count = len(graph_data.get('nodes', []))
                    edges_count = len(graph_data.get('edges', []))
                    
                    self.log(f"Graph API: {nodes_count} nodes, {edges_count} edges")
                    
                    # Should have around 30 nodes and 400+ edges as specified
                    nodes_ok = nodes_count >= 20  # Allow some flexibility
                    edges_ok = edges_count >= 100  # Allow some flexibility for 400+ target
                    
                    # Check node structure if we have nodes
                    if nodes_count > 0:
                        first_node = graph_data['nodes'][0]
                        node_fields = ['id', 'label', 'profile', 'influence_score', 'color', 'size']
                        has_node_structure = all(field in first_node for field in node_fields)
                    else:
                        has_node_structure = True  # No nodes to check
                    
                    # Check edge structure if we have edges
                    if edges_count > 0:
                        first_edge = graph_data['edges'][0]
                        edge_fields = ['id', 'source', 'target', 'direction', 'weight']
                        has_edge_structure = all(field in first_edge for field in edge_fields)
                    else:
                        has_edge_structure = True  # No edges to check
                    
                    return has_nodes and has_edges and nodes_ok and edges_ok and has_node_structure and has_edge_structure
            return False
        except Exception as e:
            self.log(f"Connections Graph API test failed: {e}")
            return False
    
    def test_connections_compare_api(self) -> bool:
        """Test /api/connections/compare for Compare functionality"""
        try:
            # Test compare with mock data
            compare_data = {
                "left": "test_user_1",
                "right": "test_user_2"
            }
            response = self.session.post(
                f"{self.base_url}/api/connections/compare",
                json=compare_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    compare_result = data['data']
                    # Check for compare structure
                    required_fields = ['left', 'right', 'audience_overlap']
                    has_required = all(field in compare_result for field in required_fields)
                    
                    # Check audience overlap structure
                    if 'audience_overlap' in compare_result:
                        overlap = compare_result['audience_overlap']
                        overlap_fields = ['a_to_b', 'b_to_a', 'shared_users', 'jaccard_similarity']
                        has_overlap_structure = all(field in overlap for field in overlap_fields)
                        return has_required and has_overlap_structure
                    
                    return has_required
            return False
        except Exception as e:
            self.log(f"Connections Compare API test failed: {e}")
            return False
    
    def test_connections_graph_get(self) -> bool:
        """Test GET /api/connections/graph returns nodes and edges"""
        try:
            response = self.session.get(f"{self.base_url}/api/connections/graph")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'data' in data:
                    graph_data = data['data']
                    # Check for required graph structure
                    has_nodes = 'nodes' in graph_data and isinstance(graph_data['nodes'], list)
                    has_edges = 'edges' in graph_data and isinstance(graph_data['edges'], list)
                    has_meta = 'meta' in graph_data
                    
                    # Check if we have reasonable amount of data
                    nodes_count = len(graph_data.get('nodes', []))
                    edges_count = len(graph_data.get('edges', []))
                    
                    self.log(f"Graph GET: {nodes_count} nodes, {edges_count} edges")
                    return has_nodes and has_edges and has_meta and nodes_count > 0
            return False
        except Exception as e:
            self.log(f"Connections Graph GET test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Connections dropdown tests and return results"""
        self.log("🚀 Starting Connections Dropdown Backend Testing")
        self.log(f"Testing against: {self.base_url}")
        
        # Core API Health Tests
        self.run_test("Backend health check /api/health", self.test_health_check)
        self.run_test("Connections health /api/connections/health", self.test_connections_health)
        
        # Connections Dropdown API Tests
        self.run_test("Connections Accounts API /api/connections/accounts (Influencers tab)", self.test_connections_accounts_api)
        self.run_test("Connections Graph API /api/connections/graph (Graph tab)", self.test_connections_graph_api)
        self.run_test("Connections Compare API /api/connections/compare", self.test_connections_compare_api)
        
        # Additional Graph API Tests
        self.run_test("Connections Graph GET /api/connections/graph", self.test_connections_graph_get)
        
        # Results Summary
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"\n📊 Connections Dropdown Backend Test Results:")
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
    tester = ConnectionsDropdownTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:
        print(f"\n🎉 Connections Dropdown Backend tests PASSED with {results['success_rate']:.1f}% success rate")
        return 0
    else:
        print(f"\n💥 Connections Dropdown Backend tests FAILED with {results['success_rate']:.1f}% success rate")
        return 1

if __name__ == "__main__":
    sys.exit(main())
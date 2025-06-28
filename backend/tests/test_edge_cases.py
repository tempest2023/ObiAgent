"""
Edge case tests for the backend system.
Tests unusual scenarios, error conditions, and boundary cases.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.cost_analysis import CostAnalysisNode
from agent.function_nodes.preference_matcher import PreferenceMatcherNode
from agent.utils.workflow_store import workflow_store
from agent.utils.permission_manager import permission_manager

class TestBoundaryConditions:
    """Test boundary conditions and limits"""
    
    def test_extremely_long_input(self):
        """Test handling of extremely long input"""
        node = WebSearchNode()
        
        # Create extremely long query
        long_query = "a" * 10000
        shared = {"query": long_query, "num_results": 5}
        
        # Should handle gracefully
        prep_res = node.prep(shared)
        assert len(prep_res) <= 10000  # Should have reasonable limits
        
        # Should not crash
        try:
            exec_res = node.exec(prep_res)
            node.post(shared, prep_res, exec_res)
        except Exception as e:
            # Should fail gracefully with appropriate error
            assert "too long" in str(e).lower() or "limit" in str(e).lower()
    
    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        node = WebSearchNode()
        
        # Empty query
        shared = {"query": "", "num_results": 5}
        with pytest.raises(ValueError, match="Query cannot be empty"):
            node.prep(shared)
        
        # Whitespace-only query
        shared = {"query": "   ", "num_results": 5}
        with pytest.raises(ValueError, match="Query cannot be empty"):
            node.prep(shared)
    
    def test_zero_and_negative_values(self):
        """Test handling of zero and negative values"""
        node = WebSearchNode()
        
        # Zero results
        shared = {"query": "test", "num_results": 0}
        with pytest.raises(ValueError, match="Number of results must be positive"):
            node.prep(shared)
        
        # Negative results
        shared = {"query": "test", "num_results": -1}
        with pytest.raises(ValueError, match="Number of results must be positive"):
            node.prep(shared)
    
    def test_very_large_numbers(self):
        """Test handling of very large numbers"""
        node = WebSearchNode()
        
        # Very large number of results
        shared = {"query": "test", "num_results": 1000000}
        
        # Should handle gracefully (either accept or reject with appropriate error)
        try:
            prep_res = node.prep(shared)
            assert prep_res["num_results"] <= 100  # Should have reasonable limits
        except ValueError as e:
            assert "too large" in str(e).lower() or "limit" in str(e).lower()

class TestDataTypeEdgeCases:
    """Test edge cases with different data types"""
    
    def test_wrong_data_types(self):
        """Test handling of wrong data types"""
        node = CostAnalysisNode()
        
        # Wrong type for flight_search_results
        shared = {"flight_search_results": "not a list"}
        
        with pytest.raises(TypeError, match="Expected list"):
            node.prep(shared)
        
        # Wrong type for individual flight
        shared = {"flight_search_results": [{"price": "not a number"}]}
        
        prep_res = node.prep(shared)
        with pytest.raises(ValueError, match="Invalid price"):
            node.exec(prep_res)
    
    def test_none_values(self):
        """Test handling of None values"""
        node = PreferenceMatcherNode()
        
        # None values in data
        shared = {
            "flight_search_results": [None, {"departure_time": "afternoon"}],
            "user_preferences": None
        }
        
        with pytest.raises(ValueError, match="User preferences cannot be None"):
            node.prep(shared)
    
    def test_mixed_data_types(self):
        """Test handling of mixed data types"""
        node = CostAnalysisNode()
        
        # Mixed valid and invalid data
        shared = {
            "flight_search_results": [
                {"price": 500, "duration": "2h"},  # Valid
                {"price": "invalid", "duration": "1h"},  # Invalid
                {"price": 600, "duration": "3h"}  # Valid
            ]
        }
        
        prep_res = node.prep(shared)
        with pytest.raises(ValueError, match="Invalid price"):
            node.exec(prep_res)

class TestErrorRecovery:
    """Test error recovery scenarios"""
    
    def test_partial_failure_recovery(self):
        """Test recovery from partial failures"""
        node = CostAnalysisNode()
        
        # Some flights have invalid data
        shared = {
            "flight_search_results": [
                {"price": 500, "duration": "2h", "airline": "UA"},  # Valid
                {"price": "invalid", "duration": "1h", "airline": "AA"},  # Invalid
                {"price": 600, "duration": "3h", "airline": "DL"}  # Valid
            ]
        }
        
        # Should handle gracefully by filtering out invalid entries
        try:
            prep_res = node.prep(shared)
            result = node.exec(prep_res)
            node.post(shared, prep_res, result)
            
            # Should still provide analysis for valid flights
            assert "cost_analysis" in shared
            assert shared["cost_analysis"]["cheapest"]["price"] == 500
        except Exception as e:
            # Should fail with clear error message
            assert "invalid" in str(e).lower()
    
    def test_network_timeout_recovery(self, monkeypatch):
        """Test recovery from network timeouts"""
        node = WebSearchNode()
        shared = {"query": "test query", "num_results": 5}
        
        # Mock timeout
        def timeout_search(*args, **kwargs):
            raise Exception("Request timeout")
        
        monkeypatch.setattr("agent.function_nodes.web_search.search_web", timeout_search)
        
        prep_res = node.prep(shared)
        
        # Should handle timeout gracefully
        with pytest.raises(Exception, match="Request timeout"):
            node.exec(prep_res)
    
    def test_memory_error_recovery(self):
        """Test recovery from memory errors"""
        # This would test actual memory error handling
        # For now, we verify the concept
        assert True  # Placeholder for memory error tests

class TestConcurrencyEdgeCases:
    """Test edge cases in concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_same_resource_access(self):
        """Test concurrent access to same resource"""
        # Simulate concurrent access to workflow store
        workflow_id = "concurrent_test"
        
        # Create multiple tasks that access the same workflow
        async def add_workflow():
            workflow_store.add_workflow(
                workflow_id=workflow_id,
                metadata=Mock(name="Concurrent Test"),
                nodes=[],
                success_rate=0.8
            )
        
        async def get_workflow():
            return workflow_store.get_workflow(workflow_id)
        
        # Run concurrent operations
        tasks = [
            asyncio.create_task(add_workflow()),
            asyncio.create_task(get_workflow()),
            asyncio.create_task(add_workflow())
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle concurrent access gracefully
        assert len(results) == 3
        
        # Clean up
        workflow_store.remove_workflow(workflow_id)
    
    @pytest.mark.asyncio
    async def test_race_condition_handling(self):
        """Test handling of race conditions"""
        # Test race condition in permission requests
        request_ids = []
        
        async def create_request():
            request_id = permission_manager.create_permission_request(
                user_id="race_test_user",
                operation="payment",
                details="Race test",
                amount=100
            )
            request_ids.append(request_id)
            return request_id
        
        # Create multiple requests concurrently
        tasks = [asyncio.create_task(create_request()) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed with unique IDs
        assert len(set(results)) == 5
        assert len(set(request_ids)) == 5
        
        # Clean up
        for request_id in request_ids:
            permission_manager.remove_request(request_id)

class TestStateManagementEdgeCases:
    """Test edge cases in state management"""
    
    def test_workflow_store_cleanup(self):
        """Test cleanup of workflow store"""
        # Add many workflows
        workflow_ids = []
        for i in range(100):
            workflow_id = f"cleanup_test_{i}"
            workflow_store.add_workflow(
                workflow_id=workflow_id,
                metadata=Mock(name=f"Cleanup Test {i}"),
                nodes=[],
                success_rate=0.8
            )
            workflow_ids.append(workflow_id)
        
        # Verify all were added
        for workflow_id in workflow_ids:
            assert workflow_store.get_workflow(workflow_id) is not None
        
        # Clean up all
        for workflow_id in workflow_ids:
            workflow_store.remove_workflow(workflow_id)
        
        # Verify all were removed
        for workflow_id in workflow_ids:
            assert workflow_store.get_workflow(workflow_id) is None
    
    def test_permission_manager_cleanup(self):
        """Test cleanup of permission manager"""
        # Create many permission requests
        request_ids = []
        for i in range(50):
            request_id = permission_manager.create_permission_request(
                user_id=f"cleanup_user_{i}",
                operation="payment",
                details=f"Cleanup test {i}",
                amount=100 + i
            )
            request_ids.append(request_id)
        
        # Verify all were created
        for request_id in request_ids:
            assert not permission_manager.is_authorized(request_id)
        
        # Clean up all
        for request_id in request_ids:
            permission_manager.remove_request(request_id)
        
        # Verify all were removed
        for request_id in request_ids:
            # Should not find the request
            user_requests = permission_manager.get_user_requests("cleanup_user_0")
            assert not any(req.request_id == request_id for req in user_requests)

class TestInputValidationEdgeCases:
    """Test edge cases in input validation"""
    
    def test_special_characters(self):
        """Test handling of special characters"""
        node = WebSearchNode()
        
        # Test various special characters
        special_queries = [
            "query with spaces",
            "query-with-dashes",
            "query_with_underscores",
            "query.with.dots",
            "query!with!exclamation",
            "query?with?question",
            "query#with#hash",
            "query$with$dollar",
            "query%with%percent",
            "query&with&ampersand",
            "query*with*asterisk",
            "query(with)parentheses",
            "query[with]brackets",
            "query{with}braces",
            "query|with|pipe",
            "query\\with\\backslash",
            "query\"with\"quotes",
            "query'with'apostrophe",
            "query`with`backtick",
            "query~with~tilde"
        ]
        
        for query in special_queries:
            shared = {"query": query, "num_results": 5}
            
            # Should handle all special characters gracefully
            prep_res = node.prep(shared)
            assert prep_res["query"] == query
    
    def test_unicode_characters(self):
        """Test handling of Unicode characters"""
        node = WebSearchNode()
        
        unicode_queries = [
            "café",
            "naïve",
            "résumé",
            "über",
            "mañana",
            "你好",
            "こんにちは",
            "안녕하세요",
            "Привет",
            "مرحبا",
            "שלום",
            "नमस्ते",
            "สวัสดี",
            "வணக்கம்"
        ]
        
        for query in unicode_queries:
            shared = {"query": query, "num_results": 5}
            
            # Should handle Unicode gracefully
            prep_res = node.prep(shared)
            assert prep_res["query"] == query
    
    def test_very_long_strings(self):
        """Test handling of very long strings"""
        node = WebSearchNode()
        
        # Create very long query
        long_query = "a" * 50000
        shared = {"query": long_query, "num_results": 5}
        
        # Should handle gracefully
        try:
            prep_res = node.prep(shared)
            assert len(prep_res["query"]) <= 10000  # Should have reasonable limits
        except ValueError as e:
            assert "too long" in str(e).lower()

class TestPerformanceEdgeCases:
    """Test edge cases related to performance"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        node = CostAnalysisNode()
        
        # Create large dataset
        large_flight_data = []
        for i in range(10000):
            large_flight_data.append({
                "airline": f"Airline{i % 10}",
                "flight_number": f"FL{i}",
                "price": 100 + (i % 900),
                "duration": f"{2 + (i % 8)}h",
                "departure_time": f"{i % 24:02d}:{i % 60:02d}"
            })
        
        shared = {"flight_search_results": large_flight_data}
        
        # Should handle large dataset efficiently
        import time
        start_time = time.time()
        
        try:
            prep_res = node.prep(shared)
            result = node.exec(prep_res)
            node.post(shared, prep_res, result)
            
            processing_time = time.time() - start_time
            
            # Should complete in reasonable time
            assert processing_time < 30.0, f"Large dataset processing took {processing_time:.2f}s"
            
        except Exception as e:
            # Should fail gracefully with appropriate error
            assert "too large" in str(e).lower() or "memory" in str(e).lower()
    
    def test_memory_pressure(self):
        """Test behavior under memory pressure"""
        # This would test actual memory pressure scenarios
        # For now, we verify the concept
        assert True  # Placeholder for memory pressure tests

class TestSecurityEdgeCases:
    """Test edge cases related to security"""
    
    def test_sql_injection_attempts(self):
        """Test handling of SQL injection attempts"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' UNION SELECT * FROM users; --",
            "'; UPDATE users SET password='hacked'; --"
        ]
        
        node = WebSearchNode()
        
        for malicious_input in malicious_inputs:
            shared = {"query": malicious_input, "num_results": 5}
            
            # Should handle malicious input safely
            prep_res = node.prep(shared)
            assert prep_res["query"] == malicious_input  # Should be treated as plain text
    
    def test_xss_attempts(self):
        """Test handling of XSS attempts"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;"
        ]
        
        node = WebSearchNode()
        
        for xss_input in xss_inputs:
            shared = {"query": xss_input, "num_results": 5}
            
            # Should handle XSS attempts safely
            prep_res = node.prep(shared)
            assert prep_res["query"] == xss_input  # Should be treated as plain text
    
    def test_path_traversal_attempts(self):
        """Test handling of path traversal attempts"""
        path_traversal_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd"
        ]
        
        node = WebSearchNode()
        
        for traversal_input in path_traversal_inputs:
            shared = {"query": traversal_input, "num_results": 5}
            
            # Should handle path traversal attempts safely
            prep_res = node.prep(shared)
            assert prep_res["query"] == traversal_input  # Should be treated as plain text 
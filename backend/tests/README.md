# ObiAgent Backend Test Suite

This directory contains comprehensive tests for the ObiAgent backend system, covering unit tests, integration tests, security tests, performance tests, and edge cases.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_agent_improved.py         # Main agent system tests
├── test_function_nodes_improved.py # Function node tests
├── test_integration.py            # Integration tests
├── test_security.py               # Security tests
├── test_performance.py            # Performance tests
├── test_edge_cases.py             # Edge case tests
├── test_utils.py                  # Utility function tests
├── pytest.ini                    # Pytest configuration
├── run_tests.py                  # Test runner script
└── README.md                     # This file
```

## Running Tests

### Quick Start

```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration
python tests/run_tests.py --type security
python tests/run_tests.py --type performance
python tests/run_tests.py --type edge_cases

# Run fast tests (exclude slow tests)
python tests/run_tests.py --type fast

# Run specific test file
python tests/run_tests.py --file test_security.py

# Run with linting and security checks
python tests/run_tests.py --lint --security
```

### Using Pytest Directly

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=agent --cov-report=html

# Run specific test file
pytest tests/test_security.py

# Run tests by marker
pytest tests/ -m security
pytest tests/ -m integration
pytest tests/ -m "not slow"
```

## Test Categories

### 1. Unit Tests (`test_agent_improved.py`, `test_function_nodes_improved.py`)
- Test individual components in isolation
- Mock external dependencies
- Fast execution
- High coverage

### 2. Integration Tests (`test_integration.py`)
- Test complete workflows
- Test component interactions
- Test data flow between components
- May require external services

### 3. Security Tests (`test_security.py`)
- Test API key handling
- Test input validation
- Test permission system
- Test CORS and authentication
- Test SQL injection prevention
- Test XSS prevention

### 4. Performance Tests (`test_performance.py`)
- Test memory management
- Test async operations
- Test large dataset handling
- Test resource usage
- Test optimization opportunities

### 5. Edge Case Tests (`test_edge_cases.py`)
- Test boundary conditions
- Test error recovery
- Test unusual inputs
- Test concurrent operations
- Test state management edge cases

### 6. Utility Tests (`test_utils.py`)
- Test helper functions
- Test utility modules
- Test configuration handling
- Test data validation

## Test Fixtures

The `conftest.py` file provides common fixtures:

- `sample_shared_store`: Sample shared store for testing
- `sample_flight_data`: Sample flight data for testing
- `sample_web_search_results`: Sample web search results
- `mock_websocket`: Mock WebSocket for testing
- `mock_openai_client`: Mock OpenAI client
- `mock_gemini_client`: Mock Gemini client
- `mock_requests_response`: Mock HTTP response

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.security`: Security tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.edge_cases`: Edge case tests
- `@pytest.mark.slow`: Slow tests
- `@pytest.mark.asyncio`: Async tests

## Coverage Requirements

- Minimum coverage: 70%
- Coverage reports: HTML, XML, and terminal
- Coverage location: `htmlcov/` directory

## Test Data

Test data is generated dynamically to avoid external dependencies:

- Sample flight data with realistic values
- Mock API responses
- Simulated user interactions
- Test workflows and permissions

## Error Handling

Tests verify proper error handling:

- Missing API keys
- Network failures
- Invalid inputs
- Permission denials
- Resource exhaustion

## Performance Benchmarks

Performance tests include:

- Memory usage monitoring
- Execution time measurement
- Resource cleanup verification
- Concurrent operation testing

## Security Validation

Security tests verify:

- Input sanitization
- API key protection
- Permission enforcement
- CORS configuration
- SQL injection prevention
- XSS prevention

## Continuous Integration

Tests are configured for CI/CD:

- Automated test execution
- Coverage reporting
- Linting integration
- Security scanning
- Performance monitoring

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Don't rely on external services
3. **Clear Assertions**: Use descriptive assertion messages
4. **Error Testing**: Test both success and failure scenarios
5. **Performance Awareness**: Monitor test execution time
6. **Security Focus**: Always test security implications
7. **Documentation**: Document complex test scenarios

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes the backend directory
2. **Missing Dependencies**: Install test dependencies: `pip install pytest pytest-asyncio pytest-cov`
3. **API Key Errors**: Tests should not require real API keys
4. **Permission Errors**: Ensure proper file permissions

### Debug Mode

```bash
# Run with debug output
pytest tests/ -v -s

# Run single test with debug
pytest tests/test_security.py::TestAPIKeySecurity::test_openai_api_key_missing -v -s
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use appropriate test markers
3. Add comprehensive docstrings
4. Include both positive and negative test cases
5. Update this README if adding new test categories
6. Ensure tests pass in CI environment

## Test Maintenance

Regular maintenance tasks:

1. Update test data to match current API responses
2. Review and update security test vectors
3. Monitor test execution time
4. Update coverage requirements
5. Review and update edge case scenarios 
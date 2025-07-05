# GPUStack UI Backend Testing

This directory contains comprehensive tests for the GPUStack UI backend.

## Test Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_auth_service.py
│   └── test_file_processor.py
├── integration/            # Integration tests for API endpoints
│   └── test_auth_api.py
├── fixtures/               # Test data and fixtures
└── conftest.py            # Test configuration and fixtures
```

## Running Tests

### Using the test runner script:

```bash
# Run all tests
python run_tests.py all

# Run only unit tests
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run with coverage report
python run_tests.py coverage

# Run specific test file
python run_tests.py all --file tests/unit/test_auth_service.py
```

### Using pytest directly:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m auth

# Run with verbose output
pytest -v tests/
```

## Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual functions/classes
- `@pytest.mark.integration` - Integration tests for API endpoints
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slower running tests

## Test Environment

Tests run with the following environment variables:

- `TESTING=1` - Indicates test environment
- `GPUSTACK_API_BASE=http://localhost:8080` - Mock GPUStack API
- `TAVILY_API_KEY=test-key` - Test API key

## Coverage Reports

Coverage reports are generated in the `htmlcov/` directory and can be viewed by opening `htmlcov/index.html` in a browser.

## Writing Tests

### Unit Tests

Unit tests should test individual components in isolation:

```python
import pytest
from services.my_service import MyService

class TestMyService:
    def test_my_function(self):
        service = MyService()
        result = service.my_function("input")
        assert result == "expected_output"
```

### Integration Tests

Integration tests should test API endpoints and component interactions:

```python
import pytest
from fastapi.testclient import TestClient

class TestMyAPI:
    def test_my_endpoint(self, client: TestClient, auth_headers):
        response = client.get("/api/my-endpoint", headers=auth_headers)
        assert response.status_code == 200
```

### Fixtures

Common test fixtures are available in `conftest.py`:

- `client` - FastAPI test client
- `async_client` - Async test client
- `auth_headers` - Authentication headers
- `mock_user_data` - Sample user data
- `sample_file_content` - Sample file content for testing

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Mocking**: Use mocks for external dependencies (GPUStack API, file system, etc.)
3. **Clear Names**: Test names should clearly describe what is being tested
4. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification phases
5. **Edge Cases**: Test both happy path and error conditions
6. **Fast Tests**: Keep tests fast by avoiding unnecessary I/O operations

## Continuous Integration

These tests are designed to run in CI/CD pipelines. See the GitHub Actions workflow for automated testing configuration.

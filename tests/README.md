# Tests

This directory contains comprehensive test suites for the Mergington High School Activities API.

## Test Structure

- `conftest.py` - Test configuration and shared fixtures
- `test_api.py` - Main API endpoint tests
- `test_edge_cases.py` - Edge cases and error handling tests

## Running Tests

### Basic test run:
```bash
pytest tests/ -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing -v
```

### Run specific test file:
```bash
pytest tests/test_api.py -v
```

### Run specific test class:
```bash
pytest tests/test_api.py::TestSignupEndpoint -v
```

## Test Categories

### API Tests (`test_api.py`)
- **Root Endpoint**: Tests the redirect functionality
- **Activities Endpoint**: Tests retrieving all activities
- **Signup Endpoint**: Tests student registration for activities
- **Unregister Endpoint**: Tests removing students from activities
- **Integration Scenarios**: Tests complete workflows

### Edge Cases (`test_edge_cases.py`)
- **Edge Cases**: Invalid inputs, special characters, missing parameters
- **Data Consistency**: State management and data integrity
- **HTTP Methods**: Ensures correct HTTP method usage

## Test Features

- **Fixtures**: Automatic activity state reset between tests
- **100% Coverage**: Complete coverage of the FastAPI application
- **Error Testing**: Comprehensive error condition testing
- **Integration Testing**: End-to-end workflow validation
- **URL Encoding**: Tests for special characters in URLs and parameters

## Dependencies

Tests require the following packages (installed via `requirements.txt`):
- `pytest` - Testing framework
- `httpx` - HTTP client for testing FastAPI
- `pytest-asyncio` - Async testing support
- `pytest-cov` - Coverage reporting
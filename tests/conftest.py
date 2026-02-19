"""
Pytest configuration and shared fixtures for UUP Dump API tests.
"""

import pytest
import logging
from unittest.mock import Mock


@pytest.fixture
def mock_response():
    """
    Create a mock response object that mimics requests.Response.

    Usage:
        def test_something(mock_response):
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "value"}
    """
    response = Mock()
    response.status_code = 200
    response.text = ""
    response.json.return_value = {}
    return response


@pytest.fixture
def mock_successful_response():
    """
    Pre-configured mock response for successful API calls.
    """
    response = Mock()
    response.status_code = 200
    response.text = '{"response": {"success": true}}'
    response.json.return_value = {"response": {"success": True}}
    return response


@pytest.fixture
def mock_error_response():
    """
    Pre-configured mock response for API error responses.
    """
    response = Mock()
    response.status_code = 200
    response.text = '{"response": {"error": "NO_UPDATE_FOUND"}}'
    response.json.return_value = {"response": {"error": "NO_UPDATE_FOUND"}}
    return response


@pytest.fixture
def sample_update_id():
    """Provide a sample update UUID for testing."""
    return "12345678-1234-1234-1234-123456789abc"


@pytest.fixture
def sample_api_params():
    """Provide sample API parameters for testing."""
    return {
        "arch": "amd64",
        "ring": "Retail",
        "flight": "Mainline",
        "build": "22621",
        "sku": 48,
    }


@pytest.fixture
def caplog_at_info(caplog):
    """
    Fixture that sets log level to INFO for capturing logs.

    Usage:
        def test_something(caplog_at_info):
            # caplog is now set to INFO level
            logger.info("test message")
            assert "test message" in caplog.text
    """
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture
def caplog_at_debug(caplog):
    """
    Fixture that sets log level to DEBUG for capturing logs.
    """
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture(autouse=True)
def reset_logging():
    """
    Reset logging configuration after each test to prevent interference.
    This fixture runs automatically for every test.
    """
    yield
    # Cleanup after test
    logging.getLogger("uup_dump_api.adapter").handlers.clear()
    logging.getLogger("uup_dump_api.adapter").setLevel(logging.NOTSET)


@pytest.fixture
def mock_requests_get(monkeypatch):
    """
    Fixture to easily mock requests.get for multiple tests.

    Usage:
        def test_something(mock_requests_get):
            mock_requests_get.return_value.json.return_value = {"data": "test"}
            # Your test code here
    """
    mock = Mock()
    monkeypatch.setattr("uup_dump_api.adapter.requests.get", mock)
    return mock


# Markers for test categorization
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "network: mark test as requiring network access")


# Hook to add test report header
def pytest_report_header(config):
    """Add custom header to pytest output."""
    return ["UUP Dump API Test Suite", "Testing adapter, exceptions, and API methods"]


# Hook to customize test collection
def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.
    Automatically mark tests based on their location.
    """
    for item in items:
        # Auto-mark based on class names
        if "Integration" in str(item.parent):
            item.add_marker(pytest.mark.integration)
        elif "Test" in str(item.parent):
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "slow" in item.nodeid.lower() or "timeout" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)

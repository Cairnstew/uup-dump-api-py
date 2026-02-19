"""
Comprehensive test suite for UUP Dump API Python module.

Tests cover:
- RestAdapter functionality
- Exception handling
- API method calls
- Logging configuration
- Error message mapping
"""

import pytest
import logging
from unittest.mock import Mock, patch
from requests.exceptions import (
    Timeout,
    ConnectionError as RequestsConnectionError,
    HTTPError,
    RequestException,
)

# Import from the uup_dump_api package
from uup_dump_api.exceptions import (
    UUPDumpAPIError,
    UUPDumpHTTPError,
    UUPDumpValidationError,
    UUPDumpTimeoutError,
    UUPDumpConnectionError,
    UUPDumpResponseError,
    get_error_message,
    API_ERROR_MESSAGES,
)
from uup_dump_api.adapter import RestAdapter


class TestExceptions:
    """Test custom exception classes."""

    def test_base_exception(self):
        """Test base UUPDumpAPIError exception."""
        error = UUPDumpAPIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_http_error(self):
        """Test UUPDumpHTTPError with status code and response body."""
        error = UUPDumpHTTPError(
            "HTTP error", status_code=404, response_body="Not found"
        )
        assert str(error) == "HTTP error"
        assert error.status_code == 404
        assert error.response_body == "Not found"

    def test_http_error_without_optional_params(self):
        """Test UUPDumpHTTPError without optional parameters."""
        error = UUPDumpHTTPError("HTTP error")
        assert str(error) == "HTTP error"
        assert error.status_code is None
        assert error.response_body is None

    def test_validation_error(self):
        """Test UUPDumpValidationError exception."""
        error = UUPDumpValidationError("Invalid parameter")
        assert str(error) == "Invalid parameter"
        assert isinstance(error, UUPDumpAPIError)

    def test_timeout_error(self):
        """Test UUPDumpTimeoutError exception."""
        error = UUPDumpTimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, UUPDumpAPIError)

    def test_connection_error(self):
        """Test UUPDumpConnectionError exception."""
        error = UUPDumpConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, UUPDumpAPIError)

    def test_response_error(self):
        """Test UUPDumpResponseError with error code and API response."""
        api_response = {"response": {"error": "NO_UPDATE_FOUND"}}
        error = UUPDumpResponseError(
            "No update found", error_code="NO_UPDATE_FOUND", api_response=api_response
        )
        assert str(error) == "No update found"
        assert error.error_code == "NO_UPDATE_FOUND"
        assert error.api_response == api_response

    def test_response_error_without_optional_params(self):
        """Test UUPDumpResponseError without optional parameters."""
        error = UUPDumpResponseError("API error")
        assert str(error) == "API error"
        assert error.error_code is None
        assert error.api_response is None


class TestErrorMessages:
    """Test error message mapping."""

    def test_known_error_codes(self):
        """Test that all documented error codes have messages."""
        known_errors = [
            "UNKNOWN_ARCH",
            "UNKNOWN_RING",
            "UNKNOWN_FLIGHT",
            "NO_UPDATE_FOUND",
            "UNSUPPORTED_LANG",
            "NO_FILES",
            "UPDATE_INFORMATION_NOT_EXISTS",
        ]

        for error_code in known_errors:
            message = get_error_message(error_code)
            assert message != f"Unknown error: {error_code}"
            assert len(message) > 0

    def test_unknown_error_code(self):
        """Test handling of unknown error codes."""
        message = get_error_message("UNKNOWN_ERROR_CODE_XYZ")
        assert message == "Unknown error: UNKNOWN_ERROR_CODE_XYZ"

    def test_api_error_messages_dict(self):
        """Test that API_ERROR_MESSAGES contains expected entries."""
        assert isinstance(API_ERROR_MESSAGES, dict)
        assert len(API_ERROR_MESSAGES) > 0
        assert "UNKNOWN_ARCH" in API_ERROR_MESSAGES
        assert "NO_UPDATE_FOUND" in API_ERROR_MESSAGES


class TestRestAdapterInit:
    """Test RestAdapter initialization."""

    def test_default_initialization(self):
        """Test adapter initialization with default parameters."""
        adapter = RestAdapter()
        assert adapter.timeout == 10
        assert adapter.BASE_URL == "https://api.uupdump.net"
        assert adapter.logger is not None

    def test_custom_timeout(self):
        """Test adapter initialization with custom timeout."""
        adapter = RestAdapter(timeout=30)
        assert adapter.timeout == 30

    def test_custom_log_level(self):
        """Test adapter initialization with custom log level."""
        adapter = RestAdapter(log_level=logging.DEBUG)
        assert adapter.logger.level == logging.DEBUG

    def test_logger_setup(self):
        """Test that logger is properly configured."""
        adapter = RestAdapter()
        assert isinstance(adapter.logger, logging.Logger)
        assert adapter.logger.name == "uup_dump_api.adapter"


class TestRestAdapterGetMethod:
    """Test the internal _get method of RestAdapter."""

    @patch("uup_dump_api.adapter.requests.get")
    def test_successful_request(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"data": "test"}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        result = adapter._get("test.php")

        assert result == {"response": {"data": "test"}}
        mock_get.assert_called_once()

    @patch("uup_dump_api.adapter.requests.get")
    def test_request_with_params(self, mock_get):
        """Test request with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        params = {"search": "windows", "sortByDate": "1"}
        adapter._get("listid.php", params=params)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"] == params

    @patch("uup_dump_api.adapter.requests.get")
    def test_timeout_error(self, mock_get):
        """Test that timeout raises UUPDumpTimeoutError."""
        mock_get.side_effect = Timeout()

        adapter = RestAdapter(timeout=5)

        with pytest.raises(UUPDumpTimeoutError) as exc_info:
            adapter._get("test.php")

        assert "timed out after 5 seconds" in str(exc_info.value)

    @patch("uup_dump_api.adapter.requests.get")
    def test_connection_error(self, mock_get):
        """Test that connection error raises UUPDumpConnectionError."""
        mock_get.side_effect = RequestsConnectionError("Connection refused")

        adapter = RestAdapter()

        with pytest.raises(UUPDumpConnectionError) as exc_info:
            adapter._get("test.php")

        assert "Failed to connect" in str(exc_info.value)

    @patch("uup_dump_api.adapter.requests.get")
    def test_http_error(self, mock_get):
        """Test that HTTP error raises UUPDumpHTTPError."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        adapter = RestAdapter()

        with pytest.raises(UUPDumpHTTPError) as exc_info:
            adapter._get("test.php")

        assert exc_info.value.status_code == 404

    @patch("uup_dump_api.adapter.requests.get")
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid response"
        mock_get.return_value = mock_response

        adapter = RestAdapter()

        with pytest.raises(UUPDumpHTTPError) as exc_info:
            adapter._get("test.php")

        assert "Invalid JSON response" in str(exc_info.value)

    @patch("uup_dump_api.adapter.requests.get")
    def test_api_error_response(self, mock_get):
        """Test handling of API error in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"error": "NO_UPDATE_FOUND"}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()

        with pytest.raises(UUPDumpResponseError) as exc_info:
            adapter._get("test.php")

        assert exc_info.value.error_code == "NO_UPDATE_FOUND"
        assert "No update found" in str(exc_info.value)

    @patch("uup_dump_api.adapter.requests.get")
    def test_generic_request_exception(self, mock_get):
        """Test handling of generic request exceptions."""
        mock_get.side_effect = RequestException("Generic error")

        adapter = RestAdapter()

        with pytest.raises(UUPDumpHTTPError) as exc_info:
            adapter._get("test.php")

        assert "Request failed" in str(exc_info.value)


class TestRestAdapterMethods:
    """Test all public API methods of RestAdapter."""

    @patch("uup_dump_api.adapter.requests.get")
    def test_listid_default(self, mock_get):
        """Test listid with default parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"builds": []}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        result = adapter.listid()

        assert result == {"response": {"builds": []}}
        call_args = mock_get.call_args
        assert "listid.php" in call_args[0][0]

    @patch("uup_dump_api.adapter.requests.get")
    def test_listid_with_search(self, mock_get):
        """Test listid with search parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.listid(search="windows 11", sortByDate=True)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["search"] == "windows 11"
        assert params["sortByDate"] == "1"

    @patch("uup_dump_api.adapter.requests.get")
    def test_fetchupd_default(self, mock_get):
        """Test fetchupd with default parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"updateInfo": {}}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.fetchupd()

        call_args = mock_get.call_args
        assert "fetchupd.php" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["arch"] == "amd64"
        assert params["ring"] == "Retail"

    @patch("uup_dump_api.adapter.requests.get")
    def test_fetchupd_custom_params(self, mock_get):
        """Test fetchupd with custom parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.fetchupd(
            arch="arm64",
            ring="Dev",
            flight="Active",
            build="25000",
            sku=128,
            cacheRequests=True,
        )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["arch"] == "arm64"
        assert params["ring"] == "Dev"
        assert params["flight"] == "Active"
        assert params["build"] == "25000"
        assert params["sku"] == "128"
        assert params["cacheRequests"] == "1"

    @patch("uup_dump_api.adapter.requests.get")
    def test_get_files(self, mock_get):
        """Test get_files method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"files": {}}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        update_id = "12345-6789-abcd"
        adapter.get_files(updateId=update_id)

        call_args = mock_get.call_args
        assert "get.php" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["id"] == update_id

    @patch("uup_dump_api.adapter.requests.get")
    def test_get_files_with_language(self, mock_get):
        """Test get_files with language parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.get_files(
            updateId="test-id",
            usePack="en-us",
            desiredEdition="edition-uuid",
            requestType=1,
        )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["pack"] == "en-us"
        assert params["edition"] == "edition-uuid"
        assert params["requestType"] == "1"

    @patch("uup_dump_api.adapter.requests.get")
    def test_list_editions(self, mock_get):
        """Test list_editions method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"editionList": []}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.list_editions(lang="en-us")

        call_args = mock_get.call_args
        assert "listeditions.php" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["lang"] == "en-us"

    @patch("uup_dump_api.adapter.requests.get")
    def test_list_editions_with_update_id(self, mock_get):
        """Test list_editions with update ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.list_editions(lang="en-us", updateId="test-id")

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["lang"] == "en-us"
        assert params["id"] == "test-id"

    @patch("uup_dump_api.adapter.requests.get")
    def test_list_langs(self, mock_get):
        """Test list_langs method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"langList": []}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.list_langs()

        call_args = mock_get.call_args
        assert "listlangs.php" in call_args[0][0]

    @patch("uup_dump_api.adapter.requests.get")
    def test_list_langs_with_params(self, mock_get):
        """Test list_langs with optional parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.list_langs(updateId="test-id", returnInfo=True)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["id"] == "test-id"
        assert params["returnInfo"] == "true"

    @patch("uup_dump_api.adapter.requests.get")
    def test_update_info(self, mock_get):
        """Test update_info method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"info": {}}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.update_info(updateId="test-id")

        call_args = mock_get.call_args
        assert "updateinfo.php" in call_args[0][0]
        params = call_args[1]["params"]
        assert params["id"] == "test-id"

    @patch("uup_dump_api.adapter.requests.get")
    def test_update_info_with_filters(self, mock_get):
        """Test update_info with filtering parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        adapter.update_info(updateId="test-id", onlyInfo="title", ignoreFiles=True)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["onlyinfo"] == "title"
        assert params["ignoreFiles"] == "true"

    @patch("uup_dump_api.adapter.requests.get")
    def test_api_version(self, mock_get):
        """Test api_version method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"version": "1.0.0"}}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        result = adapter.api_version()

        call_args = mock_get.call_args
        assert "api_version.php" in call_args[0][0]
        assert result == {"response": {"version": "1.0.0"}}


class TestLogging:
    """Test logging functionality."""

    def test_adapter_logger_exists(self):
        """Test that adapter has a logger."""
        adapter = RestAdapter()
        assert hasattr(adapter, "logger")
        assert isinstance(adapter.logger, logging.Logger)

    @patch("uup_dump_api.adapter.requests.get")
    def test_logging_on_successful_request(self, mock_get, caplog):
        """Test that successful requests are logged."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.return_value = mock_response

        with caplog.at_level(logging.DEBUG):
            adapter = RestAdapter(log_level=logging.DEBUG)
            adapter._get("test.php")

        # Check that debug logs were created
        assert any("Making GET request" in record.message for record in caplog.records)

    @patch("uup_dump_api.adapter.requests.get")
    def test_logging_on_error(self, mock_get, caplog):
        """Test that errors are logged."""
        mock_get.side_effect = Timeout()

        with caplog.at_level(logging.ERROR):
            adapter = RestAdapter()

            with pytest.raises(UUPDumpTimeoutError):
                adapter._get("test.php")

        # Check that error was logged
        assert any("timed out" in record.message for record in caplog.records)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @patch("uup_dump_api.adapter.requests.get")
    def test_empty_response(self, mock_get):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        result = adapter._get("test.php")

        assert result == {}

    @patch("uup_dump_api.adapter.requests.get")
    def test_response_without_response_key(self, mock_get):
        """Test handling of response without 'response' key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        adapter = RestAdapter()
        result = adapter._get("test.php")

        assert result == {"data": "test"}

    @patch("uup_dump_api.adapter.requests.get")
    def test_very_long_response_body_truncation(self, mock_get):
        """Test that long response bodies are truncated in errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "x" * 1000  # Long response
        mock_get.return_value = mock_response

        adapter = RestAdapter()

        with pytest.raises(UUPDumpHTTPError) as exc_info:
            adapter._get("test.php")

        # Response body should be truncated to 500 chars
        assert len(exc_info.value.response_body) == 500

    def test_zero_timeout(self):
        """Test initialization with zero timeout."""
        adapter = RestAdapter(timeout=0)
        assert adapter.timeout == 0

    def test_negative_timeout(self):
        """Test initialization with negative timeout."""
        adapter = RestAdapter(timeout=-1)
        assert adapter.timeout == -1


class TestIntegration:
    """Integration tests that test multiple components together."""

    @patch("uup_dump_api.adapter.requests.get")
    def test_full_workflow_listid_to_get_files(self, mock_get):
        """Test a complete workflow: list updates, then get files."""
        # First call - listid
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "response": {"builds": [{"uuid": "test-uuid"}]}
        }

        # Second call - get_files
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {"response": {"files": {"file1.cab": {}}}}

        mock_get.side_effect = [mock_response1, mock_response2]

        adapter = RestAdapter()

        # List updates
        list_result = adapter.listid(search="windows")
        assert "builds" in list_result["response"]

        # Get files for first update
        update_id = list_result["response"]["builds"][0]["uuid"]
        files_result = adapter.get_files(updateId=update_id)
        assert "files" in files_result["response"]

    @patch("uup_dump_api.adapter.requests.get")
    def test_error_recovery_retry_pattern(self, mock_get):
        """Test that calling again after an error works."""
        # First call fails
        mock_get.side_effect = Timeout()

        adapter = RestAdapter()

        with pytest.raises(UUPDumpTimeoutError):
            adapter._get("test.php")

        # Second call succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {}}
        mock_get.side_effect = None
        mock_get.return_value = mock_response

        result = adapter._get("test.php")
        assert result == {"response": {}}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

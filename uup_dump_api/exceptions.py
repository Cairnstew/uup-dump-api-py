from typing import Optional, Dict, Any, Union

"""
Custom exceptions for UUP Dump API module.
"""


class UUPDumpAPIError(Exception):
    """Base exception for all UUP Dump API errors."""

    pass


class UUPDumpHTTPError(UUPDumpAPIError):
    """Raised when an HTTP request fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class UUPDumpValidationError(UUPDumpAPIError):
    """Raised when invalid parameters are provided."""

    pass


class UUPDumpTimeoutError(UUPDumpAPIError):
    """Raised when a request times out."""

    pass


class UUPDumpConnectionError(UUPDumpAPIError):
    """Raised when unable to connect to the API."""

    pass


class UUPDumpResponseError(UUPDumpAPIError):
    """Raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        api_response: Optional[Dict[Any, Any]] = None,
    ):
        self.error_code = error_code
        self.api_response = api_response
        super().__init__(message)


# Map API error codes to human-readable messages
API_ERROR_MESSAGES = {
    # fetchupd.php errors
    "UNKNOWN_ARCH": "Invalid architecture specified. Supported: amd64, x86, arm64, all",
    "UNKNOWN_RING": "Invalid ring/channel specified. Supported: Canary, Dev, Beta, ReleasePreview, Retail, WIF, WIS, RP",
    "UNKNOWN_FLIGHT": "Invalid flight specified. Supported: Mainline, Active, Skip, Current",
    "UNKNOWN_COMBINATION": "Invalid combination of parameters",
    "ILLEGAL_BUILD": "Invalid build number format",
    "ILLEGAL_MINOR": "Invalid minor version number",
    "NO_UPDATE_FOUND": "No update found matching the specified criteria",
    "EMPTY_FILELIST": "Update found but file list is empty",
    "WU_REQUEST_FAILED": "Windows Update request failed",
    # get.php errors
    "UNSUPPORTED_LANG": "Unsupported language specified",
    "UNSPECIFIED_LANG": "Language parameter is required",
    "UNSUPPORTED_EDITION": "Unsupported edition specified",
    "UNSUPPORTED_COMBINATION": "Unsupported combination of parameters",
    "MISSING_FILES": "Some required files are missing",
    "NO_FILES": "No files available for this update",
    "XML_PARSE_ERROR": "Error parsing XML response from Windows Update",
    # listeditions.php errors
    # UNSUPPORTED_LANG already defined above
    # listid.php errors
    "NO_FILEINFO_DIR": "File information directory not found",
    "SEARCH_NO_RESULTS": "No results found for the search query",
    # updateinfo.php errors
    "UPDATE_INFORMATION_NOT_EXISTS": "Update information does not exist",
    "KEY_NOT_EXISTS": "Requested key does not exist in update information",
}


def get_error_message(error_code: Union[str, int]) -> str:
    """
    Get a human-readable error message for an API error code.

    Args:
        error_code: The error code returned by the API

    Returns:
        Human-readable error message
    """
    error_code_str = str(error_code)
    return API_ERROR_MESSAGES.get(error_code_str, f"Unknown error: {error_code}")

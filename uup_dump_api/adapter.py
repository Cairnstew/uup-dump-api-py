"""
REST adapter for UUP Dump API with logging and exception handling.
"""

import requests
import logging
from typing import Optional, Dict, Any
from requests.exceptions import (
    Timeout,
    ConnectionError as RequestsConnectionError,
    HTTPError,
    RequestException,
)

from .exceptions import (
    UUPDumpHTTPError,
    # UUPDumpValidationError,
    UUPDumpTimeoutError,
    UUPDumpConnectionError,
    UUPDumpResponseError,
    get_error_message,
)


class RestAdapter:
    """
    REST adapter for interacting with the UUP Dump API.

    Provides methods to fetch Windows Update information, list updates,
    and retrieve update details with comprehensive error handling and logging.
    """

    def __init__(self, timeout: float = 10, log_level: int = logging.INFO):
        """
        Initialize the REST adapter.

        Args:
            timeout: Request timeout in seconds (default: 10)
            log_level: Logging level (default: logging.INFO)
        """
        self.timeout = timeout
        self.BASE_URL: str = "https://api.uupdump.net"

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # Create console handler if no handlers exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.info(
            f"Initialized UUP Dump API adapter (base_url={self.BASE_URL}, timeout={timeout}s)"
        )

    def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API with error handling.

        Args:
            endpoint: API endpoint to call
            params: Query parameters (optional)

        Returns:
            JSON response from the API

        Raises:
            UUPDumpTimeoutError: If the request times out
            UUPDumpConnectionError: If unable to connect to the API
            UUPDumpHTTPError: If the HTTP request fails
            UUPDumpResponseError: If the API returns an error response
        """
        url = f"{self.BASE_URL}/{endpoint}"

        self.logger.debug(f"Making GET request to {url} with params: {params}")

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)

            # Log response status
            self.logger.debug(f"Response status: {resp.status_code}")

            # Raise HTTPError for bad status codes
            resp.raise_for_status()

            # Parse JSON response
            try:
                data = resp.json()
            except ValueError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                raise UUPDumpHTTPError(
                    f"Invalid JSON response from API: {str(e)}",
                    status_code=resp.status_code,
                    response_body=resp.text[:500],  # First 500 chars
                )

            # Check for API-level errors
            if isinstance(data, dict) and "response" in data:
                response_data = data["response"]

                # Check for error in response
                if isinstance(response_data, dict) and "error" in response_data:
                    error_code = response_data["error"]
                    error_message = get_error_message(error_code)

                    self.logger.error(
                        f"API returned error: {error_code} - {error_message}"
                    )

                    raise UUPDumpResponseError(
                        error_message, error_code=error_code, api_response=data
                    )

            self.logger.debug("Request successful")
            return data

        except Timeout as e:
            self.logger.error(f"Request timed out after {self.timeout}s: {url}")
            raise UUPDumpTimeoutError(
                f"Request to {endpoint} timed out after {self.timeout} seconds"
            ) from e

        except RequestsConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise UUPDumpConnectionError(
                f"Failed to connect to UUP Dump API: {str(e)}"
            ) from e

        except HTTPError as e:
            status_code = e.response.status_code if e.response else None
            response_body = e.response.text[:500] if e.response else None

            self.logger.error(f"HTTP error {status_code}: {e}")

            raise UUPDumpHTTPError(
                f"HTTP {status_code} error: {str(e)}",
                status_code=status_code,
                response_body=response_body,
            ) from e

        except RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise UUPDumpHTTPError(f"Request failed: {str(e)}") from e

    def listid(self, search: str = "", sortByDate: bool = False) -> Dict[str, Any]:
        """
        List updates in the fileinfo database.

        Args:
            search: Search query (optional)
            sortByDate: Sort results by creation date (optional)

        Returns:
            Dictionary containing list of updates

        Raises:
            UUPDumpResponseError: If API returns an error (e.g., NO_FILEINFO_DIR, SEARCH_NO_RESULTS)
        """
        self.logger.info(
            f"Listing updates (search='{search}', sortByDate={sortByDate})"
        )

        params = {}
        if search:
            params["search"] = search
        if sortByDate:
            params["sortByDate"] = "1"

        return self._get("listid.php", params=params)

    def fetchupd(
        self,
        arch: str = "amd64",
        ring: str = "Retail",
        flight: str = "Mainline",
        build: str = "22621",
        minor: int = 0,
        sku: int = 48,
        type: str = "Production",
        cacheRequests: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch latest update information from Windows Update servers.

        Args:
            arch: Architecture (amd64, x86, arm64, all)
            ring: Channel (Canary, Dev, Beta, ReleasePreview, Retail, WIF, WIS, RP)
            flight: Content type (Mainline, Active, Skip, Current)
            build: Build number (major or major.minor format)
            minor: Build minor (unused if build is major.minor format)
            sku: SKU number
            type: Release type (Production, Test) for WCOS
            cacheRequests: Should request responses be cached

        Returns:
            Dictionary containing update information

        Raises:
            UUPDumpResponseError: If API returns an error (e.g., UNKNOWN_ARCH, NO_UPDATE_FOUND)
        """
        self.logger.info(
            f"Fetching update (arch={arch}, ring={ring}, flight={flight}, "
            f"build={build}, minor={minor}, sku={sku})"
        )

        params = {
            "arch": arch,
            "ring": ring,
            "flight": flight,
            "build": build,
            "minor": str(minor),
            "sku": str(sku),
            "type": type,
        }
        if cacheRequests:
            params["cacheRequests"] = "1"

        return self._get("fetchupd.php", params=params)

    def get_files(
        self,
        updateId: str,
        usePack: Optional[str] = None,
        desiredEdition: Optional[str] = None,
        requestType: int = 0,
    ) -> Dict[str, Any]:
        """
        Fetch files from an update and parse to array.

        Args:
            updateId: Update identifier (UUID)
            usePack: Language name in xx-xx format (optional)
            desiredEdition: Edition UUID (requires usePack to be specified)
            requestType: 0=uncached (default), 1=use cache, 2=offline retrieval

        Returns:
            Dictionary containing file information

        Raises:
            UUPDumpResponseError: If API returns an error (e.g., UNSUPPORTED_LANG, NO_FILES)
        """
        self.logger.info(
            f"Getting files for update {updateId} (lang={usePack}, edition={desiredEdition})"
        )

        params = {"id": updateId}
        if usePack:
            params["pack"] = usePack
        if desiredEdition:
            params["edition"] = desiredEdition
        if requestType:
            params["requestType"] = str(requestType)

        return self._get("get.php", params=params)

    def list_editions(
        self, lang: str, updateId: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List supported editions for a language and update.

        Args:
            lang: Language name in xx-xx format
            updateId: Update identifier (UUID, optional)

        Returns:
            Dictionary containing list of editions

        Raises:
            UUPDumpResponseError: If API returns an error (e.g., UNSUPPORTED_LANG)
        """
        self.logger.info(f"Listing editions for language {lang} (updateId={updateId})")

        params = {"lang": lang}
        if updateId:
            params["id"] = updateId

        return self._get("listeditions.php", params=params)

    def list_langs(
        self, updateId: Optional[str] = None, returnInfo: bool = False
    ) -> Dict[str, Any]:
        """
        List languages supported for an update.

        Args:
            updateId: Update identifier (UUID, optional)
            returnInfo: Should full update information be returned with languages

        Returns:
            Dictionary containing list of languages
        """
        self.logger.info(
            f"Listing languages (updateId={updateId}, returnInfo={returnInfo})"
        )

        params = {}
        if updateId:
            params["id"] = updateId
        if returnInfo:
            params["returnInfo"] = "true"

        return self._get("listlangs.php", params=params)

    def update_info(
        self, updateId: str, onlyInfo: Optional[str] = None, ignoreFiles: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed information about an update.

        Args:
            updateId: Update identifier (UUID)
            onlyInfo: Specific key to output (optional)
            ignoreFiles: Skip the 'files' key in output

        Returns:
            Dictionary containing update information

        Raises:
            UUPDumpResponseError: If API returns an error (e.g., UPDATE_INFORMATION_NOT_EXISTS)
        """
        self.logger.info(f"Getting update info for {updateId} (onlyInfo={onlyInfo})")

        params = {"id": updateId}
        if onlyInfo:
            params["onlyinfo"] = onlyInfo
        if ignoreFiles:
            params["ignoreFiles"] = "true"

        return self._get("updateinfo.php", params=params)

    def api_version(self) -> Dict[str, Any]:
        """
        Get the API version.

        Returns:
            Dictionary containing API version information
        """
        self.logger.info("Getting API version")
        return self._get("api_version.php")

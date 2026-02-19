# UUP Dump API - Python Module

A Python wrapper for the [UUP Dump API](https://uupdump.net/) with comprehensive logging and exception handling.

## Features

- ✅ Complete API coverage for all UUP Dump endpoints
- ✅ Comprehensive exception handling with custom error types
- ✅ Detailed logging at multiple levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Automatic retry and timeout handling
- ✅ Type hints for better IDE support
- ✅ User-friendly error messages mapped from API error codes

## Installation

```bash
pip install requests
```

## Quick Start

```python
from adapter import RestAdapter
from exceptions import UUPDumpAPIError

# Create API client
api = RestAdapter(timeout=10)

try:
    # Search for Windows 11 updates
    result = api.listid(search="Windows 11", sortByDate=True)
    
    if 'response' in result:
        builds = result['response']['builds']
        print(f"Found {len(builds)} updates")
        
except UUPDumpAPIError as e:
    print(f"Error: {e}")
```

## Logging

The module uses Python's built-in `logging` module for comprehensive logging.

### Basic Logging Setup

```python
import logging
from adapter import RestAdapter

# Create adapter with INFO level logging (default)
api = RestAdapter(log_level=logging.INFO)

# Or use DEBUG for detailed troubleshooting
api = RestAdapter(log_level=logging.DEBUG)
```

### Custom Logging Configuration

```python
import logging

# Configure logging manually
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='uup_api.log'  # Log to file
)

api = RestAdapter()
```

### Logging Levels

- **DEBUG**: Detailed information including request parameters and response status
- **INFO**: General information about operations (default)
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages when operations fail

### Example Log Output

```
2024-01-15 10:30:45 - adapter - INFO - Initialized UUP Dump API adapter (base_url=https://api.uupdump.net, timeout=10s)
2024-01-15 10:30:45 - adapter - INFO - Listing updates (search='Windows 11', sortByDate=True)
2024-01-15 10:30:45 - adapter - DEBUG - Making GET request to https://api.uupdump.net/listid.php with params: {'search': 'Windows 11', 'sortByDate': '1'}
2024-01-15 10:30:46 - adapter - DEBUG - Response status: 200
2024-01-15 10:30:46 - adapter - DEBUG - Request successful
```

## Exception Handling

The module provides custom exceptions for different error scenarios.

### Exception Hierarchy

```
UUPDumpAPIError (base exception)
├── UUPDumpHTTPError          # HTTP request failures
├── UUPDumpTimeoutError       # Request timeouts
├── UUPDumpConnectionError    # Connection failures
├── UUPDumpValidationError    # Invalid parameters
└── UUPDumpResponseError      # API-level errors
```

### Exception Usage

```python
from adapter import RestAdapter
from exceptions import (
    UUPDumpAPIError,
    UUPDumpResponseError,
    UUPDumpTimeoutError,
    UUPDumpConnectionError
)

api = RestAdapter(timeout=5)

try:
    result = api.fetchupd(arch="amd64", ring="Retail")
    
except UUPDumpResponseError as e:
    # API returned an error (e.g., NO_UPDATE_FOUND, UNKNOWN_ARCH)
    print(f"API Error: {e}")
    print(f"Error Code: {e.error_code}")
    
except UUPDumpTimeoutError as e:
    # Request timed out
    print(f"Timeout: {e}")
    
except UUPDumpConnectionError as e:
    # Could not connect to API
    print(f"Connection Error: {e}")
    
except UUPDumpAPIError as e:
    # Catch-all for any other errors
    print(f"Unexpected Error: {e}")
```

### API Error Codes

The module automatically maps API error codes to human-readable messages:

| Error Code | Description |
|------------|-------------|
| `UNKNOWN_ARCH` | Invalid architecture specified |
| `UNKNOWN_RING` | Invalid ring/channel specified |
| `NO_UPDATE_FOUND` | No update matching criteria |
| `UNSUPPORTED_LANG` | Unsupported language |
| `NO_FILES` | No files available for update |
| `WU_REQUEST_FAILED` | Windows Update request failed |
| ... | See `exceptions.py` for complete list |

## API Methods

### `listid(search, sortByDate)`
List available updates.

```python
result = api.listid(search="Windows 11", sortByDate=True)
```

### `fetchupd(arch, ring, flight, build, ...)`
Fetch update information from Windows Update.

```python
result = api.fetchupd(
    arch="amd64",
    ring="Retail",
    flight="Mainline",
    build="22621",
    sku=48
)
```

### `get_files(updateId, usePack, desiredEdition, ...)`
Get file list for an update.

```python
result = api.get_files(
    updateId="your-uuid-here",
    usePack="en-us",
    desiredEdition="professional"
)
```

### `list_editions(lang, updateId)`
List available editions.

```python
result = api.list_editions(lang="en-us", updateId="your-uuid-here")
```

### `list_langs(updateId, returnInfo)`
List available languages.

```python
result = api.list_langs(updateId="your-uuid-here")
```

### `update_info(updateId, onlyInfo, ignoreFiles)`
Get detailed update information.

```python
result = api.update_info(updateId="your-uuid-here", ignoreFiles=True)
```

### `api_version()`
Get API version.

```python
result = api.api_version()
```

## Complete Example

```python
import logging
from adapter import RestAdapter
from exceptions import UUPDumpAPIError, UUPDumpResponseError

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create API client
api = RestAdapter(timeout=10)

try:
    # 1. Search for updates
    print("Searching for updates...")
    search_result = api.listid(search="23H2", sortByDate=True)
    
    if 'response' in search_result:
        builds = search_result['response']['builds']
        update_id = list(builds.keys())[0]
        
        # 2. Get update info
        print(f"Getting info for {update_id}...")
        info = api.update_info(updateId=update_id)
        
        # 3. List languages
        print("Listing languages...")
        langs = api.list_langs(updateId=update_id)
        
        # 4. List editions
        print("Listing editions...")
        editions = api.list_editions(lang="en-us", updateId=update_id)
        
        print("Success!")

except UUPDumpResponseError as e:
    print(f"API Error [{e.error_code}]: {e}")
except UUPDumpAPIError as e:
    print(f"Error: {e}")
```

## Error Handling Best Practices

1. **Always catch specific exceptions first**, then fall back to the base exception:
   ```python
   try:
       result = api.fetchupd(...)
   except UUPDumpResponseError as e:
       # Handle API errors
   except UUPDumpTimeoutError as e:
       # Handle timeouts
   except UUPDumpAPIError as e:
       # Handle any other errors
   ```

2. **Check for error codes** in API responses:
   ```python
   try:
       result = api.fetchupd(arch="invalid")
   except UUPDumpResponseError as e:
       if e.error_code == "UNKNOWN_ARCH":
           print("Please use: amd64, x86, arm64, or all")
   ```

3. **Use appropriate logging levels**:
   - Development: `logging.DEBUG`
   - Production: `logging.INFO` or `logging.WARNING`

4. **Set reasonable timeouts** based on your use case:
   ```python
   # For interactive applications
   api = RestAdapter(timeout=10)
   
   # For background tasks
   api = RestAdapter(timeout=30)
   ```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
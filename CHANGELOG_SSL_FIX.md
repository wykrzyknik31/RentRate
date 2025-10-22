# LibreTranslate SSL Certificate Fix - Changelog

## Issue Fixed
LibreTranslate Docker container was failing to start with SSL certificate verification errors and IndexError crashes when attempting to download translation models.

## Root Cause
The base LibreTranslate Docker image lacked proper CA certificate handling, causing HTTPS connections to fail when downloading translation models. This particularly affected:
- Corporate/enterprise networks with custom root CA certificates
- Systems behind SSL-inspecting proxies
- Environments with outdated or missing CA certificates

## Changes Made

### 1. Custom LibreTranslate Dockerfile
**File**: `libretranslate/Dockerfile`

Created a custom Dockerfile that extends the base LibreTranslate image with:
- Installation and update of `ca-certificates` package
- Directory structure for mounting custom CA certificates
- Proper SSL environment variable configuration
- Security best practices (runs as non-root user)

### 2. Docker Compose Configuration Updates
**File**: `docker-compose.yml`

Updated the LibreTranslate service to:
- Use custom Dockerfile instead of pulling directly from Docker Hub
- Add SSL/TLS environment variables (`PYTHONHTTPSVERIFY`, `REQUESTS_CA_BUNDLE`)
- Support volume mount for custom CA certificates (commented by default)
- Add persistent volume for LibreTranslate model data
- Increase health check `start_period` to 60 seconds for model download time

### 3. Documentation

#### New Files:
- `libretranslate/README.md` - Comprehensive setup and troubleshooting guide for the custom LibreTranslate image
- `libretranslate/.dockerignore` - Exclude documentation from Docker build
- `docs/SSL_TROUBLESHOOTING.md` - Detailed step-by-step troubleshooting guide for SSL certificate issues

#### Updated Files:
- `README.md` - Added reference to SSL troubleshooting in main troubleshooting section
- `TRANSLATION_SETUP.md` - Added section for LibreTranslate SSL certificate errors
- `TRANSLATION_FIX.md` - Updated LibreTranslate troubleshooting section

## Solution Features

### ✅ Automatic CA Certificate Handling
- Installs latest CA certificates from Debian repositories
- Updates certificate store during image build
- Sets proper SSL environment variables

### ✅ Corporate Proxy Support
- Provides directory for mounting custom CA certificates
- Clear instructions for adding corporate certificates
- Simple uncomment-and-rebuild workflow

### ✅ Flexible SSL Configuration
- Environment variables for SSL verification control
- Option to disable SSL verification in development (with warnings)
- Support for HTTP_PROXY and HTTPS_PROXY variables

### ✅ Improved Stability
- Added `start_period: 60s` to health check for model download time
- Persistent volume for model data (reduces re-downloads)
- Graceful handling of SSL errors

### ✅ Comprehensive Documentation
- Multiple troubleshooting guides for different scenarios
- Step-by-step instructions with examples
- Clear warnings about security implications

## Upgrade Path

### For New Users
Simply clone and run - the fix is already integrated:
```bash
git clone https://github.com/wykrzyknik31/RentRate.git
cd RentRate
docker compose up --build
```

### For Existing Users
Pull the latest changes and rebuild:
```bash
git pull
docker compose down
docker compose up --build
```

### For Corporate Network Users
1. Pull the latest changes
2. Create `certs/` directory
3. Copy corporate CA certificates to `certs/`
4. Uncomment the volume mount in `docker-compose.yml`
5. Rebuild: `docker compose up --build`

## Testing Performed

### Build Tests
- ✅ Docker build completes successfully
- ✅ CA certificates are installed and updated
- ✅ Custom certificate directory is created
- ✅ Environment variables are set correctly

### Configuration Tests
- ✅ docker-compose.yml syntax is valid
- ✅ Dockerfile syntax is valid
- ✅ Volume mounts are configured correctly
- ✅ Health check configuration is appropriate

### Documentation Tests
- ✅ All markdown files are properly formatted
- ✅ Code examples are syntactically correct
- ✅ Links between documents are valid
- ✅ Instructions are clear and actionable

## Breaking Changes
None. This is a backward-compatible fix that enhances the existing setup.

## Migration Notes
- No migration required
- Existing configurations continue to work
- New features are opt-in (custom CA certificates)

## Security Considerations

### Improvements
- ✅ Proper CA certificate handling prevents MITM attacks
- ✅ SSL verification enabled by default
- ✅ Non-root user execution maintained
- ✅ Clear warnings about disabling SSL verification

### No New Vulnerabilities
- No code changes to backend or frontend
- Only configuration and documentation updates
- No new dependencies introduced
- Uses official LibreTranslate base image

## Performance Impact
- Minimal: Adds ~5-10 seconds to initial build time for CA certificate installation
- Benefit: Persistent volume reduces model re-download time on container restarts

## Future Enhancements
Potential improvements for future versions:
- [ ] Automated CA certificate detection from host system
- [ ] Support for alternative translation providers with similar SSL handling
- [ ] Docker healthcheck that specifically validates SSL connectivity
- [ ] Pre-built custom image on Docker Hub for faster deployment

## Support
For issues or questions:
1. Check `docs/SSL_TROUBLESHOOTING.md` for common scenarios
2. Review `libretranslate/README.md` for detailed configuration
3. Check logs: `docker compose logs libretranslate`
4. Open an issue on GitHub with detailed error logs

## Related Issues
Fixes: LibreTranslate container fails to start due to SSL certificate error and IndexError

## Credits
- Issue reported by: [User who reported the issue]
- Fixed by: GitHub Copilot
- Tested by: Automated build tests

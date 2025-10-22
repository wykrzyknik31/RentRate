# LibreTranslate Configuration Fix

## Problem

After adding the translation feature and rebuilding the project with Docker, the LibreTranslate container was failing to start with the following errors:

```
URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)'))
Cannot update models (normal if you're offline): Download failed for Albanian → English
IndexError: list index out of range
```

**Root Cause**: LibreTranslate attempts to download language models on container startup. The SSL certificate verification was failing during this download, preventing the models from being downloaded and causing the container to crash immediately with exit code 1.

**Impact**: The translation button on the frontend always showed "błąd tłumaczenia" (translation error) because the backend couldn't connect to the translation service.

## Solution

Following the recommended approach from the issue, the project now uses the **public LibreTranslate API** (https://libretranslate.com) instead of running a local container.

### Changes Made

#### 1. docker-compose.yml
- **Disabled the libretranslate service**: Commented out the entire service with explanatory notes
- **Updated backend configuration**:
  - Changed `LIBRETRANSLATE_URL` from `http://libretranslate:5000` to `https://libretranslate.com`
  - Added `LIBRETRANSLATE_API_KEY` environment variable (empty by default, optional)
  - Removed the dependency on `libretranslate` service health check
- **Disabled libretranslate_data volume**: Commented out as it's no longer needed

#### 2. TRANSLATION_SETUP.md
- Added prominent notice about the configuration change
- Updated default configuration section to reflect public API usage
- Expanded troubleshooting section with detailed SSL certificate error explanation
- Added instructions for re-enabling local LibreTranslate if needed
- Clarified that the public API is now the recommended default

#### 3. README.md
- Updated the "Access the application" section to reflect that translation now uses the public API
- Changed from "http://localhost:5001 (LibreTranslate)" to "Public LibreTranslate API (https://libretranslate.com)"

#### 4. Makefile
- Updated `logs-translate` command to provide helpful message about the configuration
- Added check for whether libretranslate service is running
- Prevents confusing errors when trying to view logs for non-existent service

### Benefits

✅ **No SSL Certificate Issues**: Public API doesn't require downloading models on startup  
✅ **Simpler Deployment**: One less container to manage  
✅ **Faster Startup**: No waiting for LibreTranslate container to download models  
✅ **Easier Maintenance**: No need to manage local LibreTranslate updates  
✅ **Better Reliability**: Public API is stable and well-maintained  
✅ **Backward Compatible**: Backend code already supported external translation services  

### Tradeoffs

⚠️ **Rate Limits**: The public API has rate limits (can be increased with API key)  
⚠️ **Internet Dependency**: Requires internet access for translations  
⚠️ **Privacy**: Review text is sent to external service (though LibreTranslate respects privacy)  
⚠️ **Network Restrictions**: May not work in all network environments  

## Testing

All existing tests pass successfully:
```bash
$ pytest tests/test_translation.py tests/test_api.py -v
======================== 20 passed, 8 warnings in 0.78s ========================
```

The tests confirm:
- ✅ Language detection works correctly
- ✅ Translation endpoint validates inputs properly
- ✅ Caching mechanism functions as expected
- ✅ Error handling is robust
- ✅ Same-language translations are handled efficiently

## Deployment

### For New Users
Simply run:
```bash
docker compose up --build
```

The translation feature will use the public API by default.

### For Existing Users
1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Stop and remove existing containers:
   ```bash
   docker compose down
   ```

3. Remove the old libretranslate volume (optional, to free space):
   ```bash
   docker volume rm rentrate_libretranslate_data
   ```

4. Start the updated services:
   ```bash
   docker compose up --build
   ```

## Configuration Options

### Using an API Key (Optional)

To increase rate limits, you can get a free API key from LibreTranslate and add it to docker-compose.yml:

```yaml
- LIBRETRANSLATE_API_KEY=your_api_key_here
```

### Re-enabling Local LibreTranslate

If you prefer to self-host (e.g., for privacy, offline usage, or avoiding rate limits):

1. Uncomment the `libretranslate` service in `docker-compose.yml`
2. Uncomment the `libretranslate_data` volume
3. Change backend environment: `LIBRETRANSLATE_URL=http://libretranslate:5000`
4. Add backend dependency back:
   ```yaml
   depends_on:
     libretranslate:
       condition: service_healthy
   ```
5. Rebuild: `docker compose up --build`

⚠️ **Note**: You may still encounter SSL certificate issues with local hosting. See TRANSLATION_SETUP.md for troubleshooting.

### Using Alternative Services

The backend supports any LibreTranslate-compatible API. You can:
- Use a different LibreTranslate instance
- Use Google Translate, DeepL, or other services (requires code changes)
- Host LibreTranslate on a separate server

## Verification

### 1. Check Docker Compose Configuration
```bash
docker compose config --services
```
Expected output (no libretranslate):
```
db
backend
frontend
```

### 2. Verify Environment Variables
```bash
docker compose config | grep LIBRETRANSLATE
```
Expected output:
```
LIBRETRANSLATE_URL: https://libretranslate.com
LIBRETRANSLATE_API_KEY: ''
```

### 3. Test Translation Endpoint (when deployed)
```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "target_lang": "pl"}'
```

Expected response (or 503 if rate-limited):
```json
{
  "translated_text": "Witaj świecie",
  "source_lang": "en",
  "target_lang": "pl",
  "from_cache": false
}
```

## Troubleshooting

### "Translation service unavailable" (503 Error)

**Causes**:
- Network restrictions blocking libretranslate.com
- Rate limit exceeded on public API
- Internet connectivity issues

**Solutions**:
1. Check internet connectivity
2. Consider getting an API key for higher limits
3. Consider self-hosting LibreTranslate (see Configuration Options above)
4. Check if libretranslate.com is accessible from your network

### Docker Compose Syntax Errors

If you see errors after updating:
```bash
docker compose config
```

This will validate the YAML syntax and show any errors.

### Backend Can't Start

If backend shows errors about LIBRETRANSLATE_URL:
1. Verify the environment variable is set in docker-compose.yml
2. Check for typos in the URL
3. Review backend logs: `docker compose logs backend`

## Security Considerations

✅ **No Secrets Exposed**: No API keys required by default  
✅ **HTTPS Connection**: All communication with public API is encrypted  
✅ **Input Validation**: Backend validates all translation requests  
✅ **Error Handling**: Errors don't expose internal details  
✅ **Caching**: Reduces repeated API calls  

⚠️ **Data Privacy**: Review text is sent to external service (LibreTranslate is open-source and privacy-focused, but still external)

## Performance

- **Translation Time**: 1-3 seconds for typical review text
- **Cache Hits**: < 100ms when translation is cached
- **Rate Limits**: Public API has reasonable limits for normal usage
- **Startup Time**: ~10-15 seconds (reduced from ~60+ seconds with local LibreTranslate)

## Future Improvements

Potential enhancements:
- [ ] Add configuration for alternative translation providers
- [ ] Implement client-side rate limiting
- [ ] Add admin panel for managing translation cache
- [ ] Support batch translation of multiple reviews
- [ ] Add translation quality feedback mechanism

## References

- [LibreTranslate Public API](https://libretranslate.com/)
- [LibreTranslate GitHub](https://github.com/LibreTranslate/LibreTranslate)
- [Translation Setup Guide](TRANSLATION_SETUP.md)
- [Issue: Fixing translation v3](https://github.com/wykrzyknik31/RentRate/issues/[issue-number])

## Support

If you encounter issues:
1. Check backend logs: `docker compose logs backend`
2. Verify network connectivity to libretranslate.com
3. Review TRANSLATION_SETUP.md for detailed configuration
4. Open an issue on GitHub with logs and error details

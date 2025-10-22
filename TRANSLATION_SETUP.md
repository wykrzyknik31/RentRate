# Translation Feature Setup Guide

## Overview

RentRate now includes an automatic translation feature that allows users to translate reviews written in different languages into their preferred UI language. The feature uses language detection and translation APIs to provide seamless multilingual support.

## Features

- **Automatic Language Detection**: Reviews are automatically detected for their language
- **Smart Translation Button**: Only shows for reviews in a language different from the current UI language
- **Translation Caching**: Translations are cached in the database to reduce API calls and improve performance
- **Loading States**: Visual feedback during translation with spinner animation
- **Error Handling**: Graceful error messages when translation fails
- **Toggle Original/Translated**: Users can switch between original and translated text
- **Multi-language Support**: Works with all languages supported by the translation provider

## How It Works

1. When reviews are loaded, the backend detects the language of each review's text
2. If a review's language differs from the UI language, a "Translate" button appears
3. Clicking the button sends the text to the translation API
4. The translated text is displayed and cached for future use
5. Users can toggle between original and translated text

## Translation Provider

The feature uses **LibreTranslate**, an open-source translation API that can be:
- Self-hosted for complete control and privacy
- Used via the public instance (with rate limits)
- Replaced with other providers (Google Translate, DeepL, etc.)

## Configuration

### Backend Environment Variables

Add these environment variables to configure the translation service:

```bash
# LibreTranslate API URL (default: public instance)
LIBRETRANSLATE_URL=https://libretranslate.com

# API Key (REQUIRED for public API - get free key at https://portal.libretranslate.com)
LIBRETRANSLATE_API_KEY=your_api_key_here
```

### Default Configuration with Docker Compose

**⚠️ IMPORTANT CHANGE**: As of the latest version, the project uses the **public LibreTranslate API** 
instead of a self-hosted instance. This was changed because the local LibreTranslate container 
was experiencing SSL certificate verification issues when downloading language models on startup.

The default `docker-compose.yml` now configures:
- Uses the public LibreTranslate API at `https://libretranslate.com`
- Automatically configured with `LIBRETRANSLATE_URL=https://libretranslate.com`
- **API key is REQUIRED** - get a free API key at https://portal.libretranslate.com
- No local LibreTranslate container to manage
- Simpler deployment and maintenance

**Getting Started**:

1. Get a free API key from https://portal.libretranslate.com
2. Create a `.env` file and add: `LIBRETRANSLATE_API_KEY=your-api-key-here`
3. Start all services:
```bash
docker-compose up -d
```

Note about the public instance:
- The public instance requires an API key for authentication
- Free tier is available with reasonable rate limits
- Service availability is generally good
- Network restrictions may prevent access in some environments

### Re-enabling Local LibreTranslate (Optional)

If you prefer to self-host LibreTranslate (e.g., for privacy, performance, or offline usage):

1. Uncomment the `libretranslate` service in `docker-compose.yml`
2. Update the backend environment variable to: `LIBRETRANSLATE_URL=http://libretranslate:5000`
3. Add the backend dependency on libretranslate service health check
4. Uncomment the `libretranslate_data` volume
5. Rebuild: `docker compose up --build`

⚠️ Note: The local container may experience SSL certificate issues when downloading language models. 
If you encounter these issues, refer to the troubleshooting section below.

### Self-Hosting LibreTranslate Separately

To self-host LibreTranslate outside of docker-compose:

1. **Using Docker**:
```bash
docker run -d -p 5001:5000 libretranslate/libretranslate
```

2. **Update the environment variable**:
```bash
LIBRETRANSLATE_URL=http://localhost:5001
```

3. **For production**, follow the [LibreTranslate documentation](https://github.com/LibreTranslate/LibreTranslate)

### Using Alternative Translation Providers

To use Google Translate, DeepL, or other providers:

1. Modify the `/api/translate` endpoint in `backend/app.py`
2. Replace the LibreTranslate API call with your chosen provider's API
3. Update the environment variables accordingly

Example providers:
- **Google Cloud Translation API**: High quality, pay-per-use
- **DeepL API**: High quality, limited free tier
- **Azure Translator**: Enterprise-grade, Microsoft Azure
- **AWS Translate**: Scalable, Amazon Web Services

## API Endpoints

### Detect Language
```
POST /api/detect-language
Content-Type: application/json

{
  "text": "Hello world"
}
```

Response:
```json
{
  "detected_language": "en",
  "confidence": 0.99,
  "all_detected": [
    {"lang": "en", "prob": 0.99}
  ]
}
```

### Translate Text
```
POST /api/translate
Content-Type: application/json

{
  "text": "Hello world",
  "target_lang": "es",
  "source_lang": "en"  // optional, will be auto-detected if not provided
}
```

Response:
```json
{
  "translated_text": "Hola mundo",
  "source_lang": "en",
  "target_lang": "es",
  "from_cache": false
}
```

## Database Schema

The translation cache is stored in the `Translation` table:

```sql
CREATE TABLE translation (
    id INTEGER PRIMARY KEY,
    original_text TEXT NOT NULL,
    source_lang VARCHAR(10) NOT NULL,
    target_lang VARCHAR(10) NOT NULL,
    translated_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_translation_lookup ON translation(original_text, source_lang, target_lang);
```

## Supported Languages

The feature supports all languages that LibreTranslate supports. Common languages include:

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Polish (pl)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And many more...

## Performance Considerations

1. **Caching**: Translations are cached to reduce API calls
2. **Async Detection**: Language detection happens in the background
3. **Rate Limiting**: Consider implementing rate limiting for the translation endpoint
4. **Cost**: Self-hosting is recommended for high-volume applications

## Privacy Notice

When using external translation APIs:
- Review text is sent to the translation service
- Consider adding a privacy notice in your terms of service
- Self-hosting provides complete data control
- LibreTranslate is open-source and respects privacy

## Troubleshooting

### Translation Button Not Showing
- Check that language detection is working: `/api/detect-language`
- Verify the review has text content
- Ensure the detected language differs from UI language

### Translation Fails with 503 Error
- The translation service may be unavailable
- Check `LIBRETRANSLATE_URL` is correct
- Try self-hosting LibreTranslate
- Check API key if required

### LibreTranslate Container Fails to Start (SSL Certificate Error)
If you're trying to use the local LibreTranslate container and see SSL certificate verification errors:
```
URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]'))
Cannot update models (normal if you're offline): Download failed for Albanian → English
IndexError: list index out of range
```

**Root Cause**: LibreTranslate tries to download language models on startup, but SSL certificate 
verification fails, causing the container to crash.

**Recommended Solution**: Use the public LibreTranslate API (default configuration):
- The public API is stable and doesn't require downloading models
- No SSL certificate issues
- Simpler deployment
- Already configured in the default `docker-compose.yml`

**Alternative Solutions** (if you need to self-host):
1. **Disable SSL verification** (not recommended for production):
   - Set `PYTHONHTTPSVERIFY=0` in the libretranslate service environment
   
2. **For corporate networks with custom CA certificates**:
   - Create a `certs` directory and add your CA certificate files
   - Uncomment the volume mount in `docker-compose.yml`
   - Rebuild: `docker compose up --build`
   
3. **Use pre-downloaded models**:
   - Configure LibreTranslate to use offline mode with pre-installed models
   - See [LibreTranslate documentation](https://github.com/LibreTranslate/LibreTranslate) for details

See `libretranslate/README.md` for detailed instructions on self-hosting.

### Slow Translation Performance
- Consider self-hosting for better performance
- Ensure database indexes are created
- Check network latency to translation service

### Cache Not Working
- Verify the Translation table exists
- Check database write permissions
- Look for errors in backend logs

## Testing

Run the translation tests:
```bash
pytest tests/test_translation.py -v
```

The test suite covers:
- Language detection
- Translation with caching
- Error handling
- API validation

## Future Enhancements

Potential improvements:
- Batch translation for multiple reviews
- User preference for auto-translate
- Translation quality feedback
- Support for multiple translation providers
- Translation of property addresses
- Translation history and management

## Support

For issues or questions:
1. Check the backend logs for error messages
2. Verify API endpoint connectivity
3. Review the LibreTranslate documentation
4. Open an issue on the GitHub repository

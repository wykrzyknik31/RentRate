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

# API Key (optional, required for some instances)
LIBRETRANSLATE_API_KEY=your_api_key_here
```

### Default Configuration with Docker Compose

The default `docker-compose.yml` includes a self-hosted LibreTranslate instance:
- LibreTranslate runs as a service in the Docker network
- Automatically configured with `LIBRETRANSLATE_URL=http://libretranslate:5000`
- No API key required
- Better performance and privacy than public instance
- No rate limits

To start all services including LibreTranslate:
```bash
docker-compose up -d
```

### Using the Public LibreTranslate Instance

To use the public LibreTranslate instance at `https://libretranslate.com` instead:
1. Remove the `libretranslate` service from `docker-compose.yml`
2. Update the backend environment variable:
```bash
LIBRETRANSLATE_URL=https://libretranslate.com
```

Note that:
- The public instance has rate limits
- No API key is required
- Service availability may vary
- Network restrictions may prevent access

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
If you see SSL certificate verification errors in the logs:
```
URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]'))
IndexError: list index out of range
```

**Solution**: The custom LibreTranslate Dockerfile already addresses this issue by:
- Installing and updating CA certificates
- Configuring SSL environment variables
- Supporting custom CA certificates for corporate proxies

**For corporate networks with custom CA certificates**:
1. Create a `certs` directory and add your CA certificate files
2. Uncomment the volume mount in `docker-compose.yml`
3. Rebuild: `docker compose up --build`

See `libretranslate/README.md` for detailed instructions.

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

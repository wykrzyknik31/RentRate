# Translation Feature Setup Guide

## Overview

RentRate includes an automatic translation feature that allows users to translate reviews written in different languages into their preferred UI language. The feature uses Google Translate API for reliable, high-quality translations with extensive language support.

## Features

- **Automatic Language Detection**: Reviews are automatically detected for their language
- **Smart Translation Button**: Only shows for reviews in a language different from the current UI language
- **Translation Caching**: Translations are cached in the database to reduce API calls and improve performance
- **Loading States**: Visual feedback during translation with spinner animation
- **Error Handling**: Graceful error messages when translation fails
- **Toggle Original/Translated**: Users can switch between original and translated text
- **Multi-language Support**: Supports 100+ languages via Google Translate API
- **High Quality**: Enterprise-grade translation quality from Google's advanced neural machine translation

## How It Works

1. When reviews are loaded, the backend detects the language of each review's text
2. If a review's language differs from the UI language, a "Translate" button appears
3. Clicking the button sends the text to Google Translate API
4. The translated text is displayed and cached for future use
5. Users can toggle between original and translated text

## Translation Provider

The feature uses **Google Cloud Translation API**, which provides:
- ✅ Reliable and stable API with 99.9% uptime SLA
- ✅ High translation quality with neural machine translation
- ✅ Support for 100+ languages
- ✅ Automatic language detection
- ✅ No SSL issues or container dependencies
- ✅ Easy to configure and maintain

## Configuration

### Prerequisites

Before setting up translation, you need a Google Cloud API key:

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Cloud Translation API**
   - In your project, go to "APIs & Services" > "Library"
   - Search for "Cloud Translation API"
   - Click on it and press "Enable"

3. **Create API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key (you can restrict it to Translation API for security)

### Backend Environment Variables

Add the Google Translate API key to your environment:

```bash
# Google Translate API Key (required for translation features)
GOOGLE_TRANSLATE_API_KEY=your-google-api-key-here
```

### Configuration with Docker Compose

The `.env` file should include:

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your Google Translate API key
GOOGLE_TRANSLATE_API_KEY=your-google-api-key-here
```

To start all services:
```bash
docker compose up -d
```

### Local Development Setup

For local development without Docker:

1. **Install backend dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variable**:
```bash
# On Linux/Mac
export GOOGLE_TRANSLATE_API_KEY=your-google-api-key-here

# On Windows
set GOOGLE_TRANSLATE_API_KEY=your-google-api-key-here
```

3. **Start the backend**:
```bash
python app.py
```

## Pricing

Google Cloud Translation API pricing (as of 2024):
- **Free tier**: $10 credit per month (approximately 500,000 characters)
- **Pay-as-you-go**: $20 per million characters
- **Translation API Basic**: Best for most use cases
- **Translation API Advanced**: For higher quality and additional features

For most small to medium applications, the free tier is sufficient. Monitor usage in the Google Cloud Console.

## Security Best Practices

1. **API Key Security**:
   - Never commit API keys to version control
   - Use environment variables for API keys
   - Restrict API key to Translation API only
   - Set up API key restrictions (HTTP referrer or IP address)

2. **Rate Limiting**:
   - Implement rate limiting in your application
   - Cache translations to reduce API calls
   - Monitor usage to avoid unexpected charges

3. **Error Handling**:
   - Implement proper error handling for API failures
   - Provide fallback behavior when translation is unavailable
   - Log errors for monitoring and debugging

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

Google Translate API supports 100+ languages. Common languages include:

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
- Hindi (hi)
- Turkish (tr)
- Vietnamese (vi)
- And 85+ more languages...

For the complete list, see [Google Translate Language Support](https://cloud.google.com/translate/docs/languages).

## Performance Considerations

1. **Caching**: Translations are cached to reduce API calls and costs
2. **Async Detection**: Language detection happens in the background
3. **Rate Limiting**: Consider implementing rate limiting for the translation endpoint
4. **Cost Optimization**: Monitor usage and implement caching strategies
5. **Batch Processing**: For large volumes, consider batch translation requests

## Privacy Notice

When using Google Translate API:
- Review text is sent to Google's translation service
- Data is processed according to [Google Cloud Privacy Policy](https://cloud.google.com/terms/cloud-privacy-notice)
- Consider adding a privacy notice in your terms of service
- Google does not use customer data to train their models
- Data is encrypted in transit and at rest

## Troubleshooting

### Translation Button Not Showing
- Check that language detection is working: `/api/detect-language`
- Verify the review has text content
- Ensure the detected language differs from UI language

### Translation Fails with 503 Error
**Symptoms**: Translation requests return "Translation service not configured"

**Solution**:
1. Verify `GOOGLE_TRANSLATE_API_KEY` is set in your `.env` file
2. Check that the API key is valid in Google Cloud Console
3. Ensure Cloud Translation API is enabled for your project
4. Restart the backend service after adding the API key:
   ```bash
   docker compose restart backend
   ```

### Translation Fails with 400 Error
**Symptoms**: Translation requests return invalid parameter errors

**Solution**:
1. Check that the language codes are valid (e.g., 'en', 'es', 'pl')
2. Ensure the text is not empty
3. Verify the API key has not expired or been revoked

### High API Costs
**Symptoms**: Unexpected charges from Google Cloud

**Solution**:
1. Check translation cache is working (monitor database)
2. Review API usage in Google Cloud Console
3. Set up budget alerts in Google Cloud
4. Implement rate limiting in your application
5. Consider caching more aggressively

### API Key Security Issues
**Symptoms**: Unauthorized API usage or exposed API key

**Solution**:
1. Regenerate the API key immediately
2. Add API key restrictions (HTTP referrer or IP address)
3. Review and restrict API key to only Translation API
4. Check application logs for suspicious activity
5. Set up Cloud Monitoring alerts

### Slow Translation Performance
**Symptoms**: Translations take a long time to complete

**Solution**:
1. Check your internet connection speed
2. Ensure translation cache is working (check database)
3. Monitor Google Cloud Translation API latency
4. Consider using a CDN or regional endpoints
5. Review network routing and firewall rules

### Cache Not Working
**Symptoms**: Same translations trigger API calls repeatedly

**Solution**:
1. Verify the Translation table exists in the database
2. Check database write permissions
3. Review backend logs for cache errors
4. Ensure database migrations have run
5. Check database connection is stable

## Testing

Run the translation tests:
```bash
cd /home/runner/work/RentRate/RentRate
pytest tests/test_translation*.py -v
```

The test suite covers:
- Language detection
- Translation with Google Translate API
- Translation caching
- Error handling and edge cases
- API configuration
- Logging and monitoring

All tests use mocked Google Translate API responses to avoid actual API calls during testing.

## Monitoring and Analytics

### Google Cloud Console

Monitor your translation usage:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Dashboard"
4. Click on "Cloud Translation API"
5. View usage metrics, quotas, and errors

### Application Logs

The backend logs detailed information about translations:
- Translation requests (source, target, text length)
- Successful translations
- Errors with full tracebacks
- Cache hits and misses

View logs:
```bash
# Docker
docker compose logs backend -f

# Local development
# Check console output where app.py is running
```

## Future Enhancements

Potential improvements:
- Batch translation for multiple reviews
- User preference for auto-translate
- Translation quality feedback
- Support for multiple translation providers (DeepL, Azure, AWS)
- Translation of property addresses and landlord names
- Translation history and management dashboard
- Cost tracking and budget management
- A/B testing different translation providers

## Support

For issues or questions:
1. Check the backend logs for detailed error messages
2. Verify Google Cloud Translation API is enabled
3. Review [Google Cloud Translation API documentation](https://cloud.google.com/translate/docs)
4. Check [Google Cloud Status Dashboard](https://status.cloud.google.com/)
5. Open an issue on the GitHub repository with:
   - Error messages from logs
   - Steps to reproduce
   - Environment details (Docker/local, OS, etc.)

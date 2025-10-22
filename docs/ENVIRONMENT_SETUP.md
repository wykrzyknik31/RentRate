# Environment Configuration Guide

This guide explains how to configure RentRate using environment variables.

## Quick Start

RentRate works out-of-the-box with sensible defaults. You don't need to create a `.env` file unless you want to customize the configuration.

## Creating a Custom Configuration

If you want to customize settings:

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your preferred settings

3. **Restart the services:**
   ```bash
   docker compose down
   docker compose up -d
   ```

## Available Environment Variables

### Database Configuration

```bash
POSTGRES_USER=rentrate          # PostgreSQL username
POSTGRES_PASSWORD=rentrate      # PostgreSQL password
POSTGRES_DB=rentrate            # PostgreSQL database name
```

**Note:** These are used by both the database and backend services.

### Backend Configuration

```bash
FLASK_ENV=development           # Flask environment (development/production)
SECRET_KEY=your-secret-key      # Secret key for JWT tokens (MUST change in production)
```

**Security Warning:** Always use a strong, random secret key in production environments.

### Translation Service Configuration

```bash
LIBRETRANSLATE_URL=https://libretranslate.com    # Translation service URL
LIBRETRANSLATE_API_KEY=                          # Optional API key for higher rate limits
```

#### Translation Service Options

**Option 1: Public LibreTranslate API (Default)**
```bash
LIBRETRANSLATE_URL=https://libretranslate.com
LIBRETRANSLATE_API_KEY=
```
- ✅ No setup required
- ✅ Works immediately
- ⚠️ Has rate limits
- ⚠️ Requires internet connection

**Option 2: Public LibreTranslate API with API Key**
```bash
LIBRETRANSLATE_URL=https://libretranslate.com
LIBRETRANSLATE_API_KEY=your_api_key_here
```
- ✅ Higher rate limits
- ✅ More reliable for production
- 💰 Free tier available at https://libretranslate.com

**Option 3: Self-Hosted LibreTranslate**
```bash
LIBRETRANSLATE_URL=http://libretranslate:5000
LIBRETRANSLATE_API_KEY=
```
- ✅ No rate limits
- ✅ Works offline
- ✅ Better privacy
- ⚠️ Requires uncommenting service in docker-compose.yml
- ⚠️ Uses more resources (~500MB RAM, ~1GB disk)

**Option 4: Custom Translation Service**
```bash
LIBRETRANSLATE_URL=https://your-custom-instance.com
LIBRETRANSLATE_API_KEY=your_api_key
```
- Use your own LibreTranslate instance
- Or any LibreTranslate-compatible API

### Frontend Configuration

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000    # Backend API URL
```

**Note:** This should match where your backend is accessible from the browser.

## Verifying Your Configuration

### 1. Check Environment Variables Are Loaded

```bash
docker compose config | grep LIBRETRANSLATE
```

Expected output:
```
LIBRETRANSLATE_API_KEY: ""
LIBRETRANSLATE_URL: https://libretranslate.com
```

### 2. Check Backend Container Environment

```bash
docker compose exec backend env | grep LIBRETRANSLATE
```

Expected output:
```
LIBRETRANSLATE_URL=https://libretranslate.com
LIBRETRANSLATE_API_KEY=
```

### 3. Test Translation Endpoint

Start the services:
```bash
docker compose up -d
```

Test the translation API:
```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "target_lang": "pl"}'
```

Expected response:
```json
{
  "translated_text": "Witaj świecie",
  "source_lang": "en",
  "target_lang": "pl",
  "from_cache": false
}
```

### 4. Test Language Detection

```bash
curl -X POST http://localhost:5000/api/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

Expected response:
```json
{
  "detected_language": "en",
  "confidence": 0.99,
  "all_detected": [{"lang": "en", "prob": 0.99}]
}
```

## Troubleshooting

### "Translation service unavailable" (503 Error)

**Possible causes:**
1. No internet connection to libretranslate.com
2. Rate limit exceeded
3. Network firewall blocking the request

**Solutions:**
1. Check internet connectivity: `curl https://libretranslate.com`
2. Get an API key for higher limits
3. Use self-hosted LibreTranslate (see Option 3 above)
4. Check backend logs: `docker compose logs backend`

### Environment Variables Not Loading

**Issue:** Changes to `.env` not reflected in containers

**Solution:**
1. Stop all services: `docker compose down`
2. Rebuild if needed: `docker compose build`
3. Start services: `docker compose up -d`

**Note:** Docker Compose reads `.env` on startup. Changes require a restart.

### Backend Can't Connect to Translation Service

**Issue:** "Connection refused" or "Name resolution failed"

**Solutions:**

For public API:
```bash
# Test connectivity
curl https://libretranslate.com/languages
```

For self-hosted:
```bash
# Check service is running
docker compose ps | grep libretranslate

# Check logs
docker compose logs libretranslate
```

## Security Best Practices

### For Development

The default configuration is fine for development:
```bash
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
```

### For Production

**MUST** change these settings:

1. **Generate a strong secret key:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Update your `.env` file:**
   ```bash
   FLASK_ENV=production
   SECRET_KEY=<your-generated-secret-key>
   POSTGRES_PASSWORD=<strong-password>
   ```

3. **Never commit `.env` to version control**
   - The `.env` file is already in `.gitignore`
   - Use `.env.example` as a template for others

## Advanced Configuration

### Using Multiple Environments

Create separate `.env` files for different environments:

```bash
.env.development
.env.staging
.env.production
```

Then specify which to use:
```bash
cp .env.production .env
docker compose up -d
```

### Overriding Environment Variables

You can override settings without editing `.env`:

```bash
LIBRETRANSLATE_URL=https://custom.com docker compose up -d
```

Or in docker-compose.yml:
```yaml
environment:
  - LIBRETRANSLATE_URL=https://custom.com
```

## Getting Help

If you encounter issues:

1. **Check the logs:**
   ```bash
   docker compose logs backend
   docker compose logs frontend
   docker compose logs db
   ```

2. **Verify configuration:**
   ```bash
   docker compose config
   ```

3. **Check service status:**
   ```bash
   docker compose ps
   ```

4. **Review documentation:**
   - [TRANSLATION_SETUP.md](../TRANSLATION_SETUP.md)
   - [LIBRETRANSLATE_FIX.md](../LIBRETRANSLATE_FIX.md)
   - [README.md](../README.md)

5. **Open an issue on GitHub** with:
   - Your configuration (sanitized, no passwords)
   - Error messages
   - Relevant logs

## References

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [LibreTranslate API Documentation](https://libretranslate.com/docs/)
- [Flask Configuration](https://flask.palletsprojects.com/en/latest/config/)

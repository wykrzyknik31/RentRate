# SSL Certificate Troubleshooting Guide

This guide helps resolve SSL certificate issues with the LibreTranslate service in RentRate.

## Problem Overview

When starting the LibreTranslate Docker container, you might encounter errors like:

```
URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)'))
IndexError: list index out of range
```

This occurs when LibreTranslate tries to download translation models over HTTPS but cannot verify SSL certificates.

## Common Scenarios

### 1. Corporate/Enterprise Network
You're behind a corporate proxy that uses custom root CA certificates.

**Solution**: Mount your custom CA certificates
```bash
# 1. Create certs directory
mkdir -p certs

# 2. Copy your corporate CA certificate
cp /path/to/corporate-ca.crt certs/

# 3. Edit docker-compose.yml and uncomment the volume mount:
# - ./certs:/usr/local/share/ca-certificates/custom:ro

# 4. Rebuild and restart
docker compose down
docker compose up --build
```

### 2. Outdated System CA Certificates
Your Docker host has outdated CA certificates.

**Solution**: The custom Dockerfile automatically updates CA certificates. Just rebuild:
```bash
docker compose build libretranslate
docker compose up
```

### 3. Restricted Network with SSL Inspection
Your network performs SSL inspection/MITM.

**Solution**: Same as corporate network - add your organization's SSL inspection certificate to the `certs/` directory.

### 4. Development Environment (Not Recommended for Production)
You need to quickly test without SSL verification.

**Solution**: Disable SSL verification in docker-compose.yml:
```yaml
environment:
  - PYTHONHTTPSVERIFY=0  # WARNING: Not secure!
```

## Step-by-Step Fix

1. **Check if you're affected**:
   ```bash
   docker compose logs libretranslate | grep -i ssl
   ```

2. **Try the automatic fix** (rebuild with CA certificates):
   ```bash
   docker compose down
   docker compose build libretranslate
   docker compose up
   ```

3. **If still failing**, check if you need custom CA certificates:
   ```bash
   # On your host system
   ls /etc/ssl/certs/ | grep -i custom
   # or
   echo $SSL_CERT_FILE
   ```

4. **Add custom certificates** if needed:
   ```bash
   mkdir -p certs
   # Copy all custom CA certificates
   cp /etc/pki/ca-trust/source/anchors/*.crt certs/ 2>/dev/null || \
   cp /usr/local/share/ca-certificates/*.crt certs/ 2>/dev/null
   ```

5. **Update docker-compose.yml** to mount the certificates:
   ```yaml
   volumes:
     - ./certs:/usr/local/share/ca-certificates/custom:ro
   ```

6. **Rebuild and verify**:
   ```bash
   docker compose up --build
   docker compose logs libretranslate
   ```

## Verifying the Fix

Once the container starts successfully, verify it's working:

```bash
# 1. Check container is healthy
docker compose ps libretranslate
# Should show "healthy" status

# 2. Test the API
curl http://localhost:5001/languages
# Should return a list of supported languages

# 3. Test translation
curl -X POST http://localhost:5001/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"Hello","source":"en","target":"es","format":"text"}'
# Should return translated text
```

## Environment Variables

You can customize SSL behavior with these environment variables in `docker-compose.yml`:

```yaml
environment:
  # Enable/disable Python HTTPS verification (1=enabled, 0=disabled)
  - PYTHONHTTPSVERIFY=1
  
  # Path to CA certificate bundle
  - REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
  
  # For corporate proxies
  - HTTP_PROXY=http://proxy.company.com:8080
  - HTTPS_PROXY=http://proxy.company.com:8080
  - NO_PROXY=localhost,127.0.0.1,libretranslate
```

## Advanced: Building with Custom Base Image

If you need more control, you can modify `libretranslate/Dockerfile`:

```dockerfile
FROM libretranslate/libretranslate:latest

USER root

# Install additional tools
RUN apt-get update && \
    apt-get install -y ca-certificates openssl && \
    update-ca-certificates

# Add your custom CA certificate directly
COPY corporate-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

USER libretranslate
```

## Getting Help

If you're still experiencing issues:

1. **Check logs in detail**:
   ```bash
   docker compose logs libretranslate --tail=100
   ```

2. **Verify network connectivity**:
   ```bash
   docker compose exec libretranslate curl -v https://www.google.com
   ```

3. **Check certificate installation**:
   ```bash
   docker compose exec libretranslate ls -la /etc/ssl/certs/
   docker compose exec libretranslate ls -la /usr/local/share/ca-certificates/
   ```

4. **Test Python SSL from inside container**:
   ```bash
   docker compose exec libretranslate python -c "import ssl; print(ssl.get_default_verify_paths())"
   ```

5. **Open an issue** on GitHub with:
   - Full error logs
   - Your environment details (OS, Docker version)
   - Network configuration (proxy, firewall, etc.)

## Related Documentation

- [LibreTranslate Setup](../libretranslate/README.md)
- [Translation Setup Guide](../TRANSLATION_SETUP.md)
- [Docker Implementation](../DOCKER_IMPLEMENTATION.md)

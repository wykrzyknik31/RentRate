# LibreTranslate Custom Dockerfile

This directory contains a custom Dockerfile for LibreTranslate that addresses SSL certificate verification issues.

## Problem Solved

The base LibreTranslate image sometimes fails to start due to SSL certificate verification errors when downloading translation models. This happens particularly in:
- Environments behind corporate proxies with custom CA certificates
- Systems with outdated or missing CA certificates
- Restricted network environments

## Solution

This custom Dockerfile extends the base LibreTranslate image with:
1. **Updated CA certificates**: Installs and updates `ca-certificates` package
2. **Custom CA certificate support**: Provides a directory for mounting custom certificates
3. **SSL configuration**: Sets environment variables for proper SSL/TLS handling

## Usage

### Standard Usage
The docker-compose.yml is already configured to use this custom Dockerfile. Simply run:
```bash
docker compose up --build
```

### For Corporate Proxies with Custom CA Certificates

If you're behind a corporate proxy with custom root CA certificates:

1. Create a `certs` directory in the project root:
   ```bash
   mkdir -p certs
   ```

2. Copy your custom CA certificate file(s) to the `certs` directory:
   ```bash
   cp /path/to/your/corporate-ca.crt certs/
   ```

3. Uncomment the volume mount in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./certs:/usr/local/share/ca-certificates/custom:ro
   ```

4. Rebuild and restart the container:
   ```bash
   docker compose down
   docker compose up --build
   ```

The custom CA certificates will be automatically loaded and trusted.

## Disabling SSL Verification (Not Recommended)

If you're in a development environment and need to disable SSL verification entirely, you can set the environment variable in docker-compose.yml:

```yaml
environment:
  - PYTHONHTTPSVERIFY=0
```

**Warning**: This is NOT recommended for production as it makes your application vulnerable to man-in-the-middle attacks.

## Troubleshooting

### Container Still Fails to Start

1. **Check logs**:
   ```bash
   docker compose logs libretranslate
   ```

2. **Verify CA certificates are installed**:
   ```bash
   docker compose exec libretranslate ls -la /etc/ssl/certs/
   ```

3. **Test SSL connectivity**:
   ```bash
   docker compose exec libretranslate curl -v https://www.google.com
   ```

### Models Not Downloading

If models still fail to download:
1. Check your internet connection
2. Verify proxy settings if behind a corporate firewall
3. Check if ports are blocked by firewall
4. Try pulling models manually (see LibreTranslate documentation)

### Custom CA Certificate Not Working

1. Verify the certificate is in PEM format
2. Ensure the certificate file has `.crt` extension
3. Check file permissions (should be readable)
4. Rebuild the container after adding certificates:
   ```bash
   docker compose up --build
   ```

## Technical Details

### Environment Variables
- `PYTHONHTTPSVERIFY`: Controls Python's SSL verification (1=enabled, 0=disabled)
- `REQUESTS_CA_BUNDLE`: Path to CA certificate bundle for requests library

### Volume Mounts
- `/usr/local/share/ca-certificates/custom`: Directory for custom CA certificates
- `/home/libretranslate/.local`: LibreTranslate data directory (for model persistence)

### Health Check
The container includes a health check that:
- Verifies the `/languages` endpoint is accessible
- Runs every 30 seconds
- Times out after 10 seconds
- Allows 60 seconds for initial startup (model download time)

## References

- [LibreTranslate GitHub](https://github.com/LibreTranslate/LibreTranslate)
- [LibreTranslate Documentation](https://libretranslate.com/docs/)
- [CA Certificates in Docker](https://docs.docker.com/engine/security/certificates/)

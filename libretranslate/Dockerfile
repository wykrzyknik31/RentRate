# Custom LibreTranslate Dockerfile with CA certificates support
FROM libretranslate/libretranslate:latest

# Switch to root to install packages
USER root

# Install ca-certificates and update certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directory for custom CA certificates
RUN mkdir -p /usr/local/share/ca-certificates/custom

# Environment variables for SSL configuration
# Users can set these to disable SSL verification if needed (not recommended)
ENV PYTHONHTTPSVERIFY=1
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Switch back to non-root user for security
USER libretranslate

# The rest of the configuration comes from the base image

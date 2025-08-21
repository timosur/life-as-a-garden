#!/bin/sh
set -e

# Create htpasswd file with environment variables
if [ -n "$AUTH_USER" ] && [ -n "$AUTH_PASS" ]; then
    echo "Creating htpasswd file for user: $AUTH_USER"
    htpasswd -bc /etc/nginx/.htpasswd "$AUTH_USER" "$AUTH_PASS"
else
    echo "Warning: AUTH_USER or AUTH_PASS not set, using default credentials"
    htpasswd -bc /etc/nginx/.htpasswd "garden" "changeme123"
fi

# Execute the original command
exec "$@"

#!/bin/bash

# Simple script to create htpasswd file for basic auth
# Usage: ./create-htpasswd.sh username password

if [ $# -ne 2 ]; then
    echo "Usage: $0 <username> <password>"
    echo "Example: $0 garden mySecretPassword123"
    exit 1
fi

USERNAME=$1
PASSWORD=$2

# Create htpasswd file
echo "Creating htpasswd file for user: $USERNAME"
htpasswd -bc /etc/nginx/.htpasswd "$USERNAME" "$PASSWORD"

echo "htpasswd file created successfully!"
echo "User: $USERNAME"
echo "File location: /etc/nginx/.htpasswd"

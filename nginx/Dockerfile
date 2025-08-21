FROM nginx:alpine

# Install openssl for dhparam generation and apache2-utils for htpasswd
RUN apk add --no-cache openssl apache2-utils

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Use nginx configuration file from the build context
COPY nginx.conf /etc/nginx/nginx.conf

# Copy htpasswd creation script
COPY create-htpasswd.sh /tmp/create-htpasswd.sh
RUN chmod +x /tmp/create-htpasswd.sh

# Create htpasswd file with default credentials (change these!)
# You can override these with environment variables
ARG AUTH_USER=garden
ARG AUTH_PASS=changeme123
RUN /tmp/create-htpasswd.sh "$AUTH_USER" "$AUTH_PASS"

# Create directory for Let's Encrypt challenges
RUN mkdir -p /var/www/certbot

# Generate dhparam file for better security
RUN openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Create log directory
RUN mkdir -p /var/log/nginx

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

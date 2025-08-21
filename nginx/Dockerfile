FROM nginx:alpine

# Install openssl for dhparam generation and apache2-utils for htpasswd
RUN apk add --no-cache openssl apache2-utils

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Use nginx configuration file from the build context
COPY nginx.conf /etc/nginx/nginx.conf

# Copy and setup entrypoint script for runtime credential setup
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create directory for Let's Encrypt challenges
RUN mkdir -p /var/www/certbot

# Generate dhparam file for better security
RUN openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Create log directory
RUN mkdir -p /var/log/nginx

# Expose ports
EXPOSE 80 443

# Set entrypoint and start nginx
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

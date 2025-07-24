FROM nginx:alpine

# Install openssl for dhparam generation (only needed for production)
RUN apk add --no-cache openssl

# Copy nginx configurations
COPY nginx*.conf /etc/nginx/

# Use local config by default, can be overridden in production
COPY nginx.local.conf /etc/nginx/nginx.conf

# Create directory for Let's Encrypt challenges (only used in production)
RUN mkdir -p /var/www/certbot

# Generate dhparam file for better security (only used in production)
RUN openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Create log directory
RUN mkdir -p /var/log/nginx

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

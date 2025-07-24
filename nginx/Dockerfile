FROM nginx:alpine

# Install openssl for dhparam generation
RUN apk add --no-cache openssl

# Use nginx configuration file from the build context
COPY nginx.conf /etc/nginx/nginx.conf

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

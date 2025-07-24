#!/bin/bash

# init-letsencrypt.sh
# This script initializes Let's Encrypt certificates for the domain

set -e

domains=(garden.timosur.com)
rsa_key_size=4096
data_path="./certbot"
email="garden@timosur.com"
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

# For automated deployments, don't prompt for confirmation
if [ -d "$data_path" ] && [ -z "$CI" ]; then
  read -p "Existing data found for $domains. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
elif [ -d "$data_path" ]; then
  echo "Running in CI environment. Proceeding with certificate initialization..."
fi

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

echo "### Creating certbot webroot directory ..."
mkdir -p "$data_path/www/.well-known/acme-challenge"
echo

echo "### Creating dummy certificate for $domains ..."
path="/etc/letsencrypt/live/$domains"
mkdir -p "$data_path/conf/live/$domains"
docker-compose -f docker-compose.yml -f docker-compose.yml run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" certbot
echo

echo "### Starting nginx ..."
# Build and start nginx
docker-compose -f docker-compose.yml -f docker-compose.yml up --force-recreate -d nginx
echo

echo "### Testing webroot accessibility ..."
# Create a test file to verify the webroot is accessible
test_content="test-$(date +%s)"
echo "$test_content" > "$data_path/www/.well-known/acme-challenge/test"
sleep 5

# Test if the file is accessible via HTTP and check the content
echo "Testing: http://garden.timosur.com/.well-known/acme-challenge/test"
response=$(curl -f "http://garden.timosur.com/.well-known/acme-challenge/test" 2>/dev/null || echo "CURL_FAILED")

if [ "$response" = "$test_content" ]; then
  echo "✓ Webroot is accessible and serving correct content"
  rm "$data_path/www/.well-known/acme-challenge/test"
else
  echo "✗ Webroot is not serving the correct content. Debug information:"
  echo "Expected: '$test_content'"
  echo "Got: '$response'"
  echo ""
  echo "1. Check if nginx is running:"
  docker-compose ps nginx
  echo ""
  echo "2. Check nginx logs:"
  docker-compose logs --tail=20 nginx
  echo ""
  echo "3. Check if the test file exists on host:"
  ls -la "$data_path/www/.well-known/acme-challenge/"
  echo ""
  echo "4. Check if the test file exists inside nginx container:"
  docker-compose exec nginx ls -la /var/www/certbot/.well-known/acme-challenge/ || echo "Directory not found in container"
  echo ""
  echo "5. Test local nginx access:"
  docker-compose exec nginx curl -f "http://localhost/.well-known/acme-challenge/test" || echo "Local test failed"
  echo ""
  echo "6. Check nginx configuration:"
  docker-compose exec nginx nginx -T | grep -A 5 -B 5 "\.well-known"
  
  rm -f "$data_path/www/.well-known/acme-challenge/test"
  echo "Fix the above issues before proceeding."
  exit 1
fi
echo

echo "### Deleting dummy certificate for $domains ..."
docker-compose -f docker-compose.yml -f docker-compose.yml run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf" certbot
echo

echo "### Requesting Let's Encrypt certificate for $domains ..."
# Join $domains to -d args
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker-compose -f docker-compose.yml -f docker-compose.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --non-interactive \
    --force-renewal" certbot
echo

echo "### Reloading nginx ..."
docker-compose -f docker-compose.yml -f docker-compose.yml exec nginx nginx -s reload

echo "### SSL certificates successfully initialized!"
echo "Your site should now be available at https://garden.timosur.com"

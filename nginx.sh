#!/bin/bash

# Vérification des prérequis
if ! command -v nginx &> /dev/null; then
    echo "Nginx n'est pas installé. Installation en cours..."
    sudo apt install nginx -y
fi

# Installation de Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Configuration de base Nginx (à adapter selon votre configuration)
# cat <<EOF | sudo tee /etc/nginx/sites-available/votre-site-ip
# server {
#     listen 80;
#     server_name [IP_PUBlique];

#     location / {
#         return 301 https://\$host\$request_uri;
#     }
# }
# EOF

# Activation du site
# sudo ln -s /etc/nginx/sites-available/votre-site-ip /etc/nginx/sites-enabled/
# sudo nginx -t
# sudo systemctl restart nginx

# Obtention du certificat (remplacer [IP_PUBlique] par l'IP publique du serveur)
sudo certbot --nginx -d [IP_PUBlique] --non-interactive --agree-tos --email votre-email@example.com

# Vérification du renouvellement
sudo certbot renew --dry-run

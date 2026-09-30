#!/bin/bash
set -e

# ==============================================================================
# Script d'installation et de déploiement en production
# OS cible : Ubuntu 22.04/24.04 LTS ou Debian 12
# ==============================================================================

PROJECT_DIR="/var/www/chatbot"
DOMAIN="${1:-}"

if [ -z "$DOMAIN" ]; then
    echo "Usage: sudo ./deploy/setup.sh <votre-domaine.com>"
    exit 1
fi

echo "=== 1. Mise à jour système et installation des paquets ==="
apt update
apt install -y curl git nginx certbot python3-certbot-nginx build-essential

# Installation de Node.js (v20 LTS) si absent
if ! command -v node &> /dev/null; then
    echo "Installation de Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# Installation de 'uv' pour l'environnement Python
if ! command -v uv &> /dev/null; then
    echo "Installation de uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Installation d'Ollama si absent
if ! command -v ollama &> /dev/null; then
    echo "Installation d'Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "=== 2. Téléchargement du modèle par défaut pour Ollama ==="
systemctl enable --now ollama || true
ollama pull granite4:7b-a1b-h || ollama pull mistral || true

echo "=== 3. Configuration des répertoires et permissions ==="
mkdir -p /var/log/chatbot
chown -R www-data:www-data /var/log/chatbot

cd "$PROJECT_DIR"

echo "=== 4. Installation des dépendances Backend (Python uv) ==="
uv sync --frozen || uv sync

echo "=== 5. Compilation du Frontend (Vite) ==="
npm ci || npm install
npm run build

chown -R www-data:www-data "$PROJECT_DIR"

echo "=== 6. Configuration Nginx ==="
sed "s/votre-domaine.com/$DOMAIN/g" "$PROJECT_DIR/deploy/nginx/chatbot.conf" > "/etc/nginx/sites-available/$DOMAIN"
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
rm -f /etc/nginx/sites-enabled/default || true

nginx -t
systemctl reload nginx

echo "=== 7. Configuration et Démarrage du Service Backend ==="
cp "$PROJECT_DIR/deploy/systemd/chatbot-backend.service" /etc/systemd/system/chatbot-backend.service
systemctl daemon-reload
systemctl enable --now chatbot-backend

echo "=== 8. Génération du Certificat SSL HTTPS ==="
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email || true

systemctl restart chatbot-backend
systemctl reload nginx

echo "=========================================================="
echo " Déploiement terminé avec succès !"
echo " Application accessible sur : https://$DOMAIN"
echo "=========================================================="

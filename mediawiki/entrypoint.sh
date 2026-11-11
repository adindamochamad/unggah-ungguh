#!/bin/bash
set -euo pipefail

MW_DIR=/var/www/html
cd "$MW_DIR"

MW_DB_HOST="${MW_DB_HOST:-db}"
MW_DB_NAME="${MW_DB_NAME:-mediawiki}"
MW_DB_USER="${MW_DB_USER:-wiki}"
MW_DB_PASS="${MW_DB_PASS:-wikipass}"
MW_SERVER="${MW_SERVER:-http://localhost:8080}"
MW_ADMIN_USER="${MW_ADMIN_USER:-Admin}"
MW_ADMIN_PASS="${MW_ADMIN_PASS:-Adminpass1!}"
MW_SITENAME="${MW_SITENAME:-Unggah-Ungguh Spike}"
MW_BOT_USER="${MW_BOT_USER:-uu-bot}"
MW_BOT_PASS="${MW_BOT_PASS:-UuBotPass1!}"

mkdir -p /persist

echo ">> waiting for mysql at ${MW_DB_HOST}"
php -r '
$host = getenv("MW_DB_HOST") ?: "db";
$user = getenv("MW_DB_USER") ?: "wiki";
$pass = getenv("MW_DB_PASS") ?: "wikipass";
for ($i = 0; $i < 90; $i++) {
  $m = @mysqli_connect($host, $user, $pass);
  if ($m) { fwrite(STDERR, ">> mysql is up\n"); exit(0); }
  sleep(2);
}
fwrite(STDERR, "!! mysql did not become ready\n");
exit(1);
'

if [ -f /persist/LocalSettings.php ] && [ ! -f "$MW_DIR/LocalSettings.php" ]; then
  echo ">> restoring LocalSettings.php from persist"
  cp /persist/LocalSettings.php "$MW_DIR/LocalSettings.php"
fi

ensure_append() {
  if [ -f "$MW_DIR/LocalSettings.php" ] && ! grep -q 'LocalSettings.append.php' "$MW_DIR/LocalSettings.php"; then
    echo 'require_once "$IP/LocalSettings.append.php";' >> "$MW_DIR/LocalSettings.php"
  fi
}

if [ ! -f "$MW_DIR/LocalSettings.php" ]; then
  echo ">> running MediaWiki installer"
  php maintenance/install.php \
    --dbserver="$MW_DB_HOST" \
    --dbtype=mysql \
    --dbname="$MW_DB_NAME" \
    --dbuser="$MW_DB_USER" \
    --dbpass="$MW_DB_PASS" \
    --server="$MW_SERVER" \
    --scriptpath="" \
    --lang=en \
    --pass="$MW_ADMIN_PASS" \
    "$MW_SITENAME" \
    "$MW_ADMIN_USER"
  ensure_append
  cp "$MW_DIR/LocalSettings.php" /persist/LocalSettings.php
else
  ensure_append
  cp "$MW_DIR/LocalSettings.php" /persist/LocalSettings.php
fi

echo ">> maintenance/update.php (includes SMW tables)"
php maintenance/update.php --quick

echo ">> ensuring bot user ${MW_BOT_USER}"
php maintenance/createAndPromote.php --force --bot "$MW_BOT_USER" "$MW_BOT_PASS"

chown -R www-data:www-data "$MW_DIR/images" || true
chown www-data:www-data "$MW_DIR/LocalSettings.php" || true

echo ">> starting apache"
exec apache2-foreground

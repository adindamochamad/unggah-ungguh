FROM mediawiki:1.35

# docker.io/library/mediawiki:1.35 currently ships 1.35.13; there is no 1.35.14
# image tag. Overlay the 1.35.14 tarball so Special:Version matches the pin.
# This is not an upgrade off the 1.35 line.
RUN curl -fsSL https://releases.wikimedia.org/mediawiki/1.35/mediawiki-1.35.14.tar.gz \
        -o /tmp/mw.tar.gz \
    && tar -xzf /tmp/mw.tar.gz -C /tmp \
    && cp -a /tmp/mediawiki-1.35.14/. /var/www/html/ \
    && rm -rf /tmp/mw.tar.gz /tmp/mediawiki-1.35.14 \
    && grep -q "1.35.14" /var/www/html/includes/Defines.php

# unzip is required by Composer; git and curl already exist in this image.
# Debian 11 security mirrors 404 for the versions this image pins, so use the archive.
RUN printf '%s\n' \
        'deb http://archive.debian.org/debian bullseye main' \
        'deb http://archive.debian.org/debian-security bullseye-security main' \
        > /etc/apt/sources.list \
    && printf '%s\n' 'Acquire::Check-Valid-Until "false";' \
        > /etc/apt/apt.conf.d/99archive \
    && apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2.2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

COPY composer.local.json /var/www/html/composer.local.json

ENV COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_MEMORY_LIMIT=-1

# Pin is mediawiki/semantic-media-wiki:3.2.3 — do not loosen it.
RUN composer config --no-plugins allow-plugins.composer/installers true \
    && composer config --no-plugins allow-plugins.wikimedia/composer-merge-plugin true \
    && composer config process-timeout 600 \
    && composer update --no-dev --no-interaction --prefer-dist

COPY LocalSettings.append.php /var/www/html/LocalSettings.append.php
COPY entrypoint.sh /entrypoint.sh
COPY seed /seed

RUN chmod +x /entrypoint.sh \
    && chown -R www-data:www-data /var/www/html

ENTRYPOINT ["/entrypoint.sh"]

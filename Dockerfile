FROM 1and1internet/ubuntu-16:latest
MAINTAINER james.wilkins@1and1.co.uk
ARG DEBIAN_FRONTEND=noninteractive
ARG RPAF_VERSION=tags/v0.8.4
COPY files /
ENV SSL_KEY=/ssl/ssl.key \
    SSL_CERT=/ssl/ssl.crt \
    DOCUMENT_ROOT=html
RUN \
  apt-get update && apt-get install -o Dpkg::Options::=--force-confdef -y apache2 cronolog build-essential git apache2-dev && \
  mkdir /tmp/mod_rpaf && \
  git clone https://github.com/gnif/mod_rpaf.git /tmp/mod_rpaf && \
  update-alternatives --install /bin/sh sh /bin/bash 100 && \
  cd /tmp/mod_rpaf && \
  git checkout $RPAF_VERSION && \
  ls -la && \
  make && \
  make install && \
  sed -i -e 's/Listen 80/Listen 8080/g' /etc/apache2/ports.conf && \
  mkdir -p /var/lock/apache2 && mkdir -p /var/run/apache2 && \
  chmod -R 777 /var/log/apache2 /var/lock/apache2 /var/run/apache2 /var/www && \
  echo "SSLProtocol ALL -SSLv2 -SSLv3" >> /etc/apache2/apache2.conf && \
  sed -i -e 's/Listen 443/#Listen 8443/g' /etc/apache2/ports.conf && \
  chmod -R 755 /hooks /init && \
  chmod 666 /etc/apache2/ports.conf && \
  chmod -R 755 /etc/apache2/sites-available && \
  chmod -R 777 /etc/apache2/sites-enabled && \
  a2enmod rewrite ssl headers macro rpaf cgi expires && \
  a2disconf other-vhosts-access-log && \
  a2enconf vhosts-logging && \
  apt autoremove build-essential apache2-dev git -y && \
  rm /tmp/mod_rpaf -rf && \
  rm -rf /var/lib/apt/lists/*

EXPOSE 8080 8443

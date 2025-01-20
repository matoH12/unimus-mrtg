# Použitie najnovšieho stabilného obrazu Ubuntu
FROM ubuntu:22.04

# Nastavenie environmentálnych premenných
ENV DEBIAN_FRONTEND=noninteractive

# Inštalácia potrebných balíkov
RUN apt-get update && apt-get install -y \
    mrtg \
    apache2 \
    snmp \
    snmp-mibs-downloader \
    cron \
    python3 \
    python3-pip \
    psmisc \
    openssl \
    && apt-get clean

# Nastavenie pracovného adresára
WORKDIR /app

# Kopírovanie požiadaviek a skriptu
COPY requirements.txt .
COPY app.py .

# Inštalácia Python závislostí
RUN pip3 install --no-cache-dir -r requirements.txt

# Nastavenie Apache servera
RUN mkdir -p /var/www/html && \
    chown -R www-data:www-data /var/www/html && \
    a2enmod cgi

# Nastavenie cron jobu
#RUN echo "*/5 * * * * . /etc/environment; /usr/bin/python3 /app/app.py >> /var/log/mrtg_update.log 2>&1" > /etc/cron.d/mrtg_update && \
#    echo "*/5 * * * * env LANG=C /usr/bin/mrtg /etc/mrtg/mrtg.cfg >> /var/log/mrtg.log 2>&1" >> /etc/cron.d/mrtg_jobs && \
#    chmod 0644 /etc/cron.d/mrtg_update && \
#    touch /var/log/mrtg_update.log && \
#    touch /var/log/mrtg.log && \
#    chmod 0644 /etc/cron.d/mrtg_jobs && \
#    crontab /etc/cron.d/mrtg_update && \
#    crontab /etc/cron.d/mrtg_jobs
# Príprava log súborov
RUN mkdir -p /var/log && \
    touch /var/log/mrtg_update.log /var/log/mrtg.log && \
    chmod 0644 /var/log/mrtg_update.log /var/log/mrtg.log

# Nastavenie cron jobov
RUN echo "SHELL=/bin/bash" > /etc/cron.d/mrtg_jobs && \
    echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/cron.d/mrtg_jobs && \
    echo "*/5 * * * * . /etc/environment; /usr/bin/python3 /app/app.py >> /var/log/mrtg_update.log 2>&1" >> /etc/cron.d/mrtg_jobs && \
    echo "*/5 * * * * . /etc/environment; env LANG=C /usr/bin/mrtg /etc/mrtg/mrtg.cfg >> /var/log/mrtg.log 2>&1" >> /etc/cron.d/mrtg_jobs && \
    chmod 0644 /etc/cron.d/mrtg_jobs && \
    crontab /etc/cron.d/mrtg_jobs


RUN mkdir -p /etc/apache2/ssl && \
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/apache2/ssl/apache.key \
    -out /etc/apache2/ssl/apache.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"


RUN a2enmod ssl && \
    echo '<IfModule mod_ssl.c>\n\
<VirtualHost *:443>\n\
    SSLEngine on\n\
    SSLCertificateFile /etc/apache2/ssl/apache.crt\n\
    SSLCertificateKeyFile /etc/apache2/ssl/apache.key\n\
    DocumentRoot /var/www/html\n\
</VirtualHost>\n\
</IfModule>' > /etc/apache2/sites-available/default-ssl.conf && \
    a2ensite default-ssl

# Nastavenie ServerName pre Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf


# Export environmentálnych premenných do súboru
RUN printenv | grep -v "no_proxy" >> /etc/environment


EXPOSE 80 443



# Spustenie cron a Apache servera
#CMD ["/bin/bash", "-c", "service apache2 start && cron && tail -f /var/log/mrtg_update.log"]
# Pridanie environmentálnych premenných pri štarte kontajnera
CMD ["/bin/bash", "-c", "printenv | grep -v 'no_proxy' >> /etc/environment && service apache2 start && cron && tail -f /var/log/mrtg_update.log"]

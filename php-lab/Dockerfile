FROM php:8.2-apache

WORKDIR /var/www/html

# Copy application files into the Apache root
COPY index.php classes.php ./

# Pre-create the logs directory and assign permissions to www-data
RUN mkdir -p logs \
    && chown -R www-data:www-data logs \
    && chmod 775 logs

EXPOSE 80

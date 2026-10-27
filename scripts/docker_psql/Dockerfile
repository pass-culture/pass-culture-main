FROM postgis/postgis:18-3.6-alpine

COPY init-multiple-dbs.sh /docker-entrypoint-initdb.d/init-multiple-dbs.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-multiple-dbs.sh

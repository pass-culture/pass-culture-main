FROM postgis/postgis:15-3.4-alpine

# Install build deps and TimescaleDB
RUN apk add --no-cache \
      curl \
      ca-certificates \
      gnupg \
      build-base \
      cmake \
      git \
      postgresql15-dev

RUN git clone https://github.com/timescale/timescaledb
RUN cd timescaledb && git checkout 2.17.2 && ./bootstrap && cd build && make .. && make && make install

# Install TimescaleDB (from source or package)
# RUN apk add --no-cache timescaledb-2.17.0

# Update shared_preload_libraries
RUN echo "shared_preload_libraries = 'timescaledb,postgis-3'" >> /usr/local/share/postgresql/postgresql.conf.sample

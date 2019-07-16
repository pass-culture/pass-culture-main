FROM node:8.15.1-alpine

RUN npm install --unsafe-perm=true -g artillery -allow-root && npm install artillery-plugin-statsd
RUN apk update && apk add git && apk add openssh

RUN mkdir /usr/local/lib/node_modules/artillery/node_modules/artillery-plugin-metrics-by-endpoint

COPY files/artillery-plugin-metrics-by-endpoint/index.js /usr/local/lib/node_modules/artillery/node_modules/artillery-plugin-metrics-by-endpoint/index.js
FROM node:8-alpine

RUN npm install -g artillery@1.6.0-2 && npm install artillery-plugin-statsd
RUN apk update && apk add git && apk add openssh

RUN mkdir /usr/local/lib/node_modules/artillery/node_modules/artillery-plugin-metrics-by-endpoint

COPY files/artillery-plugin-metrics-by-endpoint/index.js /usr/local/lib/node_modules/artillery/node_modules/artillery-plugin-metrics-by-endpoint/index.js
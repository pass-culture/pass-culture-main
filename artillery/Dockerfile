FROM node:8.15.1-alpine

RUN apk update && apk add git && apk add openssh
RUN yarn global add artillery -r -o -o -t && yarn global add artillery-plugin-statsd

RUN mkdir /usr/local/share/.config/yarn/global/node_modules/artillery-plugin-metrics-by-endpoint

COPY files/artillery-plugin-metrics-by-endpoint/index.js  /usr/local/share/.config/yarn/global/node_modules/artillery-plugin-metrics-by-endpoint/index.js
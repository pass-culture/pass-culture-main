FROM node:8.15.1-alpine

RUN apk update && apk add git && apk add openssh && apk add python3 && apk add py3-pip
RUN pip3 install requests simplejson
RUN yarn global add artillery -r -o -o -t && yarn global add artillery-plugin-metrics-by-endpoint
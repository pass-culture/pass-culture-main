
FROM node:8-alpine

RUN npm install -g artillery@1.6.0-2
RUN apk update && apk add git

ENTRYPOINT ["artillery"]
CMD ["--help"]

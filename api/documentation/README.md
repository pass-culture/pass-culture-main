# The pass Culture Public API documentation

Here are the source files to generate the [pass Culture Public API Documentation](https://pass-culture.github.io/pass-culture-api-documentation/docs/category/mandatory-steps).

It is built with [Docusaurus](https://docusaurus.io/) and [Redoc](https://github.com/Redocly/redoc).

## Installation

You need to have a version of node >= 18.0.

```shell
npm install
```

## Local Development

### Prerequisite

To be able to start the development server, you need to have the pass Culture local backend server running, as Redoc will be using the Open API JSON served by spectree on http://localhost/openapi.json to generate the REST API documentation.

### Command

```shell
npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Deployment

**⚠️ This is a temporary section. Soon the deployment will be done automatically using GitHub actions.**

### Prerequisite

To be able to deploy, you need to have write access to the [pass-culture-api-documentation repo](https://github.com/pass-culture/pass-culture-api-documentation).

### Command
```shell
ENV=deploy npm run deploy
```

This command will build the static files locally and they pushes on the `gh-pages` branch on the [pass-culture-api-documentation repo](https://github.com/pass-culture/pass-culture-api-documentation).
This will update the [GitHub pages](https://pass-culture.github.io/pass-culture-api-documentation/docs/category/mandatory-steps) linked to this repo (⚠️ be aware of the fact that GitHub is caching GitHub Pages so it might take some time for changes to appear).

# The pass Culture Public API documentation

Here are the source files to generate the [pass Culture Public API Documentation](https://developers.passculture.pro/).

It is built with :
- [Docusaurus](https://docusaurus.io/): generate static documentation from markdown files
- [Redoc](https://github.com/Redocly/redoc): display an Open API JSON in a nice format. It is plugged to docusaurus thanks to [this plugin](https://github.com/rohit-gohri/redocusaurus).
- [spectree](https://github.com/0b01001001/spectree): generate Open API JSON based on the python code


## URLs

- Testing: https://developers.testing.passculture.team/
- Staging: https://developers.staging.passculture.team/
- Production: https://developers.passculture.pro/

## Installation

You need to have a version of node >= 18.0.

```shell
npm install
```

## Local Development

### Prerequisite

To be able to start the development server, you need to have the pass Culture local backend server running, as Redoc will be using the Open API JSON served by spectree on http://localhost:5001/openapi.json to generate the REST API documentation.

### Command

```shell
npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

### Good to know

- the REST API documentation is built with spectree, so you'll need to update the python code to bring updates to the Redoc part of the documentation. The python code for the public API is [here](/api/src/pcapi/routes/public) and the folder holding the documentation constants is [here](/api/src/pcapi/routes/public/documentation_constants).
- we have [a test](/api/tests/routes/public/blueprint_openapi_test.py) to ensure that we don't bring unwanted modification to the Open API JSON. This test compares the Open API JSON exposed by the backend to [the JSON used by docusaurus to build the REST API documentation](/api/documentation/static/openapi.json). It raises an error if there is a difference. If you bring modifications to the API, you will need to update the Open API JSON; for that, we have a command to automatically generate the JSON:
  - if you are using docker: `pc generate_public_api_openapi_json`
  - if you running the flask application locally: `flask generate_public_api_openapi_json` (in the flask app root folder)

> **Side note:** We are using a static file instead of the JSON exposed by our backend because we want to document endpoints that are not present in production (the Adage Mock endpoints, only available in integration).
> If we were using the json exposed by the production backend, those endpoints would not appear in the documentation.

## Deployment

Deployment is done automatically through [this workflow](/.github/workflows/dev_on_workflow_deploy.yml) (job: `deploy-api-doc-on-firebase`).

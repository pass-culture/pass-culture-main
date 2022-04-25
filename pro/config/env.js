'use strict'

const fs = require('fs')
const path = require('path')

const { name, version } = require('../package.json')

const paths = require('./paths')

// Make sure that including paths.js after env.js will read .env variables.
delete require.cache[require.resolve('./paths')]

const NODE_ENV = process.env.NODE_ENV
if (!NODE_ENV) {
  throw new Error(
    'The NODE_ENV environment variable is required but was not specified.'
  )
}

// https://github.com/bkeepers/dotenv#what-other-env-files-can-i-use
const dotenvFiles = [
  `${paths.dotenv}.${NODE_ENV}.local`,
  // Don't include `.env.local` for `test` environment
  // since normally you expect tests to produce the same
  // results for everyone
  NODE_ENV !== 'test' && `${paths.dotenv}.local`,
  `${paths.dotenv}.${NODE_ENV}`,
  paths.dotenv,
].filter(Boolean)

// Load environment variables from .env* files. Suppress warnings using silent
// if this file is missing. dotenv will never modify any environment variables
// that have already been set.  Variable expansion is supported in .env files.
// https://github.com/motdotla/dotenv
// https://github.com/motdotla/dotenv-expand
dotenvFiles.forEach(dotenvFile => {
  if (fs.existsSync(dotenvFile)) {
    require('dotenv-expand').expand(
      require('dotenv').config({
        path: dotenvFile,
      })
    );
  }
})

// We support resolving modules according to `NODE_PATH`.
// This lets you use absolute paths in imports inside large monorepos:
// https://github.com/facebook/create-react-app/issues/253.
// It works similar to `NODE_PATH` in Node itself:
// https://nodejs.org/api/modules.html#modules_loading_from_the_global_folders
// Note that unlike in Node, only *relative* paths from `NODE_PATH` are honored.
// Otherwise, we risk importing Node.js core modules into an app instead of webpack shims.
// https://github.com/facebook/create-react-app/issues/1023#issuecomment-265344421
// We also resolve them to make sure all tools using them work consistently.
const appDirectory = fs.realpathSync(process.cwd())
process.env.NODE_PATH = (process.env.NODE_PATH || '')
  .split(path.delimiter)
  .filter(folder => folder && !path.isAbsolute(folder))
  .map(folder => path.resolve(appDirectory, folder))
  .join(path.delimiter)

// Grab NODE_ENV and REACT_APP_* environment variables and prepare them to be
// injected into the application via DefinePlugin in webpack configuration.
const REACT_APP = /^REACT_APP_/i

function getClientEnvironment(publicUrl) {
  const raw = Object.keys(process.env)
    .filter(key => REACT_APP.test(key))
    .reduce(
      (env, key) => {
        env[key] = process.env[key]
        return env
      },
      {
        API_URL_OLD: process.env.API_URL_OLD,
        API_URL_NEW: process.env.API_URL_NEW,
        WEBAPP_URL: process.env.WEBAPP_URL,
        ENVIRONMENT_NAME: process.env.ENVIRONMENT_NAME,
        ENV_WORDING: process.env.ENV_WORDING,
        NAME: name,
        VERSION: version,
        SENTRY_SAMPLE_RATE: process.env.SENTRY_SAMPLE_RATE,
        SENTRY_SERVER_URL: process.env.SENTRY_SERVER_URL,
        URL_FOR_MAINTENANCE: process.env.URL_FOR_MAINTENANCE,
        MAINTENANCE_PAGE_AVAILABLE:
          process.env.MAINTENANCE_PAGE_AVAILABLE === 'true',
        DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL:
          process.env.DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL,
        DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
          process.env.DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL,
        DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL:
          process.env
            .DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL,
        ASSETS_URL: process.env.ASSETS_URL,
        NODE_ENV: process.env.NODE_ENV || 'development',
        PUBLIC_URL: publicUrl,
        WDS_SOCKET_HOST: process.env.WDS_SOCKET_HOST,
        WDS_SOCKET_PATH: process.env.WDS_SOCKET_PATH,
        WDS_SOCKET_PORT: process.env.WDS_SOCKET_PORT,
        FAST_REFRESH: process.env.FAST_REFRESH !== 'false',
        RECAPTCHA_SITE_KEY: process.env.RECAPTCHA_SITE_KEY,
        FIRBASE_API_KEY: process.env.FIRBASE_API_KEY,
        FIREBASE_AUTH_DOMAIN: process.env.FIREBASE_AUTH_DOMAIN,
        FIREBASE_PROJECT_ID: process.env.FIREBASE_PROJECT_ID,
        FIREBASE_STORAGE_BUCKET: process.env.FIREBASE_STORAGE_BUCKET,
        FIREBASE_MESSAGING_SENDER_ID: process.env.FIREBASE_MESSAGING_SENDER_ID,
        FIREBASE_APP_ID: process.env.FIREBASE_APP_ID,
        FIREBASE_MEASUREMENT_ID: process.env.FIREBASE_MEASUREMENT_ID,
      }
    )
  // Stringify all values so we can feed into webpack DefinePlugin
  const stringified = {
    'process.env': Object.keys(raw).reduce((env, key) => {
      env[key] = JSON.stringify(raw[key])
      return env
    }, {}),
  }

  return { raw, stringified }
}

module.exports = getClientEnvironment

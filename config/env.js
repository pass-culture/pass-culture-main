const fs = require('fs')
const path = require('path')
const paths = require('./paths')

delete require.cache[require.resolve('./paths')]

const { NODE_ENV } = process.env
if (!NODE_ENV) {
  throw new Error('The NODE_ENV environment variable is required but was not specified.')
}

const dotenvFiles = [
  `${paths.dotenv}.${NODE_ENV}.local`,
  `${paths.dotenv}.${NODE_ENV}`,
  NODE_ENV !== 'test' && `${paths.dotenv}.local`,
  paths.dotenv,
].filter(Boolean)

dotenvFiles.forEach(dotenvFile => {
  if (fs.existsSync(dotenvFile)) {
    require('dotenv').config({
      path: dotenvFile,
    })
  }
})

const appDirectory = fs.realpathSync(process.cwd())
process.env.NODE_PATH = (process.env.NODE_PATH || '')
  .split(path.delimiter)
  .filter(folder => folder && !path.isAbsolute(folder))
  .map(folder => path.resolve(appDirectory, folder))
  .join(path.delimiter)

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
        API_URL: process.env.API_URL || 'http://localhost',
        ENVIRONMENT_NAME: process.env.ENVIRONMENT_NAME,
        HAS_WORKERS: process.env.HAS_WORKERS || false,
        MATOMO_SERVER_URL: process.env.MATOMO_SERVER_URL,
        MAINTENANCE_PAGE_AVAILABLE: process.env.MAINTENANCE_PAGE_AVAILABLE === 'true' || false,
        NODE_ENV: process.env.NODE_ENV || 'development',
        PUBLIC_URL: publicUrl,
        SENTRY_SERVER_URL_FOR_WEBAPP: process.env.SENTRY_SERVER_URL_FOR_WEBAPP,
        TYPEFORM_URL_CULTURAL_PRACTICES_POLL:
          process.env.TYPEFORM_URL_CULTURAL_PRACTICES_POLL ||
          'https://passculture.typeform.com/to/T8rurj',
        URL_FOR_MAINTENANCE: process.env.WEBAPP_URL_FOR_MAINTENANCE,
        WEBAPP_ALGOLIA_APPLICATION_ID: process.env.WEBAPP_ALGOLIA_APPLICATION_ID,
        WEBAPP_ALGOLIA_SEARCH_API_KEY: process.env.WEBAPP_ALGOLIA_SEARCH_API_KEY,
        WEBAPP_ALGOLIA_INDEX_NAME: process.env.WEBAPP_ALGOLIA_INDEX_NAME,
      }
    )
  // Stringify all values so we can feed into Webpack DefinePlugin
  const stringified = {
    'process.env': Object.keys(raw).reduce((env, key) => {
      env[key] = JSON.stringify(raw[key])
      return env
    }, {}),
  }

  return { raw, stringified }
}

module.exports = getClientEnvironment

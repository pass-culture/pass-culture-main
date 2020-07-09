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
        ALGOLIA_APPLICATION_ID: process.env.ALGOLIA_APPLICATION_ID,
        ALGOLIA_INDEX_NAME: process.env.ALGOLIA_INDEX_NAME,
        ALGOLIA_SEARCH_API_KEY: process.env.ALGOLIA_SEARCH_API_KEY,
        API_URL: process.env.API_URL,
        CONTENTFUL_ACCESS_TOKEN: process.env.CONTENTFUL_ACCESS_TOKEN,
        CONTENTFUL_ENVIRONMENT: process.env.CONTENTFUL_ENVIRONMENT,
        CONTENTFUL_SPACE_ID: process.env.CONTENTFUL_SPACE_ID,
        ENVIRONMENT_NAME: process.env.ENVIRONMENT_NAME,
        ID_CHECK_URL: process.env.ID_CHECK_URL,
        HAS_WORKERS: process.env.HAS_WORKERS === 'true',
        MAILJET_NOT_YET_ELIGIBLE_LIST_ID: process.env.MAILJET_NOT_YET_ELIGIBLE_LIST_ID,
        MAILJET_PRIVATE_API_KEY: process.env.MAILJET_PRIVATE_API_KEY,
        MAILJET_PUBLIC_API_KEY: process.env.MAILJET_PUBLIC_API_KEY,
        MATOMO_SERVER_URL: process.env.MATOMO_SERVER_URL,
        MATOMO_GEOLOCATION_GOAL_ID: process.env.MATOMO_GEOLOCATION_GOAL_ID,
        MAINTENANCE_PAGE_AVAILABLE: process.env.MAINTENANCE_PAGE_AVAILABLE === 'true',
        NODE_ENV: process.env.NODE_ENV,
        PUBLIC_URL: publicUrl,
        RECAPTCHA_SITE_KEY: process.env.RECAPTCHA_SITE_KEY,
        SENTRY_SERVER_URL: process.env.SENTRY_SERVER_URL,
        TYPEFORM_URL_CULTURAL_PRACTICES_POLL: process.env.TYPEFORM_URL_CULTURAL_PRACTICES_POLL,
        URL_FOR_MAINTENANCE: process.env.URL_FOR_MAINTENANCE,
        ANDROID_APPLICATION_ID: process.env.ANDROID_APPLICATION_ID,
        IS_DEBUG_PAGE_ACTIVE: process.env.IS_DEBUG_PAGE_ACTIVE === 'true',
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

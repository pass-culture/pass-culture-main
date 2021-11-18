const fs = require('fs')
const path = require('path')
const paths = require('./paths')
const { name, version } = require('../package.json')

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
        API_URL_OLD: process.env.API_URL_OLD,
        API_URL_NEW: process.env.API_URL_NEW,
        APP_NATIVE_DYNAMIC_LINK: process.env.APP_NATIVE_DYNAMIC_LINK,
        ANDROID_APP_ID: process.env.ANDROID_APP_ID,
        ANDROID_APPLICATION_ID: process.env.ANDROID_APPLICATION_ID,
        APP_SEARCH_ENDPOINT: process.env.APP_SEARCH_ENDPOINT,
        APP_SEARCH_KEY: process.env.APP_SEARCH_KEY,
        BATCH_API_KEY: process.env.BATCH_API_KEY,
        BATCH_IS_ENABLED: process.env.BATCH_IS_ENABLED,
        BATCH_AUTH_KEY: process.env.BATCH_AUTH_KEY,
        BATCH_SUBDOMAIN: process.env.BATCH_SUBDOMAIN,
        BATCH_VAPID_PUBLIC_KEY: process.env.BATCH_VAPID_PUBLIC_KEY,
        CONTENTFUL_ACCESS_TOKEN: process.env.CONTENTFUL_ACCESS_TOKEN,
        CONTENTFUL_ENVIRONMENT: process.env.CONTENTFUL_ENVIRONMENT,
        CONTENTFUL_PREVIEW_TOKEN: process.env.CONTENTFUL_PREVIEW_TOKEN,
        CONTENTFUL_SPACE_ID: process.env.CONTENTFUL_SPACE_ID,
        ENVIRONMENT_NAME: process.env.ENVIRONMENT_NAME,
        FALLBACK_STORE_EMAIL_URL: process.env.FALLBACK_STORE_EMAIL_URL,
        FIREBASE_APP_ID: process.env.FIREBASE_APP_ID,
        FIREBASE_MEASUREMENT_ID: process.env.FIREBASE_MEASUREMENT_ID,
        ID_CHECK_URL: process.env.ID_CHECK_URL,
        IOS_APP_ID: process.env.IOS_APP_ID,
        IOS_APP_STORE_ID: process.env.IOS_APP_STORE_ID,
        IS_DEBUG_PAGE_ACTIVE: process.env.IS_DEBUG_PAGE_ACTIVE === 'true',
        HAS_WORKERS: process.env.HAS_WORKERS === 'true',
        MATOMO_SERVER_URL: process.env.MATOMO_SERVER_URL,
        MATOMO_GEOLOCATION_GOAL_ID: process.env.MATOMO_GEOLOCATION_GOAL_ID,
        MAINTENANCE_PAGE_AVAILABLE: process.env.MAINTENANCE_PAGE_AVAILABLE === 'true',
        NODE_ENV: process.env.NODE_ENV,
        OBJECT_STORAGE_URL: process.env.OBJECT_STORAGE_URL,
        PUBLIC_URL: publicUrl,
        RECAPTCHA_SITE_KEY: process.env.RECAPTCHA_SITE_KEY,
        RECOMMENDATION_ENDPOINT: process.env.RECOMMENDATION_ENDPOINT,
        RECOMMENDATION_TOKEN: process.env.RECOMMENDATION_TOKEN,
        SENTRY_SAMPLE_RATE: process.env.SENTRY_SAMPLE_RATE,
        SENTRY_SERVER_URL: process.env.SENTRY_SERVER_URL,
        TYPEFORM_URL_CULTURAL_PRACTICES_POLL: process.env.TYPEFORM_URL_CULTURAL_PRACTICES_POLL,
        UNIVERSAL_LINK: process.env.UNIVERSAL_LINK,
        URL_FOR_MAINTENANCE: process.env.URL_FOR_MAINTENANCE,
        WEBAPP_V2_URL: process.env.WEBAPP_V2_URL,
        NAME: name,
        VERSION: version,
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

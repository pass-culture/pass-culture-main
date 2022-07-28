declare namespace NodeJS {
  export interface ProcessEnv {
    REACT_APP_API_URL: string
    REACT_APP_ALGOLIA_APP_ID: string
    REACT_APP_ALGOLIA_API_KEY: string
    REACT_APP_ALGOLIA_COLLECTIVE_OFFERS_INDEX: string
    REACT_APP_ENVIRONMENT_NAME:
      | 'Local'
      | 'testing'
      | 'staging'
      | 'integration'
      | 'production'
    REACT_APP_URL_FOR_MAINTENANCE: string
    REACT_APP_SENTRY_SAMPLE_RATE: string
    REACT_APP_SENTRY_SERVER_URL: string
    REACT_APP_ASSETS_URL: string
    REACT_APP_ACTIVATE_MATOMO_TRACKING: string
    REACT_APP_MATOMO_SITE_ID: string
    REACT_APP_MATOMO_BASE_URL: string
  }
}

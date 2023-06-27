declare namespace NodeJS {
  export interface ProcessEnv {
    VITE_API_URL: string
    VITE_ALGOLIA_APP_ID: string
    VITE_ALGOLIA_API_KEY: string
    VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX: string
    VITE_ENVIRONMENT_NAME:
      | 'Local'
      | 'testing'
      | 'staging'
      | 'integration'
      | 'production'
    VITE_URL_FOR_MAINTENANCE: string
    VITE_SENTRY_SAMPLE_RATE: string
    VITE_SENTRY_SERVER_URL: string
    VITE_ASSETS_URL: string
    VITE_LOGS_DATA: string
  }
}

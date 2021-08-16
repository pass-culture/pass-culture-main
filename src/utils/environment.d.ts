declare namespace NodeJS {
  export interface ProcessEnv {
    REACT_APP_API_URL_OLD: string,
    REACT_APP_API_URL_NEW: string,
    ENVIRONMENT_NAME: 'Local' | 'testing' | 'staging' | 'integration' | 'production',
    URL_FOR_MAINTENANCE: string,
    SENTRY_SAMPLE_RATE: string,
    SENTRY_SERVER_URL: string,
  }
}

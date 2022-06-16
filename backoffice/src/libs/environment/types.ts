export interface Environment {
  NODE_ENV: 'development' | 'production' | 'test'
  ENV: 'testing' | 'staging' | 'integration' | 'production'
  OIDC_CLIENT_ID: string
  AUTH_ISSUER: string
  OIDC_REDIRECT_URI: string
  BASE_PATH: string
  URL_BASE: string
  SAMPLE_RATE: number
  SENTRY_DSN: string
  API_URL: string
}

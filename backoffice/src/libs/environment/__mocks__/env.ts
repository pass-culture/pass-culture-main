import { Environment } from '../types'

export const env: Environment = {
  NODE_ENV: 'development',
  ENV: 'testing',
  OIDC_CLIENT_ID: 'XYZ',
  AUTH_ISSUER: 'https://accounts.google.com/',
  OIDC_REDIRECT_URI: 'https://pc-backoffice-testing.web.app/',
  BASE_PATH: '/backoffice',
  URL_BASE: 'https://backend.testing.passculture.team',
  SAMPLE_RATE: 0.1,
  SENTRY_DSN: 'https://sentrydsn',
  API_URL: 'https://backend.testing.passculture.team/backoffice',
}

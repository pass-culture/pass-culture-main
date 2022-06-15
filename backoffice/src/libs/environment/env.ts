const URL_BASE = process.env.REACT_APP_URL_BASE || 'http://localhost'

export const env = {
  NODE_ENV: process.env.NODE_ENV,
  ENV: process.env.REACT_APP_ENV,
  URL_BASE,
  BASE_PATH: process.env.REACT_APP_BASE_PATH,
  AUTH_ISSUER: process.env.REACT_APP_AUTH_ISSUER,
  API_URL: `${URL_BASE}${process.env.REACT_APP_BASE_PATH}`,
  OIDC_CLIENT_ID: process.env.REACT_APP_OIDC_CLIENT_ID,
  REDIRECT_URI: process.env.REACT_APP_OIDC_REDIRECT_URI,
  SAMPLE_RATE: process.env.REACT_APP_SENTRY_SAMPLE_RATE || '1.O',
}

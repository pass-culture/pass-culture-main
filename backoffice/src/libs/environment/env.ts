import { parseEnvVariables } from './parser'

const URL_BASE = process.env.REACT_APP_URL_BASE || 'http://localhost'

const reactAppEnv = process.env as Record<string, string | boolean | number>

export const env = parseEnvVariables({
  NODE_ENV: reactAppEnv.NODE_ENV || 'development',
  ENV: reactAppEnv.REACT_APP_ENV,
  URL_BASE,
  BASE_PATH: reactAppEnv.REACT_APP_BASE_PATH,
  AUTH_ISSUER: reactAppEnv.REACT_APP_AUTH_ISSUER,
  API_URL: `${URL_BASE}${reactAppEnv.REACT_APP_BASE_PATH}`,
  OIDC_CLIENT_ID: reactAppEnv.REACT_APP_OIDC_CLIENT_ID,
  REDIRECT_URI: reactAppEnv.REACT_APP_OIDC_REDIRECT_URI,
  SAMPLE_RATE: reactAppEnv.REACT_APP_SENTRY_SAMPLE_RATE || '1.O',
  SENTRY_DSN: reactAppEnv.REACT_APP_SENTRY_DSN,
})

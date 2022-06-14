import { Environment } from '../types'

export const env: Environment = {
  NODE_ENV: 'development',
  REACT_APP_ENV: "testing",
  REACT_APP_OIDC_CLIENT_ID: 'XYZ',
  REACT_APP_AUTH_ISSUER: "https://accounts.google.com/",
  REACT_APP_OIDC_REDIRECT_URI: "http://pc-backoffice-testing.web.app/",
  REACT_APP_BASE_PATH: "/backoffice",
  REACT_APP_URL_BASE: "https://backend.testing.passculture.team",
}

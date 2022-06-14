export interface Environment {
  NODE_ENV: 'development' | 'production'
  REACT_APP_ENV: 'testing' | 'staging' | 'integration' | 'production'
  REACT_APP_OIDC_CLIENT_ID: string
  REACT_APP_AUTH_ISSUER: string
  REACT_APP_OIDC_REDIRECT_URI: string
  REACT_APP_BASE_PATH: string
  REACT_APP_URL_BASE: string
}

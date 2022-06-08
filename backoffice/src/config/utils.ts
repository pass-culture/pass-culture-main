export const NODE_ENV = process.env.NODE_ENV || 'development'
export const URL_BASE = process.env.REACT_APP_URL_BASE || 'http://localhost'
export const BASE_PATH = process.env.REACT_APP_BASE_PATH
export const AUTH_ISSUER = process.env.REACT_APP_AUTH_ISSUER
export const API_URL = `${URL_BASE}${BASE_PATH}`
export const OIDC_CLIENT_ID = process.env.REACT_APP_OIDC_CLIENT_ID
export const REDIRECT_URI = process.env.REACT_APP_OIDC_REDIRECT_URI


const NODE_ENV = process.env.NODE_ENV || "development"

export const IS_DEV = NODE_ENV === "development"
export const IS_PROD = !IS_DEV

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== "undefined") {
  apiUrlBasedOnDomain = window.location.hostname.includes("beta.gouv")
    ? process.env.REACT_APP_API_URL_OLD
    : process.env.REACT_APP_API_URL_NEW
}
export const REACT_APP_API_URL = apiUrlBasedOnDomain || "http://localhost/adage-iframe"

export const {
  REACT_APP_APP_SEARCH_ENDPOINT,
  REACT_APP_APP_SEARCH_KEY,
  REACT_APP_ENVIRONMENT_NAME,
  REACT_APP_URL_FOR_MAINTENANCE,
  REACT_APP_SENTRY_SAMPLE_RATE,
  REACT_APP_SENTRY_SERVER_URL,
} = process.env

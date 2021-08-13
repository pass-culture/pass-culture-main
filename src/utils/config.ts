

const NODE_ENV = process.env.NODE_ENV || "development"

export const IS_DEV = NODE_ENV === "development"
export const IS_PROD = !IS_DEV

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== "undefined") {
  apiUrlBasedOnDomain = window.location.hostname.includes("beta.gouv")
    ? process.env.API_URL_OLD
    : process.env.API_URL_NEW
}
export const API_URL = apiUrlBasedOnDomain || "http://localhost/adage-iframe"

export const {
  ENVIRONMENT_NAME,
  URL_FOR_MAINTENANCE,
  SENTRY_SAMPLE_RATE,
  SENTRY_SERVER_URL,
} = process.env

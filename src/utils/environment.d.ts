declare namespace NodeJS {
  export interface ProcessEnv {
    REACT_APP_API_URL: string;
    REACT_APP_ENVIRONMENT_NAME:
      | "Local"
      | "testing"
      | "staging"
      | "integration"
      | "production";
    REACT_APP_URL_FOR_MAINTENANCE: string;
    REACT_APP_SENTRY_SAMPLE_RATE: string;
    REACT_APP_SENTRY_SERVER_URL: string;
  }
}

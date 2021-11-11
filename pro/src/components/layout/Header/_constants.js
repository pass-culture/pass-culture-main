const ENV_NAME = process.env.ENVIRONMENT_NAME

export const STYLEGUIDE_ACTIVE = ENV_NAME !== 'production' && ENV_NAME !== 'staging'

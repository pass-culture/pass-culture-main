const ENV_NAME = process.env.ENVIRONMENT_NAME

export const HELP_PAGE_URL = 'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/'
export const STYLEGUIDE_ACTIVE = ENV_NAME !== 'production' && ENV_NAME !== 'staging'

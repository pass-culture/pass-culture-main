const { NODE_ENV } = process.env

export const IS_DEV = NODE_ENV === 'development'

export const NEW = '_new_'

export const API_URL = IS_DEV ? 'http://localhost'
                              : 'https://pc-api.btmx.fr'

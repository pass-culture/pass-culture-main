const { NODE_ENV } = process.env

export const NEW = '_new_'
export const API_URL = NODE_ENV === 'development'
  ? 'http://localhost'
  : 'https://pc-api.btmx.fr'

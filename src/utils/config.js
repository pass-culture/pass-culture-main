const { NODE_ENV } = process.env

export const NEW = '_new_'
export const URL = NODE_ENV === 'development'
  ? 'http://localhost'
  : 'http://pc-api.btmx.fr:8080'

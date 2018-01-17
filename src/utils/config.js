const { NODE_ENV } = process.env

export const URL = NODE_ENV === 'development'
  ? 'http://localhost'
  : 'http://pc-api.btmx.fr:8080'

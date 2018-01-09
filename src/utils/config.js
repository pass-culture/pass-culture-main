const { NODE_ENV } = process.env

export const URL = NODE_ENV === 'development'
  ? 'http://localhost:8080'
  : 'http://pass.culture.gouv.fr'

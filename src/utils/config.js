const { NODE_ENV } = process.env

export const URL = NODE_ENV === 'development'
  ? 'http://localhost:5000'
  : 'http://pass.culture.gouv.fr'

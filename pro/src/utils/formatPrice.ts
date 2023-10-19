import { NBSP } from 'core/shared'

export const formatPrice = (price: number) =>
  `${price.toString().replace('.', ',')}${NBSP}€`

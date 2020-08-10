import formatDecimals from '../numbers/formatDecimals'

const EURO_SIGN = `€`

export const formatResultPrice = (priceMin, priceMax, isDuo) => {
  if (priceMin === 0) {
    return 'Gratuit'
  }

  if (priceMin === priceMax && !isDuo) {
    return `${formatDecimals(priceMin)} ${EURO_SIGN}`
  }

  return `A partir de ${formatDecimals(priceMin)} ${EURO_SIGN}`
}

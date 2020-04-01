const EURO_SIGN = `€`

export const formatResultPrice = (priceMin, priceMax, isDuo) => {
  if (priceMin === 0) {
    return 'Gratuit'
  }

  if (priceMin === priceMax && !isDuo) {
    return `${priceMin} ${EURO_SIGN}`
  }

  return `A partir de ${priceMin} ${EURO_SIGN}`
}

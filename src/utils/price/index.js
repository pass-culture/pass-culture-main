const EURO_SIGN = `€`

export const formatResultPrice = (priceMin, priceMax) => {
  return priceMin === 0
    ? 'Gratuit'
    : priceMin === priceMax
      ? `${priceMin} ${EURO_SIGN}`
      : `A partir de ${priceMin} ${EURO_SIGN}`
}

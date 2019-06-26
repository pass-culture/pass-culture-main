const selectOffers = (onlineOnly, state) => {
  const { offers } = state.data || []
  return offers.filter(
    offer => offer.product.offerType.onlineOnly === onlineOnly
  )
}

export default selectOffers

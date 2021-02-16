export default (offerType, venue) => {
  if (offerType && venue && venue.isVirtual) {
    return (
      offerType.value === 'ThingType.LIVRE_EDITION' || offerType.value === 'ThingType.CINEMA_CARD'
    )
  }
  return true
}

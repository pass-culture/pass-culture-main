const offerIsNotRefundable = (selectedOfferType, venue) => {
  if (selectedOfferType && venue && venue.isVirtual) {
    const bookType = selectedOfferType.value == 'ThingType.LIVRE_EDITION'
    const cinemaCardType = selectedOfferType.value == 'ThingType.CINEMA_CARD'

    const onlineOnlyOffers = selectedOfferType.onlineOnly

    return !bookType && (!onlineOnlyOffers || !cinemaCardType)
  }
  return false
}

export default offerIsNotRefundable

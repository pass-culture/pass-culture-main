const displayDigitalOfferInformationMessage = (selectedOfferType, venue) => {
  if (selectedOfferType && venue && venue.isVirtual) {
    const bookType = selectedOfferType.value == 'ThingType.LIVRE_EDITION'
    const cinemaCardType = selectedOfferType.value == 'ThingType.CINEMA_CARD'
    const refundableOffers = !bookType && !cinemaCardType

    const offersAvailableOnlineAndOffline =
      !selectedOfferType.onlineOnly && !selectedOfferType.offlineOnly

    const onlineOnlyOffers = selectedOfferType.onlineOnly

    return (offersAvailableOnlineAndOffline && refundableOffers) || onlineOnlyOffers
  }
  return false
}

export default displayDigitalOfferInformationMessage

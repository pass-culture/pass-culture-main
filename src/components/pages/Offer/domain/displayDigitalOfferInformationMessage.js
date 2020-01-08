const displayDigitalOfferInformationMessage = (selectedOfferType, venue) => {
  if (selectedOfferType && venue && venue.isVirtual) {
    const bookType = selectedOfferType.value == 'ThingType.LIVRE_EDITION'
    const offersAvailableOnlineAndOffline =
      !selectedOfferType.onlineOnly && !selectedOfferType.offlineOnly && !bookType
    const onlineOnlyOffers = selectedOfferType.onlineOnly

    return offersAvailableOnlineAndOffline || onlineOnlyOffers
  }
  return false
}

export default displayDigitalOfferInformationMessage

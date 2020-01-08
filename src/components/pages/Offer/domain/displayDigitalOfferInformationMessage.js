const displayDigitalOfferInformationMessage = selectedOfferType => {
  if (selectedOfferType) {
    return selectedOfferType.onlineOnly
  }
  return false
}

export default displayDigitalOfferInformationMessage

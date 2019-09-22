const buildOfferAltPictoByOfferType = offerType => {
  if (!offerType) {
    return null
  }
  const offerCategory = offerType.split('.')[1]
  const offerCategoryAsLowerCase = offerCategory.toLowerCase()

  return offerCategoryAsLowerCase.replace(/_/g, ' ')
}

export default buildOfferAltPictoByOfferType

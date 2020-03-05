const isOfferBookableForUser = (offer, mediation, booking) => {
  if (!offer) {
    return false
  }
  const isTutorialCard = mediation && typeof mediation.tutoIndex !== 'undefined'
  if (isTutorialCard) {
    return false
  }
  const { isUsed } = booking || {}
  if (isUsed) {
    return false
  }
  return !offer.isBookable
}

export default isOfferBookableForUser

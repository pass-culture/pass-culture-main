const getIsNotBookable = (offer, mediation, booking) => {
  if (!offer) {
    return false
  }
  if (mediation && typeof mediation.tutoIndex !== 'undefined') {
    return false
  }
  const { isUsed } = booking || {}
  if (isUsed) {
    return false
  }
  return offer.isNotBookable
}

export default getIsNotBookable

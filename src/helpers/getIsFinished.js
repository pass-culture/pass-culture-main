const getIsFinished = (offer, mediation, booking) => {
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
  return offer.isFinished
}

export default getIsFinished

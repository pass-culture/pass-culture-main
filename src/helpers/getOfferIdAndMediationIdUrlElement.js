const getOfferIdAndMediationIdUrlElement = currentRecommendation => {
  const { mediationId, offerId } = currentRecommendation
  return `${offerId}/${mediationId || 'vide'}`
}

export default getOfferIdAndMediationIdUrlElement

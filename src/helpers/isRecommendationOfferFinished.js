export const NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD = 5

export const isRecommendationOfferFinished = (
  recommendation,
  offerId = null
) => {
  if (!recommendation) return false

  const { offer } = recommendation
  if (offerId != null && offerId !== 'tuto') {
    return offer.isFinished
  }
  return false
}

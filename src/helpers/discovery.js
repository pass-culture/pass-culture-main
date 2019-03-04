import filterAvailableStocks from './filterAvailableStocks'

export const NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD = 5

export const isRecommendations = (recommendations, previousProps) =>
  !recommendations || !previousProps.recommendations

export const isCurrentRecommendation = (currentRecommendation, previousProps) =>
  !currentRecommendation || !previousProps.currentRecommendation

export const isNewRecommendations = (recommendations, previousProps) =>
  recommendations === previousProps.recommendations

export const isNewCurrentRecommendation = (
  currentRecommendation,
  previousProps
) => currentRecommendation.index === previousProps.currentRecommendation.index

export const isSameReco = (currentRecommendation, prevProps) =>
  !currentRecommendation ||
  (prevProps &&
    prevProps.currentRecommendation &&
    currentRecommendation &&
    prevProps.currentRecommendation.id === currentRecommendation.id)

export const isRecommendationFinished = (recommendation, offerId = false) => {
  if (!recommendation) return false
  const { offer } = recommendation
  const stocks = (offer && offer.stocks) || []
  const availableStocks = filterAvailableStocks(stocks)
  const isFinished =
    offerId &&
    offerId !== 'tuto' &&
    !(availableStocks && availableStocks.length > 0)
  return isFinished
}

export default isRecommendationFinished

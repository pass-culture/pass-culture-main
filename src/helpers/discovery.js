import filterAvailableStocks from './filterAvailableStocks'

export const PREVIOUS_NEXT_LIMIT = 2

//   const recommendations = recommendationsSelector(state)
export const withRecommandations = (recommendations, previousProps) =>
  !recommendations ||
  recommendations === previousProps.recommendations ||
  !previousProps.recommendations

//   const currentRecommendation = currentRecommendationSelector(tate, offerId, mediationId)
export const withCurrentRecommandation = (
  currentRecommendation,
  previousProps
) =>
  !currentRecommendation ||
  !previousProps.currentRecommendation ||
  currentRecommendation.index === previousProps.currentRecommendation.index

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

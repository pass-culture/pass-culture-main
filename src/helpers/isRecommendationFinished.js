import { filterAvailableDates } from './filterAvailableDates'

export const isRecommendationFinished = (recommendation, offerId) => {
  // if (!recommendation) return false
  const { offer } = recommendation
  const stocks = (offer && offer.stocks) || []
  const availableDates = filterAvailableDates(stocks)
  const isFinished =
    offerId !== 'tuto' && !(availableDates && availableDates.length > 0)
  return isFinished
}

export default isRecommendationFinished

import { filterAvailableStocks } from './filterAvailableStocks'

export const isRecommendationFinished = (recommendation, offerId) => {
  // if (!recommendation) return false
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

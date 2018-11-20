import filterAvailableStocks from './filterAvailableStocks'

const isRecommendationFinished = (recommendation, offerId = false) => {
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

import { compose } from 'redux'
import selectCurrentRecommendation from './currentRecommendation'

const getRecommendationOfferName = recommendation => {
  const { offer: { name = '' } = {} } = recommendation || {}
  return name
}

export const getCurrentRecommendationOfferName = compose(
  getRecommendationOfferName,
  selectCurrentRecommendation
)

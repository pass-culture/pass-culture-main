import get from 'lodash.get'
import { compose } from 'redux'
import selectCurrentRecommendation from './currentRecommendation'

const getRecommendationOfferName = recommendation => get(recommendation, 'offer.name')

export const getCurrentRecommendationOfferName = compose(
  getRecommendationOfferName,
  selectCurrentRecommendation
)

import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'
import getOffer from '../getters/offer'

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  selectCurrentRecommendation,
  (pathname, recommendation) => {
    const [, , offerId] = pathname.split('/')
    return getOffer(recommendation, offerId)
  }
)

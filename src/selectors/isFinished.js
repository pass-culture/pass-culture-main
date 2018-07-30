import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'

export default createSelector(selectCurrentRecommendation, function(
  recommendation
) {
  const offers = get(recommendation, 'recommendationOffers', [])
  const now = moment()
  return offers.every(o => moment(o.bookingLimitDatetime).isBefore(now)) // FIXME: also check that nbooking < available
})

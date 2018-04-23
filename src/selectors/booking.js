import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'

export default createSelector(
  state => state.data.bookings,
  selectCurrentRecommendation,
  (bookings, recommendation) => {
    return []
      .concat(bookings)
      .find(b => get(b, 'recommendationId') === get(recommendation, 'id'))
  }
)

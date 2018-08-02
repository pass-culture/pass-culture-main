import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'

export default createSelector(
  state => state.data.bookings,
  currentRecommendationSelector,
  (bookings, currentRecommendation) =>
    bookings.find(
      b => get(b, 'recommendationId') === get(currentRecommendation, 'id')
    )
)

import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'

const selectBooking = createSelector(
  state => state.data.bookings,
  currentRecommendationSelector,
  (bookings, currentRecommendation) =>
    bookings.find(
      b => get(b, 'recommendationId') === get(currentRecommendation, 'id')
    )
)

export default selectBooking

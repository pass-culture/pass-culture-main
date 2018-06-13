import { createSelector } from 'reselect'

import selectCurrentVenues from './currentVenues'

export default createSelector(
  selectCurrentVenues,
  venues => venues &&
      venues.length === 1 &&
      venues[0]
)

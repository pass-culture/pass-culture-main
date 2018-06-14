import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedVenues from './currentVenues'

export default createSelector(
  selectSelectedVenues,
  venues => get(venues, '0')
)

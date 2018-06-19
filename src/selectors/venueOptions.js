import { createSelector } from 'reselect'

import selectSelectedVenues from './selectedVenues'

export default createSelector(
  selectSelectedVenues,
  venues => venues && venues.map(v =>
      ({ label: v.name, value: v.id }))
)

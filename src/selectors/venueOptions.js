import { createSelector } from 'reselect'

import { selectVenues } from './venues'

export default createSelector(
  selectVenues,
  venues => venues && venues.map(v =>
      ({ label: v.name, value: v.id }))
)

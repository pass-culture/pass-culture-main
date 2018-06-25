import { createSelector } from 'reselect'

import createVenueSelector from './venues'

export default createSelector(
  createVenueSelector(),
  venues => venues && venues.map(v =>
      ({ label: v.name, value: v.id }))
)

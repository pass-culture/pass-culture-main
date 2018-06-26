import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.venueProviders,
  (state, venueId) => venueId,
  (venueProviders, venueId) => venueProviders &&
    venueProviders.filter(vp => vp.venueId === venueId)
)

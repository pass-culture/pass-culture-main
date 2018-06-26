import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.venueProviders,
  (state, ownProps) => ownProps.match.params.venueId,
  (venueProviders, venueId) => venueProviders &&
    venueProviders.filter(vp => vp.venueId === venueId)
)

import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.venues,
  (state, ownProps) => ownProps.match.params.venueId,
  (venues, venueId) => {
    return venues && venues.find(v => v.id === venueId)
  }
)

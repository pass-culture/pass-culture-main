import { createSelector } from 'reselect'

import selectCurrentOfferer from './currentOfferer'

export default createSelector(
  selectCurrentOfferer,
  (state, ownProps) => ownProps.match.params.venueId,
  (currentOfferer, venueId) => {
    if (currentOfferer) {
      console.log('------- currentOfferer.managedVenues ------- ', currentOfferer.managedVenues)
      return currentOfferer && currentOfferer.managedVenues
.find(o => o.id === venueId)
    }
  }
)

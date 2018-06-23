import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'
import selectVenue from './venue'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'match.params.offererId'),
  selectVenue,
  (offerers, offererId, venue) => offerers &&
    offerers.find(offerer =>
      offerer.id === (offererId || get(venue, 'managingOffererId')))
)

import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'
import createSelectVenue from './venue'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'match.params.offererId'),
  createSelectVenue(),
  (offerers, offererId, venue) => offerers &&
    offerers.find(offerer =>
      offerer.id === (offererId || get(venue, 'managingOffererId')))
)

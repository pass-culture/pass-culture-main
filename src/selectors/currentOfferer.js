import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'
import selectCurrentVenue from './currentVenue'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'match.params.offererId'),
  selectCurrentVenue,
  (offerers, offererId, currentVenue) => offerers &&
    offerers.find(offerer =>
      offerer.id === (offererId || get(currentVenue, 'managingOffererId')))      
)

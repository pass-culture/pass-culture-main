import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'currentOccasion.offererId'),
  (offerers, currentOffererId) =>
    currentOffererId || get(offerers, '0.id')
)

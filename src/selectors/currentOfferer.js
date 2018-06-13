import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  (state, ownProps) => ownProps.match.params.offererId,
  (offerers, offererId) => offererId &&
      offerers &&
      offerers.find(o => o.id === offererId)
)

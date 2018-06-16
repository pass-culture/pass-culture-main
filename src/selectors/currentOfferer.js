import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'match.params.offererId'),
  (offerers, offererId) => offererId &&
      offerers &&
      offerers.find(offerer => offerer.id === offererId)
)

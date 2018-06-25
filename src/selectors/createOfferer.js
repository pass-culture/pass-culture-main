import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default () => createSelector(
  selectOfferers,
  (state, offererId) => offererId,
  (offerers, offererId) => {
    return offerers.find(offerer => offerer.id === offererId)
  }
)

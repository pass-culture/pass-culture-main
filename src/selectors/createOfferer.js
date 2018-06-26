import { createSelector } from 'reselect'

import offerersSelector from './createOfferers'

export default () => createSelector(
  offerersSelector(),
  (state, offererId) => offererId,
  (offerers, offererId) => {
    return offerers.find(offerer => offerer.id === offererId)
  }
)

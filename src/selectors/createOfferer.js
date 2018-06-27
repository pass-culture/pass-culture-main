import { createSelector } from 'reselect'

import createOfferersSelector from './createOfferers'

export default (offerersSelector=createOfferersSelector()) => createSelector(
  offerersSelector,
  (state, offererId) => offererId,
  (offerers, offererId) => {
    return offerers.find(offerer => offerer.id === offererId)
  }
)

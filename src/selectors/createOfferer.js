import { createSelector } from 'reselect'

export default offerersSelector => createSelector(
  offerersSelector,
  (state, offererId) => offererId,
  (offerers, offererId) => {
    return offerers.find(offerer => offerer.id === offererId)
  }
)

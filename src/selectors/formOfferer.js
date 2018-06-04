import { createSelector } from 'reselect'

import { getFormValue } from '../reducers/form'

export default createSelector(
  state => state.user && state.user.offerers,
  (state, ownProps) => getFormValue(state, {
    collectionName: ownProps.occasionCollection,
    entityId: ownProps.occasionId,
    name: 'offererId'
  }),
  (offerers, offererId) =>
    offerers && offererId && offerers.find(o => o.id === offererId)
)

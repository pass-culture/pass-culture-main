import { createSelector } from 'reselect'

export const getPendingOfferers = createSelector(
  state => state.data.pendingOfferers,
  offerers => offerers
)

export default createSelector(
  state => state.data.offerers,
  offerers => offerers
)

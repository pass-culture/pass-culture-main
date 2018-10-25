import { createSelector } from 'reselect'

export const getPendingOfferers = createSelector(
  state => state.data.pendingOfferer,
  offerers => offerers || []
)
export default createSelector(
  state => state.data.offerers,
  offerers => offerers
)

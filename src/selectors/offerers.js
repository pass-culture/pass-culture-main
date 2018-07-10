import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.offerers,
  offerers => offerers
)

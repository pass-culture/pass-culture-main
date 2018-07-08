import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.searchedOfferers || state.data.offerers,
  offerers => offerers
)

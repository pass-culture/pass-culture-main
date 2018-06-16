import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.offerers,
  state => state.data.searchedOfferers,
  (offerers, searchedOfferers) =>
    searchedOfferers || offerers
)

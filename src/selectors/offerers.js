import get from 'lodash.get'
import { createSelector } from 'reselect'

export default createSelector(
  state => get(state, 'data.offerers'),
  state => state.data.searchedOfferers,
  (offerers, searchedOfferers) =>
    searchedOfferers || offerers
)

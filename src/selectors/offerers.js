import get from 'lodash.get'
import { createSelector } from 'reselect'

export default createSelector(
  state => get(state, 'user.offerers'),
  state => state.data.offerers,
  (userOfferers, searchOfferers) =>
    searchOfferers || userOfferers
)

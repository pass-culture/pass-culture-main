import { createSelector } from 'reselect'
import get from 'lodash.get'

export default () => createSelector(
  state => state.data.searchedOfferers || state.data.offerers,
  offerers => offerers
)

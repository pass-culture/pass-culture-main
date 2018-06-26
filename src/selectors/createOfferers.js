import { createSelector } from 'reselect'
import get from 'lodash.get'

export default () => createSelector(
  state => get(state, 'data.searchedOfferers', get(state, 'data.offerers', [])),
  offerers => offerers
)

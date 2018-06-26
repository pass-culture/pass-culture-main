import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.things,
  (state, params) => params,
  (things, thingId) => things.find(thing => thing.id === thingId)
)

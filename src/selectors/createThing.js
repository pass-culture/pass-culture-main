import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.things,
  (state, thingId) => thingId,
  (things, thingId) => things.find(thing => thing.id === thingId)
)

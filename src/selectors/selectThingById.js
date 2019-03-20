import createCachedSelector from 're-reselect'

function mapArgsToKey(state, thingId) {
  return thingId || ''
}

export const selectThingById = createCachedSelector(
  state => state.data.things,
  (state, thingId) => thingId,
  (things, thingId) => things.find(thing => thing.id === thingId)
)(mapArgsToKey)

export default selectThingById

import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, thingId) {
  return thingId || ''
}

export const selectThingById = createCachedSelector(
  state => state.data.things,
  (state, thingId) => thingId,
  (things, thingId) => things.find(thing => thing.id === thingId)
)(mapArgsToCacheKey)

export default selectThingById

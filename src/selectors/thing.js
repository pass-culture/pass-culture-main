import createCachedSelector from 're-reselect';

export default createCachedSelector(
  state => state.data.things,
  (state, thingId) => thingId,
  (things, thingId) => things.find(thing => thing.id === thingId)
)(
  (state, thingId) => thingId || ''
)

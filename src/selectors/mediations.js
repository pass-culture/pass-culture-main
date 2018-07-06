import createCachedSelector from 're-reselect';

export default createCachedSelector(
  state => state.data.mediations,
  (state, eventId, thingId) => eventId,
  (state, eventId, thingId) => thingId,
  (mediations, eventId, thingId) => {
    if (eventId)
      mediations = mediations.filter(m => m.eventId === eventId)

    if (thingId)
      mediations = mediations.filter(m => m.thingId === thingId)

    return mediations
  },
  (state, eventId, thingId) => `${eventId}/${thingId}`
)

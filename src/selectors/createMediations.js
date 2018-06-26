import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.mediations,
  (_, eventId) => eventId,
  (_, __, thingId) => thingId,
  (mediations, eventId, thingId) => {
    if (eventId)
      mediations = mediations.filter(m => m.eventId === eventId)

    if (thingId)
      mediations = mediations.filter(m => m.thingId === thingId)

    return mediations
  }
)

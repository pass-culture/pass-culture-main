import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.mediations,
  (state, optionalEventId, optionalThingId) => optionalEventId,
  (state, optionalEventId, optionalThingId) => optionalThingId,
  (mediations, optionalEventId, optionalThingId) => {

    let selectedMediations = mediations
    if (optionalEventId)
      selectedMediations = mediations.filter(m => m.eventId === optionalEventId)

    if (optionalThingId)
      selectedMediations = mediations.filter(m => m.thingId === optionalThingId)

    selectedMediations && selectedMediations.sort((m1, m2) =>
      moment(m1.dateCreated) - moment(m2.dateCreated))

    return selectedMediations
  }
)(
  (state, optionalEventId, optionalThingId) => `${optionalEventId || ''}/${optionalThingId || ''}`
)

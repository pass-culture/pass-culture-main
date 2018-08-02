import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.eventOccurrences,
  (state, venueId) => venueId,
  (state, venueId, eventId) => eventId,
  (eventOccurrences, venueId, eventId) => {
    if (venueId)
      eventOccurrences = eventOccurrences.filter(o => o.venueId === venueId)
    if (eventId)
      eventOccurrences = eventOccurrences.filter(o => o.eventId === eventId)

    return eventOccurrences.sort(
      (o1, o2) =>
        moment(o2.beginningDatetime).unix() -
        moment(o1.beginningDatetime).unix()
    )
  }
)((state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`)

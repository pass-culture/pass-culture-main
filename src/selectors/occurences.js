import moment from 'moment'
import createCachedSelector from 're-reselect'
import {resolveDataCollection} from '../utils/resolvers'

export default createCachedSelector(
  state => state.data.eventOccurences,
  (state, venueId) => venueId,
  (state, venueId, eventId) => eventId,
  (eventOccurences, venueId, eventId) => {
    eventOccurences = resolveDataCollection(eventOccurences, 'eventOccurences')
    if (venueId)
      eventOccurences = eventOccurences.filter(o => o.venueId === venueId)
    if (eventId)
      eventOccurences = eventOccurences.filter(o => o.eventId === eventId)

    return eventOccurences
      .sort((o1,o2) => moment(o2.beginningDatetime).unix() - moment(o1.beginningDatetime).unix())
  }
)(
  (state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`
)


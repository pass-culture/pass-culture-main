import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, occurrence) => occurrence,
  (state, occurrence, eventId) => eventId,
  (state, occurrence, eventId, venueId) => venueId,
  (occurrence, eventId, venueId) => {
    return Object.assign({}, occurrence, {
      beginningDatetime: moment(
        get(occurrence, 'beginningDatetime')
      ).toISOString(),
      endDatetime: moment(get(occurrence, 'endDatetime')).toISOString(),
      eventId,
      venueId,
    })
  }
)((state, occurrence) => get(occurrence, 'id') || '')

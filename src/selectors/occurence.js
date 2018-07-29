import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, occurence) => occurence,
  (state, occurence, eventId) => eventId,
  (state, occurence, eventId, venueId) => venueId,
  (occurence, eventId, venueId) => {
    return Object.assign({}, occurence, {
      beginningDatetime: moment(
        get(occurence, 'beginningDatetime')
      ).toISOString(),
      endDatetime: moment(get(occurence, 'endDatetime')).toISOString(),
      eventId,
      venueId,
    })
  }
)((state, occurence) => get(occurence, 'id') || '')

import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, eventOccurrence) => eventOccurrence,
  (state, eventOccurrence, offerId) => offerId,
  (state, eventOccurrence, offerId, venueId) => venueId,
  (eventOccurrence, offerId, venueId) => {
    return Object.assign({}, eventOccurrence, {
      beginningDatetime: moment(
        get(eventOccurrence, 'beginningDatetime')
      ).toISOString(),
      endDatetime: moment(get(eventOccurrence, 'endDatetime')).toISOString(),
      offerId,
      venueId,
    })
  }
)((state, eventOccurrence) => get(eventOccurrence, 'id') || '')

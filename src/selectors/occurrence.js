import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, occurrence) => occurrence,
  (state, occurrence, offerId) => offerId,
  (state, occurrence, offerId, venueId) => venueId,
  (occurrence, offerId, venueId) => {
    return Object.assign({}, occurrence, {
      beginningDatetime: moment(
        get(occurrence, 'beginningDatetime')
      ).toISOString(),
      endDatetime: moment(get(occurrence, 'endDatetime')).toISOString(),
      offerId,
      venueId,
    })
  }
)((state, occurrence) => get(occurrence, 'id') || '')

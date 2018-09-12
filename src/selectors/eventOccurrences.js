import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.eventOccurrences,
  (state, offerId) => offerId,
  (eventOccurrences, offerId) => {
    if (offerId)
      eventOccurrences = eventOccurrences.filter(o => o.offerId === offerId)

    return eventOccurrences.sort(
      (o1, o2) =>
        moment(o2.beginningDatetime).unix() -
        moment(o1.beginningDatetime).unix()
    )
  }
)((state, offerId) => offerId || '')

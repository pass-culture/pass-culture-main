import get from 'lodash.get';
import { createSelector } from 'reselect'
import selectBookingsWithSource from './bookingsWithSource'
import { getThumbUrl } from './thumbUrl'


export default createSelector(
  selectBookingsWithSource,
  (bookings=[]) => bookings.map(b => Object.assign(b, {
    thumbUrl: getThumbUrl(b.mediation, b.source, b.offer),
  }))
)

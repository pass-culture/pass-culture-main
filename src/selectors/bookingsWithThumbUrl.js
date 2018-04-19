import { createSelector } from 'reselect'

import selectBookingsWithSource from './bookingsWithSource'
import getMediation from '../getters/mediation'
import getThumbUrl from '../getters/thumbUrl'

export default createSelector(selectBookingsWithSource, (bookings = []) =>
  bookings.map(b =>
    Object.assign(
      {
        thumbUrl: getThumbUrl(getMediation(b.userMediation), b.source, b.offer),
      },
      b
    )
  )
)

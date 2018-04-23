import { createSelector } from 'reselect'

import getMediation from '../getters/mediation'
import getSource from '../getters/source'

export default createSelector(
  state => state.data.bookings,
  (bookings = []) =>
    bookings.map(b =>
      Object.assign(
        {
          source: getSource(getMediation(b.recommendation), b.offer),
        },
        b
      )
    )
)

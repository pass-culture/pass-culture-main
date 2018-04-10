import { createSelector } from 'reselect'

import { getMediation } from './mediation'
import { getSource } from './source'


export default createSelector(
  state => state.data.bookings,
  (bookings=[]) => bookings.map(b => Object.assign({
      source: getSource(getMediation(b.userMediation), b.offer),
    }, b))
)

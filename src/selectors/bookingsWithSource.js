import { createSelector } from 'reselect'
import { getSource } from './source'


export default createSelector(
  state => state.data.bookings,
  (bookings=[]) => bookings.map(b => Object.assign({
    source: getSource(b.mediation, b.offer),
  }, b))
)

import get from 'lodash.get';
import { createSelector } from 'reselect'
import { getSource } from './source'


export default createSelector(
  state => state.data.bookings,
  (bookings=[]) => bookings.map(b => Object.assign(b, {
    source: getSource(b.mediation, b.offer),
  }))
)

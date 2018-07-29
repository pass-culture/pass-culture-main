import createCachedSelector from 're-reselect'

import venuesSelector from './venues'

export default createCachedSelector(
  state => state.data.occasions,
  (state, offererId, venueId) => offererId && venuesSelector(state, offererId),
  (state, offererId, venueId) => venueId,
  (occasions, venues, venueId) => {
    const venueIds = [].concat(venueId || (venues || []).map(v => v.id))

    return occasions.filter(
      o => (venueIds.length ? venueIds.includes(o.venueId) : true)
    )
  }
)((state, offererId, venueId) => `${offererId || ''}/${venueId || ''}`)

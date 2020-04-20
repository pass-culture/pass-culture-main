import get from 'lodash.get'

export const selectVenueTypes = state => get(state, 'data.venue-types', [])

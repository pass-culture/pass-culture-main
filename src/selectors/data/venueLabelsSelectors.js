import get from 'lodash.get'

export const selectVenueLabels = state => {
  const sorted_by_label = (a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0)

  const venue_types = get(state, 'data.venue-labels', [])

  if (venue_types.length === 0) return []

  venue_types.sort(sorted_by_label)

  return venue_types
}

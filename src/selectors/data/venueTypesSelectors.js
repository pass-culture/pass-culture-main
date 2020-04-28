import get from 'lodash.get'

export const selectVenueTypes = state => {
  const sorted_by_label = (a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0)

  const venue_types = get(state, 'data.venue-types', [])

  if (venue_types.length === 0) return []

  const venue_type_index_of_autre = venue_types.findIndex(
    venue_types => venue_types.label === 'Autre'
  )

  const autre = venue_types.slice(venue_type_index_of_autre, venue_type_index_of_autre + 1).pop()

  const venue_type_without_autre = venue_types.filter(venue_types => venue_types.label !== 'Autre')

  venue_type_without_autre.sort(sorted_by_label).push(autre)

  return venue_type_without_autre
}

const sorted_alphabetically_by_label = (a, b) => {
  return a.label < b.label ? -1 : a.label > b.label ? 1 : 0
}

export const selectVenueTypes = state => {
  const { 'venue-types': venue_types = [] } = state.data

  if (venue_types.length === 0) return []

  const venue_type_index_of_autre = venue_types.findIndex(
    venue_types => venue_types.label === 'Autre'
  )

  const autre = venue_types.slice(venue_type_index_of_autre, venue_type_index_of_autre + 1).pop()

  const venue_type_without_autre = venue_types.filter(venue_types => venue_types.label !== 'Autre')

  venue_type_without_autre.sort(sorted_alphabetically_by_label).push(autre)

  return venue_type_without_autre
}

const sorted_alphabetically_by_label = (a, b) => {
  return a.label < b.label ? -1 : a.label > b.label ? 1 : 0
}

export const selectVenueLabels = state => {
  const { 'venue-labels': venue_labels = [] } = state.data

  if (venue_labels.length === 0) return []

  venue_labels.sort(sorted_alphabetically_by_label)

  return venue_labels
}

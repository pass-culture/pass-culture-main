import * as pcapi from 'repository/pcapi/pcapi'

export const fetchAllVenuesByProUser = offererId => {
  return pcapi.getVenuesForOfferer({ offererId }).catch(() => [])
}

export const computeVenueDisplayName = venue => {
  if (venue.isVirtual) {
    return `${venue.offererName} - Offre numérique`
  } else {
    return venue.publicName || venue.name
  }
}

export const formatAndOrderVenues = venues => {
  const sortAlphabeticallyByDisplayName = (a, b) => {
    let aDisplayName = a.displayName.toLowerCase()
    let bDisplayName = b.displayName.toLowerCase()
    return aDisplayName < bDisplayName
      ? -1
      : aDisplayName > bDisplayName
      ? 1
      : 0
  }

  return venues
    .map(venue => {
      const displayName = computeVenueDisplayName(venue)
      return { id: venue.id, displayName }
    })
    .sort(sortAlphabeticallyByDisplayName)
}

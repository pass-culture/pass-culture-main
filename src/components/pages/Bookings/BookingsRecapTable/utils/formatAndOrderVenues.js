const formatAndOrderVenues = venues => {
  const sortAlphabeticallyByDisplayName = (a, b) => {
    let aDisplayName = a.displayName.toLowerCase()
    let bDisplayName = b.displayName.toLowerCase()
    return aDisplayName < bDisplayName ? -1 : aDisplayName > bDisplayName ? 1 : 0
  }

  return venues
    .map(venue => {
      const displayName = venue.isVirtual ? `${venue.offererName} - Offre numérique` : venue.name
      return { id: venue.id, displayName }
    })
    .sort(sortAlphabeticallyByDisplayName)
}

export default formatAndOrderVenues

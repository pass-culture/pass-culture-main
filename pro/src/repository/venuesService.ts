import { VenueListItemResponseModel } from 'apiClient/v1'
import { Venue } from 'core/Offers/types'

type VenueItem = {
  id: string
  displayName: string
}

export const computeVenueDisplayName = (
  venue: VenueListItemResponseModel | Venue
): string => {
  if (venue.isVirtual) {
    return `${venue.offererName} - Offre numérique`
  } else {
    return venue.publicName || venue.name
  }
}

export const formatAndOrderVenues = (venues: VenueListItemResponseModel[]) => {
  const sortAlphabeticallyByDisplayName = (a: VenueItem, b: VenueItem) => {
    const aDisplayName = a.displayName.toLowerCase()
    const bDisplayName = b.displayName.toLowerCase()

    return aDisplayName < bDisplayName
      ? -1
      : aDisplayName > bDisplayName
      ? 1
      : 0
  }

  return venues
    .map(venue => {
      const displayName = computeVenueDisplayName(venue)
      return { id: venue.nonHumanizedId.toString(), displayName }
    })
    .sort(sortAlphabeticallyByDisplayName)
}

import { VenueListItemResponseModel } from 'apiClient/v1'
import { Venue } from 'core/Offers/types'
import { SelectOption } from 'custom_types/form'

export const computeVenueDisplayName = (
  venue: VenueListItemResponseModel | Venue
): string => {
  if (venue.isVirtual) {
    return `${venue.offererName} - Offre numérique`
  } else {
    return venue.publicName || venue.name
  }
}

const sortAlphabeticallyByLabel = (a: SelectOption, b: SelectOption) => {
  const aLabel = a.label.toLowerCase()
  const bLabel = b.label.toLowerCase()

  return aLabel < bLabel ? -1 : aLabel > bLabel ? 1 : 0
}

export const formatAndOrderVenues = (venues: VenueListItemResponseModel[]) =>
  venues
    .map(venue => ({
      value: venue.nonHumanizedId.toString(),
      label: computeVenueDisplayName(venue),
    }))
    .sort(sortAlphabeticallyByLabel)

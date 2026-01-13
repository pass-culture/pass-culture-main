import type { OfferVenueResponse } from '@/apiClient/adage'

export const getOfferVenueAndOffererName = (
  offerVenue: OfferVenueResponse
): string => {
  const venueName = offerVenue.publicName

  const offererName = offerVenue.managingOfferer.name

  if (venueName.toLowerCase() === offererName.toLowerCase()) {
    return venueName
  }

  return `${venueName} - ${offererName} (${offerVenue.postalCode})`
}

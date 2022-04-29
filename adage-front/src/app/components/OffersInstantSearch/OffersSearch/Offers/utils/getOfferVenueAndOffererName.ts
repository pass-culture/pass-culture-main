import { VenueType } from 'app/types/offers'

const formatToReadableString = (input: string): string => {
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}

export const getOfferVenueAndOffererName = (offerVenue: VenueType): string => {
  const venueName =
    offerVenue.publicName || formatToReadableString(offerVenue.name)

  const offererName = offerVenue.managingOfferer.name

  if (venueName.toLowerCase() === offererName.toLowerCase()) {
    return venueName
  }

  return `${venueName} - ${offererName}`
}

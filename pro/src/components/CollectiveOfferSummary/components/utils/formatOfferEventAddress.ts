import { OfferVenueModel, OfferAddressType } from 'apiClient/v1'
import { Venue } from 'core/Venue/types'
import { EVENT_ADDRESS_SCHOOL_LABEL } from 'screens/OfferEducational/constants/labels'

export const formatOfferEventAddress = (
  eventAddress: OfferVenueModel,
  venue: Venue
): string => {
  if (eventAddress.addressType === OfferAddressType.SCHOOL) {
    return EVENT_ADDRESS_SCHOOL_LABEL
  }

  if (
    eventAddress.addressType === OfferAddressType.OTHER &&
    eventAddress.otherAddress
  ) {
    return eventAddress.otherAddress
  }

  return [
    venue.publicName || venue.name,
    venue.address,
    venue.postalCode,
    venue.city,
  ].join(', ')
}

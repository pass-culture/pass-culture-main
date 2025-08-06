import {
  CollectiveOfferOfferVenueResponseModel,
  GetOffererVenueResponseModel,
  GetVenueResponseModel,
  OfferAddressType,
} from '@/apiClient/v1'
import { EVENT_ADDRESS_SCHOOL_LABEL } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/constants/labels'

export const formatOfferEventAddress = (
  eventAddress: CollectiveOfferOfferVenueResponseModel,
  venue: GetVenueResponseModel,
  manadgedVenues: GetOffererVenueResponseModel[]
): string => {
  if (eventAddress.addressType === OfferAddressType.SCHOOL) {
    return EVENT_ADDRESS_SCHOOL_LABEL
  }

  if (eventAddress.addressType === OfferAddressType.OTHER) {
    return eventAddress.otherAddress
  }

  const offererAddressVenue = manadgedVenues.find(
    (venue) => venue.id === eventAddress.venueId
  )

  const displayedVenue = offererAddressVenue || venue

  return [
    displayedVenue.publicName || displayedVenue.name,
    displayedVenue.street,
    displayedVenue.postalCode,
    displayedVenue.city,
  ].join(', ')
}

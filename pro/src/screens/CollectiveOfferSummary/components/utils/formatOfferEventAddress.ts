import {
  CollectiveOfferOfferVenueResponseModel,
  GetCollectiveOfferVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { EVENT_ADDRESS_SCHOOL_LABEL } from 'screens/OfferEducational/constants/labels'

export const formatOfferEventAddress = (
  eventAddress: CollectiveOfferOfferVenueResponseModel,
  venue: GetCollectiveOfferVenueResponseModel
): string => {
  if (eventAddress.addressType === OfferAddressType.SCHOOL) {
    return EVENT_ADDRESS_SCHOOL_LABEL
  }

  if (eventAddress.addressType === OfferAddressType.OTHER) {
    return eventAddress.otherAddress
  }

  return [venue.name, venue.address, venue.postalCode, venue.city].join(', ')
}

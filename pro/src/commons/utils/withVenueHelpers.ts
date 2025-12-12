import type {
  GetVenueResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'

export const withVenueHelpers = <
  T extends GetVenueResponseModel | VenueListItemResponseModel,
>(
  venue: T
) => ({
  ...venue,

  get fullAddressAsString() {
    if (!venue.address) {
      return null
    }

    const street = venue.address.street ? `${venue.address.street}, ` : ''

    return `${street}${venue.address.postalCode} ${venue.address.city}`
  },
})

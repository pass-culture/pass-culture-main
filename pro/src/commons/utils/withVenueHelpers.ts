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
    if (!venue.location) {
      return null
    }

    const street = venue.location.street ? `${venue.location.street}, ` : ''

    return `${street}${venue.location.postalCode} ${venue.location.city}`
  },
})

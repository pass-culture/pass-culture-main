import type {
  GetVenueResponseModel,
  VenueListItemLiteResponseModel,
} from '@/apiClient/v1'

export const withVenueHelpers = <
  T extends GetVenueResponseModel | VenueListItemLiteResponseModel,
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

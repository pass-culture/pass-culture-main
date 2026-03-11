import type {
  GetVenueResponseModel,
  VenueListItemLiteResponseModel,
} from '@/apiClient/v1'

export function withVenueHelpers(
  venue: GetVenueResponseModel
): GetVenueResponseModel & {
  fullAddressAsString: string | null
}
export function withVenueHelpers(
  venue: VenueListItemLiteResponseModel
): VenueListItemLiteResponseModel & {
  fullAddressAsString: string
}
export function withVenueHelpers(
  venue: GetVenueResponseModel | VenueListItemLiteResponseModel
) {
  return {
    ...venue,

    get fullAddressAsString() {
      if (!venue.location) {
        return null
      }

      const street = venue.location.street ? `${venue.location.street}, ` : ''

      return `${street}${venue.location.postalCode} ${venue.location.city}`
    },
  }
}

import {
  type GetVenueResponseModel,
  type VenueListItemLiteResponseModel,
  VenueState,
} from '@/apiClient/v1'

export function withVenueHelpers(
  venue: GetVenueResponseModel
): GetVenueResponseModel & {
  isClosed: boolean
  fullAddressAsString: string | null
}
export function withVenueHelpers(
  venue: VenueListItemLiteResponseModel
): VenueListItemLiteResponseModel & {
  isClosed: boolean
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

    get isClosed() {
      return (
        venue.state === VenueState.CLOSING || venue.state === VenueState.CLOSED
      )
    },
  }
}

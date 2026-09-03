import {
  type GetOffererVenueResponseModel,
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
  venue: GetOffererVenueResponseModel
): GetOffererVenueResponseModel & {
  isClosed: boolean
}
export function withVenueHelpers(
  venue:
    | GetVenueResponseModel
    | VenueListItemLiteResponseModel
    | GetOffererVenueResponseModel
) {
  const isClosed =
    venue.state === VenueState.CLOSING || venue.state === VenueState.CLOSED

  if (!('location' in venue)) {
    return {
      ...venue,
      isClosed,
    }
  }

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
      return isClosed
    },
  }
}
